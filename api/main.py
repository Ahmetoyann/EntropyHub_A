from __future__ import annotations

import json
import logging
import math
import os
import threading
import time
import uuid
from collections import Counter

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from prometheus_client import CONTENT_TYPE_LATEST, Counter as PromCounter, Gauge, Histogram, generate_latest

from core.chaos.nihde import NIHDE, RUST_CORE_AVAILABLE
from core.pqc.kyber768 import Kyber768

 
DEFAULT_DEMO_API_KEY = "teknofest-local-dev-key"


def _load_api_keys() -> set[str]:
    configured = os.getenv("ENTROPYHUB_API_KEYS", "")
    keys = {item.strip() for item in configured.split(",") if item.strip()}
    if keys:
        return keys
    return {DEFAULT_DEMO_API_KEY}


def _public_paths() -> set[str]:
    return {"/", "/health", "/metrics", "/docs", "/openapi.json", "/redoc"}


def _mask_api_key(api_key: str | None) -> str:
    if not api_key:
        return "missing"
    if len(api_key) <= 8:
        return "***"
    return f"{api_key[:4]}...{api_key[-4:]}"


class FixedWindowRateLimiter:
    """Simple in-memory fixed-window limiter for demo environments."""

    def __init__(self, limit_per_minute: int = 120):
        self.limit_per_minute = max(1, int(limit_per_minute))
        self._lock = threading.Lock()
        self._store: dict[str, tuple[float, int]] = {}

    def allow(self, identity: str) -> tuple[bool, int]:
        now = time.time()
        with self._lock:
            window_start, count = self._store.get(identity, (now, 0))

            if now - window_start >= 60:
                window_start = now
                count = 0

            if count >= self.limit_per_minute:
                retry_after = max(1, int(60 - (now - window_start)))
                return False, retry_after

            self._store[identity] = (window_start, count + 1)
            return True, 0

    def reset(self):
        with self._lock:
            self._store.clear()


def _build_audit_logger() -> logging.Logger:
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("entropyhub.audit")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("logs/api_audit.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def _shannon_entropy(values: list[int]) -> float:
    if not values:
        return 0.0
    total = len(values)
    counts = Counter(values)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


class RandomBytesRequest(BaseModel):
    count: int = Field(default=32, ge=1, le=4096)


class RandomIntegersRequest(BaseModel):
    count: int = Field(default=16, ge=1, le=4096)
    min_val: int = Field(default=0)
    max_val: int = Field(default=255)

    @field_validator("max_val")
    @classmethod
    def validate_range(cls, value: int, info):
        min_val = info.data.get("min_val", 0)
        if value < min_val:
            raise ValueError("max_val must be greater than or equal to min_val")
        return value


class ReseedRequest(BaseModel):
    source: str = Field(default="api")


class KyberEncapsRequest(BaseModel):
    public_key_hex: str = Field(min_length=Kyber768.PUBLIC_KEY_SIZE * 2, max_length=Kyber768.PUBLIC_KEY_SIZE * 2)


class KyberDecapsRequest(BaseModel):
    secret_key_hex: str = Field(min_length=Kyber768.SECRET_KEY_SIZE * 2, max_length=Kyber768.SECRET_KEY_SIZE * 2)
    ciphertext_hex: str = Field(min_length=Kyber768.CIPHERTEXT_SIZE * 2, max_length=Kyber768.CIPHERTEXT_SIZE * 2)


class EntropyHubService:
    def __init__(self):
        self._lock = threading.Lock()
        self._engine = NIHDE(use_live_qrng=True, reseed_interval=256)

    def random_bytes(self, count: int) -> list[int]:
        with self._lock:
            return [self._engine.decide() for _ in range(count)]

    def random_integers(self, count: int, min_val: int, max_val: int) -> list[int]:
        if min_val == max_val:
            return [min_val] * count
        span = max_val - min_val + 1
        values = self.random_bytes(count)
        return [min_val + (value % span) for value in values]

    def reseed(self, source: str) -> dict:
        with self._lock:
            self._engine.reseed_manual(source=source)
            return self._engine.profile()

    def profile(self) -> dict:
        with self._lock:
            return self._engine.profile()


service = EntropyHubService()
audit_logger = _build_audit_logger()
configured_api_keys = _load_api_keys()
rate_limiter = FixedWindowRateLimiter(limit_per_minute=int(os.getenv("ENTROPYHUB_RATE_LIMIT_PER_MIN", "120")))

REQUEST_COUNT = PromCounter(
    "entropyhub_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "entropyhub_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)
AUTH_FAILURES = PromCounter(
    "entropyhub_auth_failures_total",
    "Total failed authentication attempts",
)
RATE_LIMIT_REJECTIONS = PromCounter(
    "entropyhub_rate_limit_rejections_total",
    "Total requests rejected by rate limiting",
)
ACTIVE_REQUESTS = Gauge(
    "entropyhub_active_requests",
    "Active in-flight HTTP requests",
)
GENERATED_BYTES = PromCounter(
    "entropyhub_generated_bytes_total",
    "Total number of random bytes generated by API endpoints",
)

app = FastAPI(
    title="EntropyHub API",
    version="2.2",
    summary="Teknofest-ready chaos RNG and ML-KEM service",
    description=(
        "EntropyHub exposes a Rust-accelerated Rossler chaos engine with "
        "Von Neumann post-processing, live entropy reseeding and ML-KEM-768 helpers."
    ),
)
app.state.rate_limiter = rate_limiter

# React Frontend entegrasyonu için CORS ayarları
# Bu ayar, tarayıcının localhost:3000'den localhost:8000'e istek atmasına izin verir.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme ortamı için tüm kaynaklara izin veriyoruz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_and_observability_middleware(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    path = request.url.path
    method = request.method
    client_ip = request.client.host if request.client else "unknown"

    ACTIVE_REQUESTS.inc()

    api_key = request.headers.get("x-api-key")
    is_public = path in _public_paths() or request.method == "OPTIONS"

    if not is_public:
        if not api_key or api_key not in configured_api_keys:
            AUTH_FAILURES.inc()
            REQUEST_COUNT.labels(method=method, path=path, status="401").inc()
            audit_logger.info(
                json.dumps(
                    {
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "event": "auth_failed",
                        "request_id": request_id,
                        "method": method,
                        "path": path,
                        "client_ip": client_ip,
                        "api_key": _mask_api_key(api_key),
                    },
                    ensure_ascii=True,
                )
            )
            ACTIVE_REQUESTS.dec()
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized: valid x-api-key is required."},
                headers={"X-Request-ID": request_id},
            )

    identity = api_key if api_key else client_ip
    allowed, retry_after = app.state.rate_limiter.allow(identity)
    if not allowed:
        RATE_LIMIT_REJECTIONS.inc()
        REQUEST_COUNT.labels(method=method, path=path, status="429").inc()
        audit_logger.info(
            json.dumps(
                {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "event": "rate_limited",
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "client_ip": client_ip,
                    "api_key": _mask_api_key(api_key),
                    "retry_after_s": retry_after,
                },
                ensure_ascii=True,
            )
        )
        ACTIVE_REQUESTS.dec()
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded."},
            headers={"Retry-After": str(retry_after), "X-Request-ID": request_id},
        )

    response = None
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        elapsed = time.perf_counter() - start
        REQUEST_COUNT.labels(method=method, path=path, status=str(status_code)).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(elapsed)
        audit_logger.info(
            json.dumps(
                {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "event": "request",
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status": status_code,
                    "latency_ms": round(elapsed * 1000, 3),
                    "client_ip": client_ip,
                    "api_key": _mask_api_key(api_key),
                },
                ensure_ascii=True,
            )
        )
        if response is not None:
            response.headers["X-Request-ID"] = request_id
        ACTIVE_REQUESTS.dec()


