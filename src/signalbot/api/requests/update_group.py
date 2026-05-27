from pydantic import Field

from signalbot.api.generated import UpdateGroupRequest as _UpdateGroupRequest


class UpdateGroupRequest(_UpdateGroupRequest):
    group_id_or_name: str = Field(exclude=True)
