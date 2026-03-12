from fastapi.testclient import TestClient

from api.main import DEFAULT_DEMO_API_KEY, app


client = TestClient(app)
AUTH_HEADERS = {"x-api-key": DEFAULT_DEMO_API_KEY}


def test_health_endpoint_reports_runtime_features():
    response = client.get("/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["postprocessing"] == "von_neumann"
    assert payload["live_entropy_reseed"] is True


def test_protected_endpoint_requires_api_key():
    response = client.post("/random/bytes", json={"count": 8})
    assert response.status_code == 401


def test_random_bytes_endpoint_returns_requested_count():
    response = client.post("/random/bytes", json={"count": 32}, headers=AUTH_HEADERS)
    assert response.status_code == 200

    payload = response.json()
    assert payload["count"] == 32
    assert len(payload["bytes"]) == 32
    assert payload["postprocessing"] == "von_neumann"


def test_kyber_keypair_endpoint_returns_expected_sizes():
    response = client.post("/crypto/kyber768/keypair", headers=AUTH_HEADERS)
    assert response.status_code == 200

    payload = response.json()
    assert payload["public_key_size"] == 1184
    assert payload["secret_key_size"] == 2400
    assert payload["algorithm"] == "ML-KEM-768"


def test_metrics_endpoint_is_available_for_prometheus_scrape():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "entropyhub_http_requests_total" in response.text


def test_rate_limit_rejects_excess_requests():
    original_limit = app.state.rate_limiter.limit_per_minute
    app.state.rate_limiter.limit_per_minute = 2
    app.state.rate_limiter.reset()

    try:
        first = client.post("/random/bytes", json={"count": 1}, headers=AUTH_HEADERS)
        second = client.post("/random/bytes", json={"count": 1}, headers=AUTH_HEADERS)
        third = client.post("/random/bytes", json={"count": 1}, headers=AUTH_HEADERS)

        assert first.status_code == 200
        assert second.status_code == 200
        assert third.status_code == 429
    finally:
        app.state.rate_limiter.limit_per_minute = original_limit
        app.state.rate_limiter.reset()