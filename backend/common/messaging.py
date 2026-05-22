"""Shared NATS messaging helpers for the aibudget gateway and services.

Two messaging styles are supported:

* **Request/reply** — used on the gateway↔service edge. Subjects are
  ``<domain>.<operation>`` (e.g. ``budget.create``). Replies are envelopes:
  ``{"ok": true, "data": ...}`` or
  ``{"ok": false, "error": {"status": int, "detail": str}}``.
* **Events** — used between services. Subjects are ``<domain>.<change>``
  (e.g. ``budget.deleted``). Payloads are ``{"event": ..., "data": ...}``.
"""
import json
import os
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass
from typing import Any

import nats
from nats.aio.client import Client as NATSClient
from nats.aio.msg import Msg

# Connection URL and request timeout come from the environment (see .env).
NATS_URL = os.environ.get("NATS_URL", "nats://nats:4222")
REQUEST_TIMEOUT = float(os.environ.get("NATS_REQUEST_TIMEOUT", "5"))

DOMAINS = ("budget", "category", "transaction")
RPC_OPERATIONS = ("create", "list", "get", "update", "delete")
EVENT_CHANGES = ("created", "updated", "deleted")


class ServiceError(Exception):
    """A domain error raised by a service handler.

    Carries the HTTP status code and detail the monolith used, so the gateway
    can reproduce the original REST response.
    """

    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


@dataclass
class Outcome:
    """Result of a service operation: the reply payload and an optional event.

    ``event_change`` is one of ``created``/``updated``/``deleted`` when the
    operation changed state and should publish an event; ``None`` for reads.
    """

    reply: Any = None
    event_change: str | None = None
    event_data: Any = None


async def connect(name: str) -> NATSClient:
    """Open a NATS connection labelled with the service/gateway name."""
    return await nats.connect(NATS_URL, name=name)


def rpc_subject(domain: str, operation: str) -> str:
    """Request/reply subject for a domain operation, e.g. ``budget.create``."""
    return f"{domain}.{operation}"


def event_subject(domain: str, change: str) -> str:
    """Event subject for a domain state change, e.g. ``budget.deleted``."""
    return f"{domain}.{change}"


def _encode(payload: Any) -> bytes:
    # default=str renders date/Decimal values that JSON cannot encode natively.
    return json.dumps(payload, default=str).encode()


def _decode(data: bytes) -> dict:
    return json.loads(data.decode()) if data else {}


# --- request/reply envelopes -------------------------------------------------

def success_envelope(data: Any) -> bytes:
    return _encode({"ok": True, "data": data})


def error_envelope(status: int, detail: str) -> bytes:
    return _encode({"ok": False, "error": {"status": status, "detail": detail}})


# --- event envelopes ---------------------------------------------------------

def event_envelope(event: str, data: Any) -> bytes:
    return _encode({"event": event, "data": data})


# --- service side: serve request/reply, publish events ----------------------

def make_rpc_callback(
    nc: NATSClient,
    domain: str,
    session_factory: Callable[[], Any],
    fn: Callable[[Any, dict], Outcome],
) -> Callable[[Msg], Any]:
    """Wrap a sync ``fn(db, request) -> Outcome`` as a NATS request/reply callback.

    A fresh session is opened per request and closed afterwards. The reply
    envelope is sent first; if the ``Outcome`` carries an event change, the
    matching domain event is then published. ``ServiceError`` becomes an error
    envelope; any other exception becomes a ``500`` envelope so a caller never
    hangs waiting for a reply.
    """

    async def _cb(msg: Msg) -> None:
        try:
            with closing(session_factory()) as db:
                outcome = fn(db, _decode(msg.data))
            await msg.respond(success_envelope(outcome.reply))
            if outcome.event_change:
                subject = event_subject(domain, outcome.event_change)
                await nc.publish(
                    subject, event_envelope(subject, outcome.event_data)
                )
        except ServiceError as exc:
            await msg.respond(error_envelope(exc.status, exc.detail))
        except Exception as exc:  # noqa: BLE001 - last-resort guard
            await msg.respond(error_envelope(500, f"Internal error: {exc}"))

    return _cb


def make_event_callback(
    session_factory: Callable[[], Any],
    fn: Callable[[Any, str, Any], None],
) -> Callable[[Msg], Any]:
    """Wrap a sync ``fn(db, event_name, data)`` as a NATS event-subscription callback.

    Events are best-effort: a handler error is logged and swallowed so one bad
    message does not stop the subscription.
    """

    async def _cb(msg: Msg) -> None:
        try:
            envelope = _decode(msg.data)
            with closing(session_factory()) as db:
                fn(db, envelope["event"], envelope["data"])
        except Exception as exc:  # noqa: BLE001 - best-effort consumer
            print(f"event handler error on {msg.subject}: {exc}", flush=True)

    return _cb


# --- gateway side: issue request/reply --------------------------------------

async def request(
    nc: NATSClient, subject: str, payload: dict, timeout: float = REQUEST_TIMEOUT
) -> dict:
    """Issue a request/reply call and return the decoded reply envelope."""
    msg = await nc.request(subject, _encode(payload), timeout=timeout)
    return _decode(msg.data)
