from __future__ import annotations

import asyncio
import time
import traceback
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    import logging
    from collections.abc import Awaitable, Callable

T = TypeVar("T")


# see https://stackoverflow.com/questions/55184226/catching-exceptions-in-individual-tasks-and-restarting-them
async def rerun_on_exception(
    coro: Callable[..., Awaitable[T]],
    *args: object,
    logger: logging.Logger,
    **kwargs: object,
) -> T:
    """Restart coroutine by waiting an exponential time delay"""
    max_sleep = 5 * 60  # sleep for at most 5 mins until rerun
    reset = 3 * 60  # reset after 3 minutes running successfully
    init_sleep = 1  # always start with sleeping for 1 second

    next_sleep = init_sleep
    while True:
        start_t = int(time.monotonic())  # seconds

        try:
            return await coro(*args, **kwargs)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001 -- `coro` is arbitrary caller-supplied
            # code; this restarts it on any failure, so the exception type
            # can't be narrowed further.
            traceback.print_exc()

        end_t = int(time.monotonic())  # seconds

        if end_t - start_t < reset:
            sleep_t = next_sleep
            next_sleep = min(max_sleep, next_sleep * 2)  # double sleep time
        else:
            next_sleep = init_sleep  # reset sleep time
            sleep_t = next_sleep

        logger.warning("Restarting coroutine in %s seconds", sleep_t)
        await asyncio.sleep(sleep_t)
