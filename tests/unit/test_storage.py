from __future__ import annotations

import importlib
from types import ModuleType
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import signalbot.storage as storage_mod

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def _make_mock_redis_module() -> ModuleType:
    """Return a fake redis module with a Redis class."""
    mock_redis_mod = ModuleType("redis")
    mock_redis_mod.Redis = MagicMock()
    return mock_redis_mod


class TestRedisStorage:
    def test_init_without_password(self, mocker: MockerFixture):
        mock_redis_mod = _make_mock_redis_module()
        mocker.patch.dict("sys.modules", {"redis": mock_redis_mod})
        importlib.reload(storage_mod)
        storage_mod.RedisStorage(host="localhost", port=6379)
        mock_redis_mod.Redis.assert_called_once_with(
            host="localhost", port=6379, db=0, password=None
        )

    def test_init_with_password(self, mocker: MockerFixture):
        mock_redis_mod = _make_mock_redis_module()
        mocker.patch.dict("sys.modules", {"redis": mock_redis_mod})
        importlib.reload(storage_mod)
        storage_mod.RedisStorage(host="localhost", port=6379, password="secret")
        mock_redis_mod.Redis.assert_called_once_with(
            host="localhost",
            port=6379,
            db=0,
            password="secret",
        )
