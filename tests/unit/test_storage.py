from __future__ import annotations

import json
import sqlite3
from typing import TYPE_CHECKING, NamedTuple

import pytest
import redis as real_redis

from signalbot.storage import (
    RedisStorage,
    SQLiteStorage,
    StorageBackend,
    StorageError,
    StorageOperation,
)

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture


class _FakeRedisStorage(NamedTuple):
    storage: RedisStorage
    redis: MagicMock


class TestSQLiteStorage:
    def test_save_and_read_round_trip(self):
        storage = SQLiteStorage()
        storage.save("key", {"a": 1, "b": [1, 2, 3]})

        assert storage.read("key") == {"a": 1, "b": [1, 2, 3]}

    def test_save_supports_json_scalars_and_none(self):
        storage = SQLiteStorage()
        flag = True
        storage.save("num", 42)
        storage.save("text", "hello")
        storage.save("flag", flag)
        storage.save("nothing", None)

        assert storage.read("num") == 42
        assert storage.read("text") == "hello"
        assert storage.read("flag") is True
        assert storage.read("nothing") is None

    def test_exists_true_after_save_false_otherwise(self):
        storage = SQLiteStorage()

        assert not storage.exists("missing")

        storage.save("present", 1)

        assert storage.exists("present")

    def test_save_overwrites_existing_key(self):
        storage = SQLiteStorage()
        storage.save("key", "first")
        storage.save("key", "second")

        assert storage.read("key") == "second"
        # ensure the upsert didn't create a duplicate row
        rows = storage._sqlite.execute(
            "SELECT COUNT(*) FROM signalbot WHERE key = ?", ["key"]
        ).fetchone()[0]
        assert rows == 1

    def test_delete_removes_key(self):
        storage = SQLiteStorage()
        storage.save("key", "value")

        storage.delete("key")

        assert not storage.exists("key")

    def test_delete_missing_key_is_a_no_op(self):
        storage = SQLiteStorage()

        storage.delete("does-not-exist")  # must not raise

    def test_read_missing_key_raises_storage_error(self):
        storage = SQLiteStorage()

        with pytest.raises(StorageError) as exc_info:
            storage.read("missing")

        assert exc_info.value.backend is StorageBackend.SQLITE
        assert exc_info.value.operation is StorageOperation.LOAD

    def test_read_corrupt_value_raises_storage_error(self):
        storage = SQLiteStorage()
        # bypass save() to insert a value that isn't valid JSON
        storage._sqlite.execute(
            "INSERT INTO signalbot VALUES (?, ?)", ["key", "{not valid json"]
        )
        storage._sqlite.commit()

        with pytest.raises(StorageError) as exc_info:
            storage.read("key")

        assert exc_info.value.backend is StorageBackend.SQLITE
        assert exc_info.value.operation is StorageOperation.LOAD

    def test_save_wraps_sqlite_errors(self):
        storage = SQLiteStorage()
        storage._sqlite.close()

        with pytest.raises(StorageError) as exc_info:
            storage.save("key", "value")

        assert exc_info.value.backend is StorageBackend.SQLITE
        assert exc_info.value.operation is StorageOperation.SAVE
        assert isinstance(exc_info.value.cause, sqlite3.Error)

    def test_delete_wraps_sqlite_errors(self):
        storage = SQLiteStorage()
        storage._sqlite.close()

        with pytest.raises(StorageError) as exc_info:
            storage.delete("key")

        assert exc_info.value.backend is StorageBackend.SQLITE
        assert exc_info.value.operation is StorageOperation.DELETE

    def test_storage_error_message_includes_backend_operation_and_cause(self):
        storage = SQLiteStorage()

        with pytest.raises(StorageError) as exc_info:
            storage.read("missing")

        assert str(exc_info.value).startswith("SQLite load failed:")


