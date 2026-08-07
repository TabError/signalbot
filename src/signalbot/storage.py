from __future__ import annotations

import contextlib

with contextlib.suppress(ModuleNotFoundError):
    import redis

import json
import sqlite3
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeAlias

from signalbot.errors import SignalBotError

if TYPE_CHECKING:
    from pathlib import Path

JSONValue: TypeAlias = (
    "str | int | float | bool | None | dict[str, JSONValue] | list[JSONValue]"
)


class Storage(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check whether a key exists in storage.

        Args:
            key: Storage key to check.

        Returns:
            True if the key exists, otherwise False.
        """

    @abstractmethod
    def read(self, key: str) -> JSONValue:
        """Read a value from storage.

        Args:
            key: Storage key to read.

        Returns:
            The deserialized value stored under the given key.
        """

    @abstractmethod
    def save(self, key: str, value: JSONValue) -> None:
        """Save a value to storage.

        Args:
            key: Storage key to write.
            value: JSON-serializable value to store.
        """

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a key from storage.

        Args:
            key: Storage key to delete.
        """


class StorageError(SignalBotError):
    """Raised when a storage backend operation fails."""


class SQLiteStorage(Storage):
    """SQLite-backed storage."""

    def __init__(self, database: str | Path = ":memory:", **kwargs: object) -> None:
        """Initialize SQLite-backed storage.

        Args:
            database: Path to the sqlite database file or `:memory:`.
            **kwargs: Additional keyword arguments passed to `sqlite3.connect`.
        """
        self._sqlite = sqlite3.connect(database, **kwargs)
        self._sqlite.execute(
            "CREATE TABLE IF NOT EXISTS signalbot (key text unique, value text)",
        )

    def exists(self, key: str) -> bool:
        """Check whether a key exists in SQLite storage.

        Args:
            key: Storage key to check.

        Returns:
            True if the key exists, otherwise False.
        """
        return self._sqlite.execute(
            "SELECT EXISTS(SELECT 1 FROM signalbot WHERE key = ?)",
            [key],
        ).fetchone()[0]

    def read(self, key: str) -> JSONValue:
        """Read and deserialize a value from SQLite storage.

        Args:
            key: Storage key to read.

        Returns:
            The deserialized value stored under the key.

        Raises:
            StorageError: If the key does not exist or deserialization fails.
        """
        try:
            result = self._sqlite.execute(
                "SELECT value FROM signalbot WHERE key = ?",
                [key],
            ).fetchone()[0]
            return json.loads(result)
        except (sqlite3.Error, TypeError, json.JSONDecodeError) as e:
            error_msg = f"SQLite load failed: {e}"
            raise StorageError(error_msg) from e

    def save(self, key: str, value: JSONValue) -> None:
        """Serialize and save a value to SQLite storage.

        Args:
            key: Storage key to write.
            value: JSON-serializable value to store.

        Raises:
            StorageError: If serialization or database write fails.
        """
        try:
            serialized = json.dumps(value)
            self._sqlite.execute(
                "INSERT INTO signalbot VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=?",
                [key, serialized, serialized],
            )
            self._sqlite.commit()
        except (sqlite3.Error, TypeError) as e:
            error_msg = f"SQLite save failed: {e}"
            raise StorageError(error_msg) from e

    def delete(self, key: str) -> None:
        """Delete a key from SQLite storage.

        Args:
            key: Storage key to delete.

        Raises:
            StorageError: If the delete operation fails.
        """
        try:
            self._sqlite.execute("DELETE FROM signalbot WHERE key = ?", [key])
            self._sqlite.commit()
        except sqlite3.Error as e:
            error_msg = f"SQLite delete failed: {e}"
            raise StorageError(error_msg) from e


class RedisStorage(Storage):
    """Redis-backed storage."""

    def __init__(self, host: str, port: int, password: str | None = None) -> None:
        """Initialize Redis-backed storage.

        Args:
            host: Redis host address.
            port: Redis server port.
            password: Optional Redis password.
        """
        self._redis = redis.Redis(host=host, port=port, db=0, password=password)

    def exists(self, key: str) -> bool:
        """Check whether a key exists in Redis storage.

        Args:
            key: Storage key to check.

        Returns:
            True if the key exists, otherwise False.
        """
        return self._redis.exists(key)

    def read(self, key: str) -> JSONValue:
        """Read and deserialize a value from Redis storage.

        Args:
            key: Storage key to read.

        Returns:
            The deserialized value stored under the key.

        Raises:
            StorageError: If the key does not exist or deserialization fails.
        """
        try:
            result_bytes = self._redis.get(key)
            result_str = result_bytes.decode("utf-8")
        except (redis.RedisError, AttributeError) as e:
            error_msg = f"Redis load failed: {e}"
            raise StorageError(error_msg) from e

        try:
            return json.loads(result_str)
        except json.JSONDecodeError as e:
            error_msg = f"Redis load failed: {e}"
            raise StorageError(error_msg) from e

    def save(self, key: str, value: JSONValue) -> None:
        """Serialize and save a value to Redis storage.

        Args:
            key: Storage key to write.
            value: JSON-serializable value to store.

        Raises:
            StorageError: If serialization or Redis write fails.
        """
        try:
            serialized = json.dumps(value)
            self._redis.set(key, serialized)
        except (redis.RedisError, TypeError) as e:
            error_msg = f"Redis save failed: {e}"
            raise StorageError(error_msg) from e

    def delete(self, key: str) -> None:
        """Delete a key from Redis storage.

        Args:
            key: Storage key to delete.

        Raises:
            StorageError: If the delete operation fails.
        """
        try:
            self._redis.delete(key)
        except redis.RedisError as e:
            error_msg = f"Redis delete failed: {e}"
            raise StorageError(error_msg) from e
