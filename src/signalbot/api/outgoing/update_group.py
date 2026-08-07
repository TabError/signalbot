from __future__ import annotations

from anyio import Path
from pydantic import AliasChoices, BaseModel, Field

from signalbot.api.generated import GroupLink, GroupPermissions, UpdateGroupRequest
from signalbot.utils.attachment_base64 import attachment_to_base64
from signalbot.utils.pydantic_anyio_path import PydanticPath


class UpdateGroup(BaseModel):
    """
    UpdateGroup for updating a group.

    If a field is None, the attribute will not change.

    Attributes:
        group_id_or_name: The group ID or name of the group to update.
        avatar: The new avatar of the group. This can be a Path or a base64 encoded
            string of the image content. Defaults to `None`.
        description: The new description of the group. Defaults to `None`.
        expiration_in_seconds: The new expiration time of the group in seconds.
            Defaults to `None`.
        group_link: Enable or disable joining the group via group link.
            Defaults to `None`.
        name: The new name of the group. Defaults to `None`.
        permissions: The new permissions for the group. Defaults to `None`.
    """

    group_id_or_name: str = Field(exclude=True)
    avatar: PydanticPath | str | None = None
    description: str | None = None
    expiration_in_seconds: int | None = Field(
        default=None,
        serialization_alias="expiration_time",
        validation_alias=AliasChoices("expiration_time", "expiration_in_seconds"),
    )
    group_link: GroupLink | None = None
    name: str | None = None
    permissions: GroupPermissions | None = None

    async def to_generated(self) -> UpdateGroupRequest:
        avatar = self.avatar
        base64_avatar = (
            await attachment_to_base64(avatar) if isinstance(avatar, Path) else avatar
        )
        other_fields = self.model_dump(exclude={"avatar"})
        return UpdateGroupRequest(**other_fields, base64_avatar=base64_avatar)
