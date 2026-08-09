from signalbot._generated import GroupEntry
from signalbot.groups.errors import GetGroupsError, UpdateGroupError
from signalbot.groups.group_update import GroupInfo, GroupUpdate
from signalbot.groups.registry import GroupRegistry
from signalbot.groups.update_group import GroupLink, GroupPermissions, UpdateGroup

__all__ = [
    "GetGroupsError",
    "GroupEntry",
    "GroupInfo",
    "GroupLink",
    "GroupPermissions",
    "GroupRegistry",
    "GroupUpdate",
    "UpdateGroup",
    "UpdateGroupError",
]
