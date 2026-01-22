import requests

BASE_URL = "http://localhost:8008"


def test_convert_ok() -> None:
    payload = {"from": "USD", "to": "RUB", "amount": 10}
    r = requests.post(f"{BASE_URL}/operations", json=payload, timeout=2)

    assert r.status_code == 200
    data = r.json()

    assert "rate" in data
    assert "result" in data
    assert "operation" in data

    op = data["operation"]
    assert op["from"] == "USD"
    assert op["to"] == "RUB"
    assert op["amount"] == 10.0
    assert op["rate"] == data["rate"]
    assert op["result"] == data["result"]
    assert "id" in op
    assert "ts" in op


def test_convert_unknown_currency_404() -> None:
    payload = {"from": "AAA", "to": "RUB", "amount": 10}
    r = requests.post(f"{BASE_URL}/operations", json=payload, timeout=2)
    assert r.status_code == 404


def test_convert_bad_request_400() -> None:
    payload = {"from": "USD", "to": "RUB", "amount": 0}
    r = requests.post(f"{BASE_URL}/operations", json=payload, timeout=2)
    assert r.status_code == 400
