import requests

BASE_URL = "http://localhost:8008"


def test_operations_list_structure() -> None:
    r = requests.get(f"{BASE_URL}/operations", timeout=2)
    assert r.status_code == 200

    data = r.json()
    assert "count" in data
    assert "items" in data
    assert isinstance(data["count"], int)
    assert isinstance(data["items"], list)


def test_operations_delete_returns_deleted_count() -> None:
    r = requests.delete(f"{BASE_URL}/operations", timeout=2)
    assert r.status_code == 200

    data = r.json()
    assert "deleted" in data
    assert isinstance(data["deleted"], int)
