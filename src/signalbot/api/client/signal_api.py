from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.api.client.attachments import AttachmentsClient, AttachmentsURIs
from signalbot.api.client.base import (
    HEALTH_CHECK_GOOD_STATUS,
    BaseURIs,
    ConnectionMode,
    SessionManager,
)
from signalbot.api.client.contacts import ContactsClient, ContactsURIs
from signalbot.api.client.general import GeneralClient, GeneralURIs, HealthCheckError
from signalbot.api.client.groups import GroupsClient, GroupsURIs
from signalbot.api.client.messages import MessagesClient, MessagesURIs
from signalbot.api.client.polls import PollsClient, PollsURIs
from signalbot.api.client.reactions import ReactionsClient, ReactionsURIs
from signalbot.api.client.receipts import ReceiptsClient, ReceiptsURIs

if TYPE_CHECKING:
    from signalbot.auth import Authentication


class SignalAPI:
    """Client for `signal-cli-rest-api`, with one sub-client per API tag.

    Usage:
        signal_api = SignalAPI(signal_service, phone_number)
        await signal_api.messages.send(...)
        await signal_api.groups.get_groups()
        await signal_api.close()
    """

    def __init__(
        self,
        signal_service: str,
        phone_number: str,
        auth: Authentication | None = None,
        download_attachments: bool = True,  # noqa: FBT001, FBT002
        connection_mode: ConnectionMode = ConnectionMode.AUTO,
    ) -> None:
        self.phone_number = phone_number
        self.auth = auth
        self.connection_mode = connection_mode
        self.download_attachments = download_attachments

        use_https = connection_mode in (ConnectionMode.HTTPS_ONLY, ConnectionMode.AUTO)
        # Shared mutable state (notably `use_https`, toggled by
        # check_signal_service) that every section's URIs object composes.
        self._uris = BaseURIs(
            signal_service=signal_service,
            phone_number=phone_number,
            use_https=use_https,
        )

        self._sessions = SessionManager()

        self.general = GeneralClient(GeneralURIs(self._uris), auth, self._sessions)
        self.messages = MessagesClient(MessagesURIs(self._uris), auth, self._sessions)
        self.groups = GroupsClient(GroupsURIs(self._uris), auth, self._sessions)
        self.attachments = AttachmentsClient(
            AttachmentsURIs(self._uris), auth, self._sessions
        )
        self.contacts = ContactsClient(ContactsURIs(self._uris), auth, self._sessions)
        self.polls = PollsClient(PollsURIs(self._uris), auth, self._sessions)
        self.reactions = ReactionsClient(
            ReactionsURIs(self._uris), auth, self._sessions
        )
        self.receipts = ReceiptsClient(ReceiptsURIs(self._uris), auth, self._sessions)

    async def close(self) -> None:
        """Close the shared HTTP session. Called when the bot is shutting down."""
        await self._sessions.close()

    async def check_signal_service(self) -> bool:
        async def is_available() -> bool:
            try:
                return (
                    await self.general.health_check()
                ).status == HEALTH_CHECK_GOOD_STATUS
            except HealthCheckError:
                return False

        if self.connection_mode != ConnectionMode.AUTO:
            # use_https is already set according to the connection mode
            return await is_available()

        self._uris.set_https(True)
        if await is_available():
            return True

        self._uris.set_https(False)
        return await is_available()
