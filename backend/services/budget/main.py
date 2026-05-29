"""budget-service entry point.

Subscribes to the `budget.*` request/reply subjects and serves them from its
own database, publishing `budget.{created,updated,deleted}` events on change.
Also consumes `category.deleted` to cascade-delete template line items that
reference the removed category.
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
from .events import apply_event
from .handlers import HANDLERS

DOMAIN = "budget"

# Events consumed to cascade through template line items.
CONSUMED_EVENTS = (event_subject("category", "deleted"),)


async def main() -> None:
    init_db()
    nc = await connect(f"{DOMAIN}-service")

    for operation, handler in HANDLERS.items():
        await nc.subscribe(
            rpc_subject(DOMAIN, operation),
            # Queue group so multiple instances share the load.
            queue=f"{DOMAIN}-service",
            cb=make_rpc_callback(nc, DOMAIN, SessionLocal, handler),
        )

    event_cb = make_event_callback(SessionLocal, apply_event)
    for subject in CONSUMED_EVENTS:
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
