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
