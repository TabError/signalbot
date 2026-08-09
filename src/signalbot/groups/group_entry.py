from signalbot._generated import GroupEntry as GeneratedGroupEntry
from signalbot.groups.group_permissions import GroupPermissions


class GroupEntry(GeneratedGroupEntry):
    """A group the bot is a member of, as returned by `GroupRegistry`."""

    permissions: GroupPermissions
