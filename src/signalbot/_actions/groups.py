from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.errors import SignalBotError

if TYPE_CHECKING:
    import logging

    from signalbot.client import SignalAPI
    from signalbot.groups import GroupRegistry, UpdateGroup


class GroupActions:
    """Update a `SignalBot`'s groups, attached as `bot.groups.actions`. See
    `bot.groups` for the read-only group cache used to resolve group ids and names.
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

    async def update(self, update_group: UpdateGroup, group_id_or_name: str) -> None:
        """Update a group's metadata.

        Args:
            update_group: Group update payload.
            group_id_or_name: The group to update.
        """
        group_id = self._groups.resolve(group_id_or_name)
        if group_id is None:
            raise SignalBotError.cannot_resolve_recipient()

        wire_request = await update_group.to_generated()
        await self._signal.groups.update(wire_request, group_id)
