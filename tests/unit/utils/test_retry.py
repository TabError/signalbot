from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

import pytest

from signalbot.utils.retry import rerun_on_exception

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pytest_mock import MockerFixture


def _monotonic_sequence(values: Iterable[float]):
    """Yield `values` in order, then fall back to the real clock.

    `time.monotonic` also drives asyncio's own event loop scheduling, so a
    plain `side_effect=[...]` list would raise `StopIteration` once the loop
    calls it more times than the test cares to script.
    """
    it = iter(values)
    real_monotonic = time.monotonic

    def _next(*_args: object, **_kwargs: object) -> float:
        try:
            return next(it)
        except StopIteration:
            return real_monotonic()

    return _next


@pytest.fixture(autouse=True)
def _quiet_traceback(mocker: MockerFixture):
    # rerun_on_exception prints a traceback for every retried exception;
    # silence it so the retry tests below don't spam stderr.
    mocker.patch("signalbot.utils.retry.traceback.print_exc")


class TestRerunOnException:
    async def test_returns_result_without_retrying_on_success(
        self, mocker: MockerFixture
    ):
        sleep_mock = mocker.patch(
            "signalbot.utils.retry.asyncio.sleep", mocker.AsyncMock()
        )
        logger = mocker.MagicMock()

        async def coro() -> str:
            return "ok"

        result = await rerun_on_exception(coro, logger=logger)

        assert result == "ok"
        sleep_mock.assert_not_awaited()
        logger.warning.assert_not_called()

    async def test_passes_through_args_and_kwargs(self, mocker: MockerFixture):
        logger = mocker.MagicMock()

        async def coro(a: int, *, b: int) -> int:
            return a + b

        result = await rerun_on_exception(coro, 2, logger=logger, b=3)

        assert result == 5

    async def test_cancelled_error_propagates_without_retry(
        self, mocker: MockerFixture
    ):
        sleep_mock = mocker.patch(
            "signalbot.utils.retry.asyncio.sleep", mocker.AsyncMock()
        )
        logger = mocker.MagicMock()

        async def coro() -> None:
            raise asyncio.CancelledError

        with pytest.raises(asyncio.CancelledError):
            await rerun_on_exception(coro, logger=logger)

        sleep_mock.assert_not_awaited()

    async def test_retries_with_exponential_backoff_until_success(
        self, mocker: MockerFixture
    ):
        sleep_mock = mocker.patch(
            "signalbot.utils.retry.asyncio.sleep", mocker.AsyncMock()
        )
        logger = mocker.MagicMock()

        calls = 0

        async def flaky_coro() -> str:
            nonlocal calls
            calls += 1
            if calls <= 3:
                error_msg = f"failure #{calls}"
                raise ValueError(error_msg)
            return "ok"

        # The real clock advances by a negligible amount during this test, so
        # every iteration lands in the "still within reset window" branch and
        # next_sleep keeps doubling: 1, 2, 4.
        result = await rerun_on_exception(flaky_coro, logger=logger)

        assert result == "ok"
        assert calls == 4
        assert sleep_mock.await_args_list == [
            mocker.call(1),
            mocker.call(2),
            mocker.call(4),
        ]
        assert logger.warning.call_count == 3

    async def test_backoff_resets_after_running_past_reset_threshold(
        self, mocker: MockerFixture
    ):
        sleep_mock = mocker.patch(
            "signalbot.utils.retry.asyncio.sleep", mocker.AsyncMock()
        )
        logger = mocker.MagicMock()
        # loop 1: start=0, fails, end=0            -> within reset window
        # loop 2: start=1000, fails, end=1200       -> ran 200s (>= 180s reset)
        # loop 3: start=2000, succeeds
        mocker.patch(
            "signalbot.utils.retry.time.monotonic",
            side_effect=_monotonic_sequence([0, 0, 1000, 1200, 2000]),
        )

        calls = 0

        async def flaky_coro() -> str:
            nonlocal calls
            calls += 1
            if calls <= 2:
                error_msg = f"failure #{calls}"
                raise ValueError(error_msg)
            return "ok"

        result = await rerun_on_exception(flaky_coro, logger=logger)

        assert result == "ok"
        # Without the reset, the second sleep would be 2 (doubled from 1).
        # Because the coroutine ran past the reset threshold before its
        # second failure, next_sleep drops back to the initial 1s.
        assert sleep_mock.await_args_list == [mocker.call(1), mocker.call(1)]
