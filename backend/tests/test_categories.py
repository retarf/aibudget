"""Tests for the category-api capability."""


def test_create_category(client):
    resp = client.post("/categories", json={"name": "Salary", "kind": "income"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Salary"
    assert body["kind"] == "income"
    assert "id" in body


def test_duplicate_name_within_kind_rejected(client):
    client.post("/categories", json={"name": "Food", "kind": "expense"})
    resp = client.post("/categories", json={"name": "Food", "kind": "expense"})
    assert resp.status_code == 409


def test_same_name_different_kind_allowed(client):
    client.post("/categories", json={"name": "Bonus", "kind": "income"})
    resp = client.post("/categories", json={"name": "Bonus", "kind": "expense"})
    assert resp.status_code == 201


def test_invalid_kind_rejected(client):
    resp = client.post("/categories", json={"name": "Savings", "kind": "saving"})
    assert resp.status_code == 422


def test_list_all_categories(client):
    client.post("/categories", json={"name": "Food", "kind": "expense"})
    client.post("/categories", json={"name": "Salary", "kind": "income"})
    resp = client.get("/categories")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_categories_filtered_by_kind(client):
    client.post("/categories", json={"name": "Food", "kind": "expense"})
    client.post("/categories", json={"name": "Salary", "kind": "income"})
    resp = client.get("/categories", params={"kind": "income"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["kind"] == "income"


def test_delete_unused_category(client):
    cid = client.post(
        "/categories", json={"name": "Food", "kind": "expense"}
    ).json()["id"]
    assert client.delete(f"/categories/{cid}").status_code == 204
    assert client.get("/categories").json() == []


def test_delete_category_in_use_rejected(client):
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
    client.post(
        f"/budgets/{bid}/transactions",
        json={
            "type": "expense",
            "amount": "10.00",
            "date": "2026-05-10",
            "category_id": cid,
        },
    )
    assert client.delete(f"/categories/{cid}").status_code == 409
