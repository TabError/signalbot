from __future__ import annotations

try:  # noqa: SIM105
    import redis
except ModuleNotFoundError:
    pass

import json
import sqlite3
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


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
    def read(self, key: str) -> Any:  # noqa: ANN401
        """Read a value from storage.

        Args:
            key: Storage key to read.

        Returns:
            The deserialized value stored under the given key.
        """

    @abstractmethod
    def save(self, key: str, object: Any) -> None:  # noqa: A002, ANN401
        """Save a value to storage.

        Args:
            key: Storage key to write.
            object: JSON-serializable value to store.
        """

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a key from storage.

        Args:
            key: Storage key to delete.
        """


class StorageError(Exception):
    """Raised when a storage backend operation fails."""


class SQLiteStorage(Storage):
    """SQLite-backed storage."""

    def __init__(self, database: str | Path = ":memory:", **kwargs: Any):  # noqa: ANN401, ANN204
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

    def read(self, key: str) -> Any:  # noqa: ANN401
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
        except Exception as e:  # noqa: BLE001
            raise StorageError(f"SQLite load failed: {e}")  # noqa: B904, EM102, TRY003

    def save(self, key: str, object: Any) -> None:  # noqa: A002, ANN401
        """Serialize and save a value to SQLite storage.

        Args:
            key: Storage key to write.
            object: JSON-serializable value to store.

        Raises:
            StorageError: If serialization or database write fails.
        """
        try:
            value = json.dumps(object)
            self._sqlite.execute(
                "INSERT INTO signalbot VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=?",  # noqa: E501
                [key, value, value],
            )
            self._sqlite.commit()
        except Exception as e:  # noqa: BLE001
            raise StorageError(f"SQLite save failed: {e}")  # noqa: B904, EM102, TRY003

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
        except Exception as e:  # noqa: BLE001
            raise StorageError(f"SQLite delete failed: {e}")  # noqa: B904, EM102, TRY003


class RedisStorage(Storage):
    """Redis-backed storage."""

    def __init__(self, host: str, port: int, password: str | None = None):  # noqa: ANN204
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

    def read(self, key: str) -> Any:  # noqa: ANN401
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
            result_dict = json.loads(result_str)
            return result_dict  # noqa: RET504, TRY300
        except Exception as e:  # noqa: BLE001
            raise StorageError(f"Redis load failed: {e}")  # noqa: B904, EM102, TRY003

    def save(self, key: str, object: Any) -> None:  # noqa: A002, ANN401
        """Serialize and save a value to Redis storage.

        Args:
            key: Storage key to write.
            object: JSON-serializable value to store.

        Raises:
            StorageError: If serialization or Redis write fails.
        """
        try:
            object_str = json.dumps(object)
            self._redis.set(key, object_str)
        except Exception as e:  # noqa: BLE001
            raise StorageError(f"Redis save failed: {e}")  # noqa: B904, EM102, TRY003

    def delete(self, key: str) -> None:
        """Delete a key from Redis storage.

        Args:
            key: Storage key to delete.

        Raises:
            StorageError: If the delete operation fails.
        """
        try:
            self._redis.delete(key)
        except Exception as e:  # noqa: BLE001
            raise StorageError(f"Redis delete failed: {e}")  # noqa: B904, EM102, TRY003
