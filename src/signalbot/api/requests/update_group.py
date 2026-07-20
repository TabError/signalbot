from __future__ import annotations

from typing import Any

from anyio import Path
from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    SerializerFunctionWrapHandler,
    model_serializer,
)

from signalbot.api.generated.api.group_link import GroupLink
from signalbot.api.generated.data.group_permissions import GroupPermissions
from signalbot.utils.attachment_base64 import attachment_to_base64
from signalbot.utils.pydantic_anyio_path import PydanticPath


class UpdateGroupRequest(BaseModel):
    """
    UpdateGroupRequest for updating a group.

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

    @model_serializer(mode="wrap")
    def serialize_model(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        payload: dict[str, Any] = handler(self)
        if self.avatar is not None:
            base64_avatar = payload.get("avatar")
            if isinstance(self.avatar, Path):
                base64_avatar = attachment_to_base64(self.avatar)
            payload["base64_avatar"] = base64_avatar
            payload.pop("avatar", None)

        return payload