class TestRedisStorage:
    def _storage_with_fake_client(self, mocker: MockerFixture) -> _FakeRedisStorage:
        mocker.patch("redis.Redis")
        storage = RedisStorage(host="localhost", port=6379)
        fake_redis = mocker.MagicMock()
        storage._redis = fake_redis
        return _FakeRedisStorage(storage, fake_redis)

    def test_init_without_password(self, mocker: MockerFixture):
        redis_cls = mocker.patch("redis.Redis")

        RedisStorage(host="localhost", port=6379)

        redis_cls.assert_called_once_with(
            host="localhost", port=6379, db=0, password=None
        )

    def test_init_with_password(self, mocker: MockerFixture):
        redis_cls = mocker.patch("redis.Redis")

        RedisStorage(host="localhost", port=6379, password="secret")

        redis_cls.assert_called_once_with(
            host="localhost", port=6379, db=0, password="secret"
        )

    def test_exists_reflects_redis_response(self, mocker: MockerFixture):
        storage, fake_redis = self._storage_with_fake_client(mocker)
        fake_redis.exists.return_value = 1

        assert storage.exists("key") is True

        fake_redis.exists.return_value = 0

        assert storage.exists("key") is False

    def test_save_and_read_round_trip(self, mocker: MockerFixture):
        storage, fake_redis = self._storage_with_fake_client(mocker)
        stored = {}
        fake_redis.set.side_effect = stored.__setitem__
        fake_redis.get.side_effect = lambda k: stored[k].encode("utf-8")

        storage.save("key", {"a": 1})

        assert storage.read("key") == {"a": 1}

    def test_read_missing_key_raises_storage_error(self, mocker: MockerFixture):
        storage, fake_redis = self._storage_with_fake_client(mocker)
        fake_redis.get.return_value = None

        with pytest.raises(StorageError) as exc_info:
            storage.read("missing")

        assert exc_info.value.backend is StorageBackend.REDIS
        assert exc_info.value.operation is StorageOperation.LOAD
        assert isinstance(exc_info.value.cause, KeyError)

    def test_read_corrupt_value_raises_storage_error(self, mocker: MockerFixture):
        storage, fake_redis = self._storage_with_fake_client(mocker)
        fake_redis.get.return_value = b"{not valid json"

        with pytest.raises(StorageError) as exc_info:
            storage.read("key")

        assert exc_info.value.backend is StorageBackend.REDIS
        assert exc_info.value.operation is StorageOperation.LOAD
        assert isinstance(exc_info.value.cause, json.JSONDecodeError)

    def test_read_wraps_redis_errors(self, mocker: MockerFixture):
        storage, fake_redis = self._storage_with_fake_client(mocker)
        fake_redis.get.side_effect = real_redis.RedisError("boom")

        with pytest.raises(StorageError) as exc_info:
            storage.read("key")

        assert exc_info.value.backend is StorageBackend.REDIS
        assert exc_info.value.operation is StorageOperation.LOAD

    def test_save_wraps_redis_errors(self, mocker: MockerFixture):
        storage, fake_redis = self._storage_with_fake_client(mocker)
        fake_redis.set.side_effect = real_redis.RedisError("boom")

        with pytest.raises(StorageError) as exc_info:
            storage.save("key", "value")

        assert exc_info.value.backend is StorageBackend.REDIS
        assert exc_info.value.operation is StorageOperation.SAVE

    def test_delete_wraps_redis_errors(self, mocker: MockerFixture):
        storage, fake_redis = self._storage_with_fake_client(mocker)
        fake_redis.delete.side_effect = real_redis.RedisError("boom")

        with pytest.raises(StorageError) as exc_info:
            storage.delete("key")

        assert exc_info.value.backend is StorageBackend.REDIS
        assert exc_info.value.operation is StorageOperation.DELETE

    def test_delete_calls_underlying_client(self, mocker: MockerFixture):
        storage, fake_redis = self._storage_with_fake_client(mocker)

        storage.delete("key")

        fake_redis.delete.assert_called_once_with("key")
