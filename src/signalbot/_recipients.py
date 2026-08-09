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
    UUID or group ID.
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

        raise SignalBotError.cannot_resolve_recipient()

    def _is_phone_number(self, phone_number: str) -> bool:
        try:
            parsed_number = phonenumbers.parse(phone_number, region=None)
            return phonenumbers.is_valid_number(parsed_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return False

    def _is_valid_uuid(self, recipient_uuid: str) -> bool:
        try:
            uuid.UUID(str(recipient_uuid))
        except ValueError:
            return False
        else:
            return True

    _USERNAME_PARTS = 2
    _MIN_USERNAME_LENGTH = 3
    _MAX_USERNAME_LENGTH = 32
    _MIN_DISCRIMINATOR_DIGITS = 2
    _MAX_DISCRIMINATOR_DIGITS = 9

    def _is_username(self, recipient_username: str) -> bool:
        """
        Check if username has correct format, as described in
        https://support.signal.org/hc/en-us/articles/6712070553754-Phone-Number-Privacy-and-Usernames#username_req
        Additionally, cannot have more than 9 digits and the digits cannot be 00.
        """
        split_username = recipient_username.split(".")
        if len(split_username) != self._USERNAME_PARTS:
            return False

        characters, digits = split_username
        min_len, max_len = self._MIN_USERNAME_LENGTH, self._MAX_USERNAME_LENGTH
        if not min_len <= len(characters) <= max_len:
            return False
        if not re.match(r"^[A-Za-z\d_]+$", characters):
            return False
        min_digits, max_digits = (
            self._MIN_DISCRIMINATOR_DIGITS,
            self._MAX_DISCRIMINATOR_DIGITS,
        )
        if not min_digits <= len(digits) <= max_digits:
            return False

        try:
            discriminator = int(digits)
        except ValueError:
            return False

        return discriminator != 0
