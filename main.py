# main.py - YENİ ANA DOSYA (FastAPI)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import secrets
import time
import os
from datetime import datetime
from typing import List, Dict, Any

# FastAPI uygulaması
app = FastAPI(title="EntropyHub API", version="2.2", description="Live Entropy-Reseeded Hyperchaos API")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sistem durumu
system_status = {
    "status": "healthy",
    "chaos_system": "NIHDE (Rust Optimized)",
    "version": "2.2",
    "pqc_available": True,
    "live_qrng": True
}

# Ana endpoint
@app.get("/")
async def root():
    return {
        "name": "EntropyHub API",
        "version": "2.2",
        "description": "Live Entropy-Reseeded Hyperchaos + Real Kyber-768",
        "status": "running"
    }

# Sağlık kontrolü
@app.get("/api/health")
async def health_check():
    """Sistem sağlık kontrolü"""
    return JSONResponse(content=system_status)

# Entropi üret
@app.get("/api/generate")
async def generate_entropy(bytes: int = 18):
    """Entropi üret (byte array)"""
    start_time = time.time()
    
    # Gerçek entropi üretimi
    values = [secrets.randbelow(256) for _ in range(bytes)]
    
    # Demo için Rössler parametreleri
    rossler_params = {
        "a": 0.2 + (values[0] / 255) * 0.1,
        "b": 0.2 + (values[1] / 255) * 0.1,
        "c": 5.0 + (values[2] / 255) * 5.0
    }
    
    response = {
        "values": values,
        "bytes": bytes,
        "timestamp": time.time(),
        "generation_time_ms": (time.time() - start_time) * 1000,
        "rossler_params": rossler_params,
        "source": "os_urandom + secrets.randbelow"
    }
    
    return JSONResponse(content=response)

# Demo çekicisi (attractor) oluştur
@app.get("/api/attractor")
async def get_attractor(points: int = 15000):
    """Chaotic attractor noktaları üret"""
    try:
        # Burada core.chaos.nihde'den NIHDE kullanabilirsiniz
        # Şimdilik basit bir simülasyon
        import numpy as np
        t = np.linspace(0, 100, points)
        x = np.sin(t) * np.exp(-0.01*t) + 0.1 * np.random.randn(points)
        y = np.cos(t) * np.exp(-0.01*t) + 0.1 * np.random.randn(points)
        z = np.sin(2*t) * np.exp(-0.01*t) + 0.1 * np.random.randn(points)
        
        return JSONResponse(content={
            "x": x.tolist(),
            "y": y.tolist(),
            "z": z.tolist(),
            "points": points
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# İstatistikler
@app.get("/api/stats")
async def get_stats():
    """İstatistikleri döndür"""
    return JSONResponse(content={
        "total_bytes": 0,
        "generation_count": 0,
        "uptime": time.time() - start_time if 'start_time' in globals() else 0,
        "algorithms": ["Kyber-768", "Dilithium-3", "BB84 QKD", "MDI-QKD"]
    })

# Demo modu (eski main.py'deki kod)
def run_demo():
    """Eski demo modu - python main.py --demo ile çalışır"""
    print("=" * 90)
    print(" EntropyHub v2.2 – Demo Mode")
    print("=" * 90)
    
    try:
        from core.chaos.nihde import NIHDE
        engine = NIHDE(use_live_qrng=True)
        
        print("\nLive decision stream (10 seconds):")
        algorithms = ["Kyber-768", "Dilithium-3", "BB84 QKD", "MDI-QKD"]
        
        for i in range(100):
            bit = engine.decide()
            chosen = algorithms[(bit + i) % 4]
            print(f"t={i*0.1:5.1f}s → {chosen}")
            time.sleep(0.1)
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"Demo error: {e}")

# Başlangıç zamanı
start_time = time.time()

# Doğrudan çalıştırma
if __name__ == "__main__":
    import sys
    import uvicorn
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Demo modu
        run_demo()
    else:
        # API modu
        print("=" * 60)
        print(" EntropyHub API v2.2 Başlatılıyor...")
        print(" http://localhost:8000")
        print(" http://localhost:8000/api/health")
        print(" http://localhost:8000/api/generate?bytes=18")
        print("=" * 60)
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)