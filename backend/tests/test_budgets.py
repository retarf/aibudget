"""Tests for the budget-api capability."""


def _create_budget(client, name="May", start="2026-05-01", end="2026-05-31"):
    return client.post(
        "/budgets",
        json={"name": name, "start_date": start, "end_date": end},
    )


def test_create_budget(client):
    resp = _create_budget(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "May"
    assert "id" in body


def test_invalid_period_rejected(client):
    resp = _create_budget(client, start="2026-05-31", end="2026-05-01")
    assert resp.status_code == 422


def test_equal_start_and_end_rejected(client):
    resp = _create_budget(client, start="2026-05-01", end="2026-05-01")
    assert resp.status_code == 422


def test_list_budgets(client):
    _create_budget(client, "May")
    _create_budget(client, "June", "2026-06-01", "2026-06-30")
    resp = client.get("/budgets")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_retrieve_budget(client):
    bid = _create_budget(client).json()["id"]
    resp = client.get(f"/budgets/{bid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == bid


def test_retrieve_missing_budget(client):
    assert client.get("/budgets/999").status_code == 404


def test_update_budget(client):
    bid = _create_budget(client).json()["id"]
    resp = client.put(
        f"/budgets/{bid}",
        json={
            "name": "May (updated)",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "May (updated)"


def test_update_missing_budget(client):
    resp = client.put(
        "/budgets/999",
        json={
            "name": "X",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
        },
    )
    assert resp.status_code == 404


def test_delete_budget(client):
    bid = _create_budget(client).json()["id"]
    assert client.delete(f"/budgets/{bid}").status_code == 204
    assert client.get(f"/budgets/{bid}").status_code == 404


def test_delete_missing_budget(client):
    assert client.delete("/budgets/999").status_code == 404


def test_delete_budget_cascades_transactions(client):
    cid = client.post(
        "/categories", json={"name": "Food", "kind": "expense"}
    ).json()["id"]
    bid = _create_budget(client).json()["id"]
    tid = client.post(
        f"/budgets/{bid}/transactions",
        json={
            "type": "expense",
            "amount": "5.00",
            "date": "2026-05-10",
            "category_id": cid,
        },
    ).json()["id"]
    client.delete(f"/budgets/{bid}")
    assert client.get(f"/transactions/{tid}").status_code == 404
