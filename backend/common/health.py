"""Shared health-check request/reply handler for the domain services.

Each service exposes it on `<domain>.health`; the gateway pings these subjects
to build its own `/health` response.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session

from .messaging import Outcome


def health_handler(db: Session, request: dict) -> Outcome:
    """Confirm the service is up and its database answers a trivial query."""
    db.execute(text("SELECT 1"))
    return Outcome(reply={"status": "ok"})
