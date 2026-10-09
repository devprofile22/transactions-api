import pytest
import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    # हर टेस्ट के लिए एक अलग, खाली temporary database
    monkeypatch.setattr(app_module, "DB", str(tmp_path / "test.db"))
    app_module.init_db()
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


def valid_body(ref="TXN-T1", amount=500, typ="DEBIT"):
    return {"reference_id": ref, "account_id": 1, "amount": amount, "type": typ}


def test_create_transaction_success(client):
    r = client.post("/transaction", json=valid_body())
    assert r.status_code == 201


def test_get_transaction(client):
    client.post("/transaction", json=valid_body())
    r = client.get("/transaction/1")
    assert r.status_code == 200
    assert r.get_json()["reference_id"] == "TXN-T1"


def test_negative_amount(client):
    r = client.post("/transaction", json=valid_body(amount=-50))
    assert r.status_code == 400


def test_missing_field(client):
    r = client.post("/transaction", json={"reference_id": "X", "amount": 10, "type": "DEBIT"})
    assert r.status_code == 400


def test_duplicate_reference_id(client):
    client.post("/transaction", json=valid_body())
    r = client.post("/transaction", json=valid_body())
    assert r.status_code == 409


def test_account_not_found(client):
    body = valid_body()
    body["account_id"] = 999
    r = client.post("/transaction", json=body)
    assert r.status_code == 404


def test_insufficient_balance(client):
    r = client.post("/transaction", json=valid_body(amount=999999))
    assert r.status_code == 422


def test_transaction_not_found(client):
    r = client.get("/transaction/9999")
    assert r.status_code == 404

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"