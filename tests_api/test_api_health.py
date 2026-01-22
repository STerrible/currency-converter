import requests

BASE_URL = "http://localhost:8008"


def test_health_ok() -> None:
    r = requests.get(f"{BASE_URL}/health", timeout=2)
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
