"""Tests for the gateway: envelope/timeout mapping, routing, and health."""
import asyncio

import nats.errors
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.gateway import nats_client
from backend.gateway.main import app

BUDGET = {
    "id": 1,
    "name": "May",
    "start_date": "2026-05-01",
    "end_date": "2026-05-31",
}


# --- call(): envelope and timeout mapping -----------------------------------

def test_call_returns_data_on_success(fake_request):
    fake_request({"budget.list": {"ok": True, "data": [BUDGET]}})
    data = asyncio.run(nats_client.call("budget.list", {}))
    assert data == [BUDGET]


def test_call_maps_error_envelope_to_http_status(fake_request):
    fake_request(
        {
            "category.create": {
                "ok": False,
                "error": {"status": 409, "detail": "duplicate"},
            }
        }
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(nats_client.call("category.create", {}))
    assert exc.value.status_code == 409
    assert exc.value.detail == "duplicate"


def test_call_maps_timeout_to_503(fake_request):
    fake_request({"budget.get": nats.errors.TimeoutError()})
    with pytest.raises(HTTPException) as exc:
        asyncio.run(nats_client.call("budget.get", {"budget_id": 1}))
    assert exc.value.status_code == 503


# --- routing via TestClient -------------------------------------------------

def test_create_budget_route_returns_201(fake_request):
    fake_request({"budget.create": {"ok": True, "data": BUDGET}})
    # No `with` block: skip the app lifespan so no real NATS connect happens.
    client = TestClient(app)
    response = client.post(
        "/budgets",
        json={
            "name": "May",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
        },
    )
    assert response.status_code == 201
    assert response.json() == BUDGET


def test_error_envelope_surfaces_through_route(fake_request):
    fake_request(
        {
            "categories": None,  # unused
            "category.create": {
                "ok": False,
                "error": {"status": 409, "detail": "duplicate"},
            },
        }
    )
    client = TestClient(app)
    response = client.post(
        "/categories", json={"name": "Rent", "kind": "expense"}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "duplicate"


# --- health -----------------------------------------------------------------

def test_health_ok_when_all_services_respond(fake_request):
    fake_request(
        {
            "budget.health": {"ok": True, "data": {"status": "ok"}},
            "category.health": {"ok": True, "data": {"status": "ok"}},
            "transaction.health": {"ok": True, "data": {"status": "ok"}},
        }
    )
    result = asyncio.run(nats_client.health_check())
    assert result["status"] == "ok"


def test_health_unhealthy_when_a_service_is_down(fake_request):
    fake_request(
        {
            "budget.health": {"ok": True, "data": {"status": "ok"}},
            "category.health": {"ok": True, "data": {"status": "ok"}},
            "transaction.health": nats.errors.TimeoutError(),
        }
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(nats_client.health_check())
    assert exc.value.status_code == 503


# --- enhanced summary route -------------------------------------------------


def test_summary_route_merges_allocations_and_actuals(fake_request):
    fake_request(
        {
            "budget.allocation.list": {
                "ok": True,
                "data": [
                    {
                        "id": 10,
                        "budget_id": 1,
                        "category_id": 1,
                        "planned_amount": "500.00",
                    },
                    {
                        "id": 11,
                        "budget_id": 1,
                        "category_id": 2,
                        "planned_amount": "1500.00",
                    },
                ],
            },
            "transaction.summary.categories": {
                "ok": True,
                "data": [
                    {
                        "category_id": 1,
                        "kind": "expense",
                        "income": "0.00",
                        "expense": "320.00",
                    },
                    {
                        "category_id": 2,
                        "kind": "income",
                        "income": "1200.00",
                        "expense": "0.00",
                    },
                ],
            },
        }
    )
    client = TestClient(app)
    response = client.get("/budgets/1/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["budget_id"] == 1
    assert body["totals"] == {
        "planned_income": "1500.00",
        "actual_income": "1200.00",
        "planned_expense": "500.00",
        "actual_expense": "320.00",
        "net": "880.00",
    }
    by_category = {row["category_id"]: row for row in body["categories"]}
    assert by_category[1] == {
        "category_id": 1,
        "kind": "expense",
        "planned_amount": "500.00",
        "actual_amount": "320.00",
    }
    assert by_category[2] == {
        "category_id": 2,
        "kind": "income",
        "planned_amount": "1500.00",
        "actual_amount": "1200.00",
    }


def test_summary_route_with_allocations_only(fake_request):
    fake_request(
        {
            "budget.allocation.list": {
                "ok": True,
                "data": [
                    {
                        "id": 10,
                        "budget_id": 1,
                        "category_id": 1,
                        "planned_amount": "500.00",
                    }
                ],
            },
            "transaction.summary.categories": {"ok": True, "data": []},
        }
    )
    client = TestClient(app)
    response = client.get("/budgets/1/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["categories"] == [
        {
            "category_id": 1,
            "kind": "expense",
            "planned_amount": "500.00",
            "actual_amount": "0.00",
        }
    ]
    assert body["totals"]["actual_expense"] == "0.00"
    assert body["totals"]["planned_expense"] == "500.00"
    assert body["totals"]["net"] == "0.00"


def test_summary_route_with_transactions_only(fake_request):
    fake_request(
        {
            "budget.allocation.list": {"ok": True, "data": []},
            "transaction.summary.categories": {
                "ok": True,
                "data": [
                    {
                        "category_id": 3,
                        "kind": "expense",
                        "income": "0.00",
                        "expense": "75.00",
                    }
                ],
            },
        }
    )
    client = TestClient(app)
    response = client.get("/budgets/1/summary")
    body = response.json()
    assert body["categories"] == [
        {
            "category_id": 3,
            "kind": "expense",
            "planned_amount": "0.00",
            "actual_amount": "75.00",
        }
    ]
    assert body["totals"]["planned_expense"] == "0.00"
    assert body["totals"]["actual_expense"] == "75.00"


def test_summary_route_empty_budget(fake_request):
    fake_request(
        {
            "budget.allocation.list": {"ok": True, "data": []},
            "transaction.summary.categories": {"ok": True, "data": []},
        }
    )
    client = TestClient(app)
    response = client.get("/budgets/1/summary")
    body = response.json()
    assert body["categories"] == []
    assert body["totals"] == {
        "planned_income": "0.00",
        "actual_income": "0.00",
        "planned_expense": "0.00",
        "actual_expense": "0.00",
        "net": "0.00",
    }


def test_summary_route_surfaces_404_for_missing_budget(fake_request):
    fake_request(
        {
            "budget.allocation.list": {
                "ok": False,
                "error": {"status": 404, "detail": "Budget not found"},
            },
            "transaction.summary.categories": {
                "ok": False,
                "error": {"status": 404, "detail": "Budget not found"},
            },
        }
    )
    client = TestClient(app)
    response = client.get("/budgets/999/summary")
    assert response.status_code == 404
    assert response.json()["detail"] == "Budget not found"


# --- template routes --------------------------------------------------------

TEMPLATE = {"id": 1, "name": "Monthly"}
TEMPLATE_DETAIL = {
    "id": 1,
    "name": "Monthly",
    "items": [
        {"id": 5, "category_id": 1, "planned_amount": "100.00"},
    ],
}


def test_create_template_route_returns_201(fake_request):
    fake_request({"budget.template.create": {"ok": True, "data": TEMPLATE}})
    client = TestClient(app)
    response = client.post("/templates", json={"name": "Monthly"})
    assert response.status_code == 201
    assert response.json() == TEMPLATE


def test_list_templates_route(fake_request):
    fake_request(
        {"budget.template.list": {"ok": True, "data": [TEMPLATE]}}
    )
    client = TestClient(app)
    response = client.get("/templates")
    assert response.status_code == 200
    assert response.json() == [TEMPLATE]


def test_get_template_route_returns_items(fake_request):
    fake_request(
        {"budget.template.get": {"ok": True, "data": TEMPLATE_DETAIL}}
    )
    client = TestClient(app)
    response = client.get("/templates/1")
    assert response.status_code == 200
    assert response.json() == TEMPLATE_DETAIL


def test_add_template_item_route_returns_201(fake_request):
    item = {"id": 7, "category_id": 2, "planned_amount": "50.00"}
    fake_request({"budget.template.item.add": {"ok": True, "data": item}})
    client = TestClient(app)
    response = client.post(
        "/templates/1/items",
        json={"category_id": 2, "planned_amount": "50.00"},
    )
    assert response.status_code == 201
    assert response.json() == item


def test_add_template_item_route_surfaces_409(fake_request):
    fake_request(
        {
            "budget.template.item.add": {
                "ok": False,
                "error": {
                    "status": 409,
                    "detail": "Category already in template",
                },
            }
        }
    )
    client = TestClient(app)
    response = client.post(
        "/templates/1/items",
        json={"category_id": 2, "planned_amount": "50.00"},
    )
    assert response.status_code == 409


def test_delete_template_route_returns_204(fake_request):
    fake_request({"budget.template.delete": {"ok": True, "data": None}})
    client = TestClient(app)
    response = client.delete("/templates/1")
    assert response.status_code == 204


def test_apply_template_route_returns_allocations(fake_request):
    allocations = [
        {"id": 1, "budget_id": 1, "category_id": 1, "planned_amount": "100.00"}
    ]
    fake_request(
        {"budget.template.apply": {"ok": True, "data": allocations}}
    )
    client = TestClient(app)
    response = client.post(
        "/budgets/1/apply-template", json={"template_id": 1}
    )
    assert response.status_code == 200
    assert response.json() == allocations


# --- allocation routes ------------------------------------------------------

ALLOCATION = {
    "id": 1,
    "budget_id": 1,
    "category_id": 1,
    "planned_amount": "100.00",
}


def test_list_allocations_route(fake_request):
    fake_request(
        {"budget.allocation.list": {"ok": True, "data": [ALLOCATION]}}
    )
    client = TestClient(app)
    response = client.get("/budgets/1/allocations")
    assert response.status_code == 200
    assert response.json() == [ALLOCATION]


def test_create_allocation_route_returns_201(fake_request):
    fake_request(
        {"budget.allocation.create": {"ok": True, "data": ALLOCATION}}
    )
    client = TestClient(app)
    response = client.post(
        "/budgets/1/allocations",
        json={"category_id": 1, "planned_amount": "100.00"},
    )
    assert response.status_code == 201
    assert response.json() == ALLOCATION


def test_create_allocation_route_surfaces_409(fake_request):
    fake_request(
        {
            "budget.allocation.create": {
                "ok": False,
                "error": {"status": 409, "detail": "duplicate"},
            }
        }
    )
    client = TestClient(app)
    response = client.post(
        "/budgets/1/allocations",
        json={"category_id": 1, "planned_amount": "100.00"},
    )
    assert response.status_code == 409


def test_update_allocation_route(fake_request):
    updated = {**ALLOCATION, "planned_amount": "150.00"}
    fake_request(
        {"budget.allocation.update": {"ok": True, "data": updated}}
    )
    client = TestClient(app)
    response = client.put(
        "/budgets/1/allocations/1", json={"planned_amount": "150.00"}
    )
    assert response.status_code == 200
    assert response.json() == updated


def test_delete_allocation_route_returns_204(fake_request):
    fake_request({"budget.allocation.delete": {"ok": True, "data": None}})
    client = TestClient(app)
    response = client.delete("/budgets/1/allocations/1")
    assert response.status_code == 204
