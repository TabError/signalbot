from __future__ import annotations

import copy
import re
from collections import defaultdict
from typing import TYPE_CHECKING

from signalbot.errors import SignalBotError

if TYPE_CHECKING:
    import logging
    from collections.abc import Iterator

    from signalbot.api import SignalAPI
    from signalbot.api.generated import GroupEntry
    from signalbot.api.outgoing import UpdateGroup


class GroupRegistry:
    """List like chache of the groups the bot is a member of, with lookup and update
    helpers.
    """

    def __init__(self, signal: SignalAPI, logger: logging.Logger) -> None:
        self._signal = signal
        self._logger = logger

        self._groups: list[GroupEntry] = []
        self._by_id: dict[str, GroupEntry] = {}
        self._by_internal_id: dict[str, GroupEntry] = {}
        self._by_name: defaultdict[str, list[GroupEntry]] = defaultdict(list)

    def __iter__(self) -> Iterator[GroupEntry]:
        return iter(self._groups)

    def __len__(self) -> int:
        return len(self._groups)

    def __getitem__(self, index: int) -> GroupEntry:
        return self._groups[index]

    def get(self, internal_id: str) -> GroupEntry | None:
        if internal_id in self._by_internal_id:
            return copy.deepcopy(self._by_internal_id[internal_id])
        return None

    def _get_internal(self, internal_id: str) -> GroupEntry | None:
        """Look up a group without copying it. For internal callers that only read
        the result and never hand it to user code."""
        return self._by_internal_id.get(internal_id)

    def resolve(self, group_id_or_name: str) -> str | None:
        group = self._by_id.get(group_id_or_name)
        if group is not None:
            return group.id

        if self._is_group_id(group_id_or_name):
            error_msg = f"[Bot] Group with id '{group_id_or_name}' not found. There "
            error_msg += "is a typo in id or the bot is not a member of the group."
            self._logger.warning(error_msg)
            return group_id_or_name

        group = self._by_internal_id.get(group_id_or_name)
        if group is not None:
            return group.id

        group = self._get_by_name(group_id_or_name)
        if group is not None:
            return group.id

        return None

    async def refresh(self) -> None:
        # reset group lookups to avoid stale data
        self._groups = await self._signal.groups.get_groups()

        self._by_id = {}
        self._by_internal_id = {}
        self._by_name = defaultdict(list)
        for group in self._groups:
            self._by_id[group.id] = group
            self._by_internal_id[group.internal_id] = group
            self._by_name[group.name].append(group)

        self._logger.info(f"[Bot] {len(self._groups)} groups detected")  # noqa: G004

    async def refresh_one(self, group_internal_id: str) -> None:
        # look up group that requires update
        group = await self._signal.groups.get_group(
            self._by_internal_id[group_internal_id].id
        )

        current_group_name = self._by_internal_id[group_internal_id].name
        # group name may have been updated
        self._by_name[current_group_name] = [
            g for g in self._by_name[current_group_name] if g.id != group.id
        ]
        self._groups = [
            group if g.internal_id == group_internal_id else g for g in self._groups
        ]
        self._by_id[group.id] = group
        self._by_internal_id[group.internal_id] = group
        self._by_name[group.name].append(group)

        self._logger.info("[Bot] Group updated")

    async def update(self, update_group: UpdateGroup) -> None:
        """Update a group's metadata.

        Args:
            update_group: Group update payload.
        """
        group_id_or_name = self.resolve(update_group.group_id_or_name)
        if group_id_or_name is None:
            raise SignalBotError("Cannot resolve recipient.")  # noqa: EM101, TRY003

        wire_request = await update_group.to_generated()
        await self._signal.groups.update_group(group_id_or_name, wire_request)

    def _get_by_name(self, group_name: str) -> GroupEntry | None:
        groups = self._by_name.get(group_name)
        if groups is not None:
            if len(groups) > 1:
                error_msg = f"[Bot] There is more than one group named '{group_name}',"
                error_msg += " using the first one."
                self._logger.warning(error_msg)
            return groups[0]
        return None

    def _is_group_id(self, group_id: str) -> bool:
        """Check if group_id has the right format, e.g.

              random string                                              length 66
              ↓                                                          ↓
        group.OyZzqio1xDmYiLsQ1VsqRcUFOU4tK2TcECmYt2KeozHJwglMBHAPS7jlkrm=
        ↑                                                                ↑
        prefix                                                           suffix
        """
        if group_id is None:
            return False

        return re.match(r"^group\.[a-zA-Z0-9]{59}=$", group_id)
