"""category-service entry point.

Subscribes to the `category.*` request/reply subjects and serves them from its
own database, publishing `category.{created,deleted}` events on change.
"""
import asyncio
import signal

from backend.common.messaging import connect, make_rpc_callback, rpc_subject

from .database import SessionLocal, init_db
from .handlers import HANDLERS

DOMAIN = "category"


async def main() -> None:
    init_db()
    nc = await connect(f"{DOMAIN}-service")

    for operation, handler in HANDLERS.items():
        await nc.subscribe(
            rpc_subject(DOMAIN, operation),
            queue=f"{DOMAIN}-service",
            cb=make_rpc_callback(nc, DOMAIN, SessionLocal, handler),
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
