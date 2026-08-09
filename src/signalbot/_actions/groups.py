from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.errors import SignalBotError

if TYPE_CHECKING:
    import logging

    from signalbot.client import SignalAPI
    from signalbot.groups import GroupRegistry, UpdateGroup


class GroupActions:
    """Update a `SignalBot`'s groups. See `bot.groups` for the read-only group cache
    used to resolve group ids and names.
    """

    def __init__(
        self,
        signal: SignalAPI,
        groups: GroupRegistry,
        logger: logging.Logger,
    ) -> None:
        self._signal = signal
        self._groups = groups
        self._logger = logger

    async def update(self, update_group: UpdateGroup) -> None:
        """Update a group's metadata.

        Args:
            update_group: Group update payload.
        """
        group_id = self._groups.resolve(update_group.group_id_or_name)
        if group_id is None:
            raise SignalBotError.cannot_resolve_recipient()

        wire_request = await update_group.to_generated()
        await self._signal.groups.update(group_id, wire_request)
