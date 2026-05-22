"""Test fixtures for the gateway.

The gateway's NATS layer is mocked: tests patch `gateway.nats_client.request`
(the request/reply call) and the held connection, so no NATS server is needed.
"""
import pytest

from backend.gateway import nats_client


class _FakeNATS:
    """Stand-in for a connected NATS client."""

    is_connected = True


@pytest.fixture
def connected(monkeypatch):
    """Pretend the gateway holds a live NATS connection."""
    monkeypatch.setattr(nats_client, "_nc", _FakeNATS())


@pytest.fixture
def fake_request(monkeypatch, connected):
    """Install a fake `request`; the test supplies replies keyed by subject.

    Returns a setter taking ``{subject: envelope_or_exception}``.
    """

    def install(responses: dict):
        async def _request(nc, subject, payload, timeout=None):
            reply = responses[subject]
            if isinstance(reply, BaseException):
                raise reply
            return reply

        monkeypatch.setattr(nats_client, "request", _request)

    return install
