"""NATS connection management and request helpers for the gateway.

The gateway holds a single NATS connection for its lifetime. `call` issues a
request/reply to a domain service and translates the reply envelope (or a
timeout) into an HTTP result, so route handlers stay thin.
"""
import nats.errors
from fastapi import HTTPException
from nats.aio.client import Client as NATSClient

from backend.common.messaging import DOMAINS, connect, request, rpc_subject

_nc: NATSClient | None = None


async def connect_nats() -> None:
    """Open the gateway's NATS connection (called from the app lifespan)."""
    global _nc
    _nc = await connect("gateway")


async def close_nats() -> None:
    """Drain and close the NATS connection on shutdown."""
    if _nc is not None:
        await _nc.drain()


def _require_nats() -> NATSClient:
    if _nc is None or not _nc.is_connected:
        raise HTTPException(
            status_code=503, detail="Gateway is not connected to NATS"
        )
    return _nc


async def call(subject: str, payload: dict):
    """Issue a request/reply call; raise `HTTPException` on error or timeout.

    A NATS timeout / missing responder becomes a `503`; an error envelope is
    re-raised with the service's own status and detail.
    """
    nc = _require_nats()
    try:
        reply = await request(nc, subject, payload)
    except (nats.errors.TimeoutError, nats.errors.NoRespondersError):
        raise HTTPException(
            status_code=503,
            detail=f"The service handling '{subject}' is unavailable",
        )
    if not reply.get("ok"):
        error = reply.get("error") or {}
        raise HTTPException(
            status_code=error.get("status", 500),
            detail=error.get("detail", "Service error"),
        )
    return reply.get("data")


async def health_check() -> dict:
    """Report healthy only if NATS and every domain service respond."""
    if _nc is None or not _nc.is_connected:
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "detail": "NATS not connected"},
        )

    services: dict[str, str] = {}
    for domain in DOMAINS:
        try:
            reply = await request(
                _nc, rpc_subject(domain, "health"), {}, timeout=2
            )
            ok = bool(reply.get("ok"))
        except (nats.errors.TimeoutError, nats.errors.NoRespondersError):
            ok = False
        services[domain] = "ok" if ok else "unavailable"

    if any(state != "ok" for state in services.values()):
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "services": services},
        )
    return {"status": "ok", "services": services}
