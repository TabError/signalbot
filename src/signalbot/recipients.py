from __future__ import annotations

import re
import uuid
from typing import TYPE_CHECKING

import phonenumbers

from signalbot.errors import SignalBotError

if TYPE_CHECKING:
    from signalbot.groups import GroupRegistry


class RecipientResolver:
    """Resolves a phone number, UUID, username, or group ID/name into the
    UUID or group internal ID.
    """

    def __init__(self, groups: GroupRegistry) -> None:
        self._groups = groups

    def resolve(self, recipient: str) -> str:
        if self._is_phone_number(recipient):
            return recipient

        if self._is_valid_uuid(recipient):
            return recipient

        if self._is_username(recipient):
            return recipient

        group_id = self._groups.resolve(recipient)
        if group_id is not None:
            return group_id

        raise SignalBotError("Cannot resolve recipient.")  # noqa: EM101, TRY003

    def _is_phone_number(self, phone_number: str) -> bool:
        try:
            parsed_number = phonenumbers.parse(phone_number, region=None)
            return phonenumbers.is_valid_number(parsed_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return False

    def _is_valid_uuid(self, recipient_uuid: str) -> bool:
        try:
            uuid.UUID(str(recipient_uuid))
            return True  # noqa: TRY300
        except ValueError:
            return False

    def _is_username(self, recipient_username: str) -> bool:  # noqa: PLR0911
        """
        Check if username has correct format, as described in
        https://support.signal.org/hc/en-us/articles/6712070553754-Phone-Number-Privacy-and-Usernames#username_req
        Additionally, cannot have more than 9 digits and the digits cannot be 00.
        """
        split_username = recipient_username.split(".")
        if len(split_username) == 2:  # noqa: PLR2004
            characters = split_username[0]
            digits = split_username[1]
            if len(characters) < 3 or len(characters) > 32:  # noqa: PLR2004
                return False
            if not re.match(r"^[A-Za-z\d_]+$", characters):
                return False
            if len(digits) < 2 or len(digits) > 9:  # noqa: PLR2004
                return False
            try:
                digits = int(digits)
                if digits == 0:  # noqa: SIM103
                    return False
                return True  # noqa: TRY300
            except ValueError:
                return False
        else:
            return False
