from signalbot._generated import GroupEntry as GeneratedGroupEntry
from signalbot.groups.group_permissions import GroupPermissions


class GroupEntry(GeneratedGroupEntry):
    """A group the bot is a member of, as returned by `GroupRegistry`."""

    # Additive: GroupPermissions is a strict superset of the generated type it
    # wraps, so this narrowing is sound; pydantic validates it on construction.
    permissions: GroupPermissions  # pyright: ignore[reportIncompatibleVariableOverride]
