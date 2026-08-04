from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.actions.base import BotActionsBase

if TYPE_CHECKING:
    from signalbot.api.generated import About


class GeneralActions(BotActionsBase):
    async def about(self) -> About:
        """Return the signal-cli-rest-api about information."""
        return await self._signal.general.about()
