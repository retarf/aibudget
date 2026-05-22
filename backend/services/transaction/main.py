"""transaction-service entry point.

Subscribes to the `transaction.*` request/reply subjects, and to `budget.*` /
`category.*` events that feed the local projections and drive the delete
cascades. Publishes `transaction.{created,updated,deleted}` events on change.
"""
import asyncio
import signal

from backend.common.messaging import (
    connect,
    event_subject,
    make_event_callback,
    make_rpc_callback,
    rpc_subject,
)

from .database import SessionLocal, init_db
from .handlers import HANDLERS
from .projection import apply_event

DOMAIN = "transaction"

# Events consumed to maintain the projections and cascade deletes.
CONSUMED_EVENTS = (
    event_subject("budget", "created"),
    event_subject("budget", "updated"),
    event_subject("budget", "deleted"),
    event_subject("category", "created"),
    event_subject("category", "deleted"),
)


async def main() -> None:
    init_db()
    nc = await connect(f"{DOMAIN}-service")

    for operation, handler in HANDLERS.items():
        await nc.subscribe(
            rpc_subject(DOMAIN, operation),
            queue=f"{DOMAIN}-service",
            cb=make_rpc_callback(nc, DOMAIN, SessionLocal, handler),
        )

    event_cb = make_event_callback(SessionLocal, apply_event)
    for subject in CONSUMED_EVENTS:
        # Queue group: instances share one database, so one applies each event.
        await nc.subscribe(
            subject, queue=f"{DOMAIN}-service-events", cb=event_cb
        )

    print(f"{DOMAIN}-service ready", flush=True)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)
    await stop.wait()
    await nc.drain()


if __name__ == "__main__":
    asyncio.run(main())