@app.get("/")
def root():
    return {
        "service": "EntropyHub API",
        "version": app.version,
        "docs": "/docs",
        "postprocessing": "von_neumann",
        "security": {
            "auth": "x-api-key",
            "rate_limit_per_minute": app.state.rate_limiter.limit_per_minute,
        },
    }


@app.get("/health")
def health():
    profile = service.profile()
    return {
        "status": "healthy",
        "version": app.version,
        "chaos_system": "Rossler",
        "rust_core_available": bool(RUST_CORE_AVAILABLE),
        "postprocessing": profile["postprocessing"],
        "live_entropy_reseed": profile["use_live_qrng"],
        "reseed_count": profile["reseed_count"],
        "pqc": "ML-KEM-768",
    }


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/chaos/reseed")
def chaos_reseed(request: ReseedRequest):
    return service.reseed(request.source)


@app.post("/random/bytes")
def random_bytes(request: RandomBytesRequest):
    values = service.random_bytes(request.count)
    GENERATED_BYTES.inc(request.count)
    return {
        "bytes": values,
        "count": request.count,
        "entropy_estimate": round(_shannon_entropy(values), 6),
        "postprocessing": "von_neumann",
    }


@app.post("/random/integers")
def random_integers(request: RandomIntegersRequest):
    GENERATED_BYTES.inc(request.count)
    return {
        "values": service.random_integers(request.count, request.min_val, request.max_val),
        "count": request.count,
        "min_val": request.min_val,
        "max_val": request.max_val,
    }


@app.post("/crypto/kyber768/keypair")
def kyber_keypair():
    public_key, secret_key = Kyber768.keygen()
    return {
        "public_key": public_key.hex(),
        "secret_key": secret_key.hex(),
        "public_key_size": len(public_key),
        "secret_key_size": len(secret_key),
        "algorithm": "ML-KEM-768",
    }


@app.post("/crypto/kyber768/encapsulate")
def kyber_encapsulate(request: KyberEncapsRequest):
    try:
        shared_secret, ciphertext = Kyber768.encaps(bytes.fromhex(request.public_key_hex))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "ciphertext": ciphertext.hex(),
        "ciphertext_size": len(ciphertext),
        "shared_secret": shared_secret.hex(),
        "shared_secret_size": len(shared_secret),
        "algorithm": "ML-KEM-768",
    }


@app.post("/crypto/kyber768/decapsulate")
def kyber_decapsulate(request: KyberDecapsRequest):
    try:
        shared_secret = Kyber768.decaps(
            bytes.fromhex(request.secret_key_hex),
            bytes.fromhex(request.ciphertext_hex),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "shared_secret": shared_secret.hex(),
        "shared_secret_size": len(shared_secret),
        "algorithm": "ML-KEM-768",
    }


if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Proje kök dizinini Python yoluna ekle (core modülü için)
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    uvicorn.run(app, host="0.0.0.0", port=8000)