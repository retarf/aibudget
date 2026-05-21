"""Tests for the transaction-api capability."""
from decimal import Decimal


def _setup(client):
    """Create a category and a budget; return (budget_id, category_id)."""
    cid = client.post(
        "/categories", json={"name": "Food", "kind": "expense"}
    ).json()["id"]
    bid = client.post(
        "/budgets",
        json={
            "name": "May",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
        },
    ).json()["id"]
    return bid, cid


def _transaction(amount="12.50", date="2026-05-10", **overrides):
    body = {"type": "expense", "amount": amount, "date": date}
    body.update(overrides)
    return body


def test_record_transaction(client):
    bid, cid = _setup(client)
    resp = client.post(
        f"/budgets/{bid}/transactions", json=_transaction(category_id=cid)
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["budget_id"] == bid
    assert Decimal(body["amount"]) == Decimal("12.50")


def test_date_outside_budget_period_rejected(client):
    bid, cid = _setup(client)
    resp = client.post(
        f"/budgets/{bid}/transactions",
        json=_transaction(date="2026-06-10", category_id=cid),
    )
    assert resp.status_code == 422


def test_non_positive_amount_rejected(client):
    bid, cid = _setup(client)
    resp = client.post(
        f"/budgets/{bid}/transactions",
        json=_transaction(amount="0", category_id=cid),
    )
    assert resp.status_code == 422


def test_transaction_for_missing_budget(client):
    _, cid = _setup(client)
    resp = client.post(
        "/budgets/999/transactions", json=_transaction(category_id=cid)
    )
    assert resp.status_code == 404


def test_list_transactions(client):
    bid, cid = _setup(client)
    client.post(
        f"/budgets/{bid}/transactions", json=_transaction(category_id=cid)
    )
    client.post(
        f"/budgets/{bid}/transactions",
        json=_transaction(date="2026-05-11", category_id=cid),
    )
    resp = client.get(f"/budgets/{bid}/transactions")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_retrieve_transaction(client):
    bid, cid = _setup(client)
    tid = client.post(
        f"/budgets/{bid}/transactions", json=_transaction(category_id=cid)
    ).json()["id"]
    resp = client.get(f"/transactions/{tid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == tid


def test_retrieve_missing_transaction(client):
    assert client.get("/transactions/999").status_code == 404


def test_update_transaction(client):
    bid, cid = _setup(client)
    tid = client.post(
        f"/budgets/{bid}/transactions", json=_transaction(category_id=cid)
    ).json()["id"]
    resp = client.put(
        f"/transactions/{tid}",
        json=_transaction(amount="9.99", date="2026-05-12", category_id=cid),
    )
    assert resp.status_code == 200
    assert Decimal(resp.json()["amount"]) == Decimal("9.99")


def test_update_missing_transaction(client):
    _, cid = _setup(client)
    resp = client.put(
        "/transactions/999", json=_transaction(category_id=cid)
    )
    assert resp.status_code == 404


def test_delete_transaction(client):
    bid, cid = _setup(client)
    tid = client.post(
        f"/budgets/{bid}/transactions", json=_transaction(category_id=cid)
    ).json()["id"]
    assert client.delete(f"/transactions/{tid}").status_code == 204
    assert client.get(f"/transactions/{tid}").status_code == 404


def test_delete_missing_transaction(client):
    assert client.delete("/transactions/999").status_code == 404
