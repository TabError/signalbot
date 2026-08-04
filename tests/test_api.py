import base64

import aiohttp
import pytest
from pytest_mock import MockerFixture, MockType

from signalbot import ConnectionMode, SignalAPI
from signalbot.api import generated
from signalbot.api.client.attachments import AttachmentsURIs
from signalbot.api.client.base import HEALTH_CHECK_GOOD_STATUS, BaseURIs
from signalbot.api.client.contacts import ContactsURIs
from signalbot.api.client.general import GeneralURIs, HealthCheckError
from signalbot.api.client.groups import GroupsURIs
from signalbot.api.client.messages import MessagesURIs
from signalbot.api.client.polls import PollsURIs
from signalbot.api.client.reactions import ReactionsURIs
from signalbot.api.client.receipts import ReceiptsURIs
from signalbot.api.generated import (
    About,
    AddMembers,
    CreatePollRequest,
    EditGroup,
    GroupEntry,
    GroupPermissions,
    RemoteDeleteRequest,
    SendMessages,
    SendMessageV2,
)
from signalbot.api.generated.api import (
    Receipt,
    ReceiptType,
    SendReactionRequest,
    TypingIndicatorRequest,
)
from signalbot.api.incoming import Attachment
from signalbot.api.outgoing import UpdateContact
from signalbot.auth import Authentication, BasicAuthentication, BearerAuthentication

HTTP_OK = 200


class TestAPI:
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    group_id = "group.OyZzqio1xDmYiLsQ1VsqRcUFOU4tK2TcECmYt2KeozHJwglMBHAPS7jlkrm="

    @pytest.fixture(autouse=True)
    def setup(self):
        self.signal_api = SignalAPI(self.signal_service, self.phone_number)

    @pytest.mark.asyncio
    async def test_send(self, mocker: MockerFixture):
        expected_timestamp = "1638715559464"
        self._mock_json_response(mocker, "post", {"timestamp": expected_timestamp})

        data_message = SendMessageV2(
            message="Hello World!",
            number=self.phone_number,
            recipients=[self.group_id],
        )
        resp = await self.signal_api.messages.send(data_message)

        assert resp.timestamp == expected_timestamp

    @pytest.mark.asyncio
    async def test_poll(self, mocker: MockerFixture):
        self._mock_json_response(mocker, "post", {"timestamp": "1774791959123"})

        recipient = self.group_id
        question = "How much is the fish?"
        answers = ["hyper hyper", "3,80 DM"]
        create_poll_request = CreatePollRequest(
            recipient=recipient,
            question=question,
            answers=answers,
            allow_multiple_selections=False,
        )
        resp = await self.signal_api.polls.poll(create_poll_request)

        assert resp.timestamp == "1774791959123"

    @pytest.mark.asyncio
    async def test_receive(self, mocker: MockerFixture):
        message1 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 1","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group1","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa: E501
        message2 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 2","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group1","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa: E501
        messages = [message1, message2]
        mock_iterator = mocker.AsyncMock()
        mock_iterator.__aiter__.return_value = messages
        mock = mocker.patch("websockets.connect")
        mock.return_value.__aenter__.return_value = mock_iterator

        results = [
            raw_message async for raw_message in self.signal_api.messages.receive()
        ]

        assert len(results) == len(messages)
        for i, _ in enumerate(results):
            assert messages[i] == results[i]

    def test_receive_uri(self):
        expected_uri = f"wss://{self.signal_service}/v1/receive/{self.phone_number}"
        actual_uri = self.signal_api.messages._uris.receive_ws_uri()
        assert actual_uri == expected_uri

    def test_send_uri(self):
        expected_uri = f"https://{self.signal_service}/v2/send"
        actual_uri = self.signal_api.messages._uris.send_uri()
        assert actual_uri == expected_uri

    def test_poll_uri(self):
        expected_uri = f"https://{self.signal_service}/v1/polls/{self.phone_number}"
        actual_uri = self.signal_api.polls._uris.poll_uri()
        assert actual_uri == expected_uri

    def test_attachment_uri(self):
        expected_uri = f"https://{self.signal_service}/v1/attachments"
        actual_uri = self.signal_api.attachments._uris.attachment_uri()
        assert actual_uri == expected_uri

    def test_groups_uri(self):
        expected_uri = f"https://{self.signal_service}/v1/groups/{self.phone_number}"
        actual_uri = self.signal_api.groups._uris.groups_uri()
        assert actual_uri == expected_uri

    def test_group_id_uri(self):
        expected_uri = (
            f"https://{self.signal_service}/v1/groups/{self.phone_number}"
            f"/{self.group_id}"
        )
        actual_uri = self.signal_api.groups._uris.group_id_uri(self.group_id)
        assert actual_uri == expected_uri

    def test_contacts_uri(self):
        expected_uri = f"https://{self.signal_service}/v1/contacts/{self.phone_number}"
        actual_uri = self.signal_api.contacts._uris.contacts_uri()
        assert actual_uri == expected_uri

    def test_react_uri(self):
        expected_uri = f"https://{self.signal_service}/v1/reactions/{self.phone_number}"
        actual_uri = self.signal_api.reactions._uris.react_uri()
        assert actual_uri == expected_uri

    def test_receipts_uri(self):
        expected_uri = f"https://{self.signal_service}/v1/receipts/{self.phone_number}"
        actual_uri = self.signal_api.receipts._uris.receipts_uri()
        assert actual_uri == expected_uri

    def test_typing_indicator_uri(self):
        expected_uri = (
            f"https://{self.signal_service}/v1/typing-indicator/{self.phone_number}"
        )
        actual_uri = self.signal_api.messages._uris.typing_indicator_uri()
        assert actual_uri == expected_uri

    def test_remote_delete_uri(self):
        expected_uri = (
            f"https://{self.signal_service}/v1/remote-delete/{self.phone_number}"
        )
        actual_uri = self.signal_api.messages._uris.remote_delete_uri()
        assert actual_uri == expected_uri

    def test_health_check_uri(self):
        expected_uri = f"https://{self.signal_service}/v1/health"
        actual_uri = self.signal_api.general._uris.health_check_uri()
        assert actual_uri == expected_uri

    def test_about_uri(self):
        expected_uri = f"https://{self.signal_service}/v1/about"
        actual_uri = self.signal_api.general._uris.about_uri()
        assert actual_uri == expected_uri

    def _mock_json_response(
        self, mocker: MockerFixture, verb: str, payload: dict | list
    ) -> MockType:
        mock2 = mocker.AsyncMock()
        mock2.return_value = payload
        mock = mocker.patch(
            f"aiohttp.ClientSession.{verb}", new_callable=mocker.AsyncMock
        )
        mock.return_value = mocker.AsyncMock(
            spec=aiohttp.ClientResponse,
            status=HTTP_OK,
            json=mock2,
        )
        return mock

    @pytest.mark.parametrize(
        ("client_attr", "method_name", "verb", "request_obj"),
        [
            (
                "reactions",
                "react",
                "post",
                SendReactionRequest(
                    reaction="🎉",
                    recipient=group_id,
                    target_author=phone_number,
                    timestamp=1638715559464,
                ),
            ),
            (
                "receipts",
                "receipt",
                "post",
                Receipt(
                    receipt_type=ReceiptType.READ,
                    recipient=phone_number,
                    timestamp=1638715559464,
                ),
            ),
            (
                "messages",
                "start_typing",
                "put",
                TypingIndicatorRequest(recipient=phone_number),
            ),
            (
                "messages",
                "stop_typing",
                "delete",
                TypingIndicatorRequest(recipient=phone_number),
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_raw_response_client_methods(
        self,
        mocker: MockerFixture,
        client_attr: str,
        method_name: str,
        verb: str,
        request_obj: SendReactionRequest | Receipt | TypingIndicatorRequest,
    ):
        mock = self._mock_json_response(mocker, verb, {})

        client = getattr(self.signal_api, client_attr)
        resp = await getattr(client, method_name)(request_obj)

        assert mock.call_count == 1
        assert resp.status == HTTP_OK

    @pytest.mark.asyncio
    async def test_remote_delete(self, mocker: MockerFixture):
        expected_timestamp = "1638715559464"
        self._mock_json_response(mocker, "delete", {"timestamp": expected_timestamp})

        remote_delete_request = RemoteDeleteRequest(
            recipient=self.phone_number, timestamp=1638715559464
        )
        resp = await self.signal_api.messages.remote_delete(remote_delete_request)

        assert resp.timestamp == expected_timestamp

    @pytest.mark.asyncio
    async def test_get_groups(self, mocker: MockerFixture):
        group_entry = GroupEntry(
            admins=[],
            blocked=False,
            description="",
            id=self.group_id,
            internal_id="internal-id",
            invite_link="",
            members=[],
            name="Test",
            pending_invites=[],
            pending_requests=[],
            permissions=GroupPermissions(
                add_members=AddMembers.EVERY_MEMBER,
                edit_group=EditGroup.EVERY_MEMBER,
                send_messages=SendMessages.EVERY_MEMBER,
            ),
        )
        self._mock_json_response(mocker, "get", [group_entry.model_dump(by_alias=True)])

        groups = await self.signal_api.groups.get_groups()

        assert groups == [group_entry]

    @pytest.mark.asyncio
    async def test_get_group(self, mocker: MockerFixture):
        group_entry = GroupEntry(
            admins=[],
            blocked=False,
            description="",
            id=self.group_id,
            internal_id="internal-id",
            invite_link="",
            members=[],
            name="Test",
            pending_invites=[],
            pending_requests=[],
            permissions=GroupPermissions(
                add_members=AddMembers.EVERY_MEMBER,
                edit_group=EditGroup.EVERY_MEMBER,
                send_messages=SendMessages.EVERY_MEMBER,
            ),
        )
        self._mock_json_response(mocker, "get", group_entry.model_dump(by_alias=True))

        group = await self.signal_api.groups.get_group(self.group_id)

        assert group == group_entry

    @pytest.mark.asyncio
    async def test_update_contact(self, mocker: MockerFixture):
        mock = self._mock_json_response(mocker, "put", {})

        update_contact = UpdateContact(recipient=self.phone_number, name="Bob")
        await self.signal_api.contacts.update_contact(update_contact)

        assert mock.call_count == 1

    @pytest.mark.asyncio
    async def test_update_group(self, mocker: MockerFixture):
        mock = self._mock_json_response(mocker, "put", {})

        update_group_request = generated.UpdateGroupRequest(name="New Name")
        await self.signal_api.groups.update_group(self.group_id, update_group_request)

        assert mock.call_count == 1

    @pytest.mark.asyncio
    async def test_download_attachment(self, mocker: MockerFixture):
        mock = mocker.patch("aiohttp.ClientSession.get", new_callable=mocker.AsyncMock)
        content_mock = mocker.AsyncMock()
        content_mock.return_value = b"file content"
        mock.return_value = mocker.AsyncMock(
            spec=aiohttp.ClientResponse,
            status=HTTP_OK,
            content=mocker.Mock(read=content_mock),
        )

        attachment = Attachment(local_filename="my-file.png")
        result = await self.signal_api.attachments.download_attachment(attachment)

        assert result == base64.b64encode(b"file content").decode("utf-8")

    @pytest.mark.asyncio
    async def test_delete_attachment(self, mocker: MockerFixture):
        mock = self._mock_json_response(mocker, "delete", {})

        attachment = Attachment(local_filename="my-file.png")
        await self.signal_api.attachments.delete_attachment(attachment)

        assert mock.call_count == 1

    @pytest.mark.asyncio
    async def test_delete_attachment_without_local_filename_raises(self):
        attachment = Attachment(local_filename=None)

        with pytest.raises(ValueError, match="no local filename"):
            await self.signal_api.attachments.delete_attachment(attachment)

    @pytest.mark.asyncio
    async def test_about(self, mocker: MockerFixture):
        about = About(
            build=1,
            capabilities={},
            mode="json-rpc",
            version="0.97",
            versions=["v1"],
        )
        self._mock_json_response(mocker, "get", about.model_dump(by_alias=True))

        resp = await self.signal_api.general.about()

        assert resp == about

    @pytest.mark.asyncio
    async def test_health_check(self, mocker: MockerFixture):
        mock = mocker.patch("aiohttp.ClientSession.get", new_callable=mocker.AsyncMock)
        mock.return_value = mocker.AsyncMock(
            spec=aiohttp.ClientResponse,
            status=HEALTH_CHECK_GOOD_STATUS,
        )

        resp = await self.signal_api.general.health_check()

        assert mock.call_count == 1
        assert resp is mock.return_value

    @pytest.mark.asyncio
    async def test_check_signal_service_prefers_configured_protocol(
        self, mocker: MockerFixture
    ):
        signal_api = SignalAPI(
            self.signal_service,
            self.phone_number,
            connection_mode=ConnectionMode.HTTP_ONLY,
        )

        health_check_mock = mocker.patch.object(
            signal_api.general, "health_check", new_callable=mocker.AsyncMock
        )
        health_check_mock.return_value = mocker.Mock(status=HEALTH_CHECK_GOOD_STATUS)

        is_healthy = await signal_api.check_signal_service()

        assert is_healthy is True
        assert signal_api._uris.use_https is False

    @pytest.mark.asyncio
    async def test_check_signal_service_https_only_uses_secure_protocol(
        self, mocker: MockerFixture
    ):
        signal_api = SignalAPI(
            self.signal_service,
            self.phone_number,
            connection_mode=ConnectionMode.HTTPS_ONLY,
        )

        health_check_mock = mocker.patch.object(
            signal_api.general, "health_check", new_callable=mocker.AsyncMock
        )
        health_check_mock.return_value = mocker.Mock(status=HEALTH_CHECK_GOOD_STATUS)

        is_healthy = await signal_api.check_signal_service()

        assert is_healthy is True
        assert health_check_mock.call_count == 1
        assert signal_api._uris.use_https is True

    @pytest.mark.asyncio
    async def test_check_signal_service_does_not_fallback_if_protocol_configured(
        self, mocker: MockerFixture
    ):
        signal_api = SignalAPI(
            self.signal_service,
            self.phone_number,
            connection_mode=ConnectionMode.HTTP_ONLY,
        )

        health_check_mock = mocker.patch.object(
            signal_api.general, "health_check", new_callable=mocker.AsyncMock
        )
        health_check_mock.side_effect = HealthCheckError()

        is_healthy = await signal_api.check_signal_service()

        assert is_healthy is False
        assert health_check_mock.call_count == 1
        assert signal_api._uris.use_https is False

    @pytest.mark.asyncio
    async def test_check_signal_service_falls_back_to_other_protocol_in_auto_mode(
        self, mocker: MockerFixture
    ):
        signal_api = SignalAPI(self.signal_service, self.phone_number)

        health_check_mock = mocker.patch.object(
            signal_api.general, "health_check", new_callable=mocker.AsyncMock
        )
        health_check_mock.side_effect = [
            HealthCheckError(),
            mocker.Mock(status=HEALTH_CHECK_GOOD_STATUS),
        ]

        is_healthy = await signal_api.check_signal_service()

        assert is_healthy is True
        assert signal_api._uris.use_https is False

    @pytest.mark.asyncio
    async def test_check_signal_service_auto_succeeds_without_fallback(
        self, mocker: MockerFixture
    ):
        signal_api = SignalAPI(
            self.signal_service,
            self.phone_number,
            connection_mode=ConnectionMode.AUTO,
        )

        health_check_mock = mocker.patch.object(
            signal_api.general, "health_check", new_callable=mocker.AsyncMock
        )
        health_check_mock.return_value = mocker.Mock(status=HEALTH_CHECK_GOOD_STATUS)

        is_healthy = await signal_api.check_signal_service()

        assert is_healthy is True
        assert health_check_mock.call_count == 1
        assert signal_api._uris.use_https is True

    async def _send_with_auth_helper(
        self, mocker: MockerFixture, auth: Authentication | None
    ) -> None:
        signal_api = SignalAPI(self.signal_service, self.phone_number, auth=auth)

        status_code = 201
        mock2 = mocker.AsyncMock()
        mock2.return_value = {"timestamp": "1638715559464"}

        mock_session = mocker.AsyncMock()
        mock_session.post.return_value = mocker.AsyncMock(
            spec=aiohttp.ClientResponse,
            status_code=status_code,
            json=mock2,
        )

        mock = mocker.patch("aiohttp.ClientSession")
        mock.return_value.__aenter__.return_value = mock_session

        data_message = SendMessageV2(
            message="Hello World!",
            number=self.phone_number,
            recipients=[self.group_id],
        )

        resp = await signal_api.messages.send(data_message)

        _, kwargs = mock.call_args

        assert resp.timestamp == "1638715559464"
        return kwargs["headers"].get("Authorization")

    @pytest.mark.asyncio
    async def test_send_with_basic_auth(self, mocker: MockerFixture):
        username = "user"
        password = "pw"  # noqa: S105

        credentials = f"{username}:{password}".encode()
        credential_string = base64.b64encode(credentials).decode("utf-8")

        auth = BasicAuthentication(username=username, password=password)

        auth_header = await self._send_with_auth_helper(mocker, auth)

        assert auth_header == f"Basic {credential_string}"

    @pytest.mark.asyncio
    async def test_send_with_bearer_auth(self, mocker: MockerFixture):
        token = "token"  # noqa: S105

        auth = BearerAuthentication(token=token)

        auth_header = await self._send_with_auth_helper(mocker, auth)

        assert auth_header == f"Bearer {token}"

    @pytest.mark.asyncio
    async def test_send_without_auth(self, mocker: MockerFixture):
        auth_header = await self._send_with_auth_helper(mocker, None)

        assert auth_header is None


class TestURIsComposition:
    """Each per-tag `*URIs` class composes a `BaseURIs` (passed into its
    constructor) rather than inheriting from it, so it only ever needs that
    one object to build its URIs — no reliance on being combined with other
    `*URIs` classes via multiple inheritance.
    """

    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    @pytest.mark.parametrize(
        ("uris_class", "method_name", "scheme", "path"),
        [
            (GeneralURIs, "about_uri", "https", "/v1/about"),
            (GeneralURIs, "health_check_uri", "https", "/v1/health"),
            (MessagesURIs, "send_uri", "https", "/v2/send"),
            (MessagesURIs, "receive_ws_uri", "wss", "/v1/receive/{phone_number}"),
            (GroupsURIs, "groups_uri", "https", "/v1/groups/{phone_number}"),
            (AttachmentsURIs, "attachment_uri", "https", "/v1/attachments"),
            (ContactsURIs, "contacts_uri", "https", "/v1/contacts/{phone_number}"),
            (PollsURIs, "poll_uri", "https", "/v1/polls/{phone_number}"),
            (ReactionsURIs, "react_uri", "https", "/v1/reactions/{phone_number}"),
            (ReceiptsURIs, "receipts_uri", "https", "/v1/receipts/{phone_number}"),
        ],
    )
    def test_uris(
        self,
        uris_class: type,
        method_name: str,
        scheme: str,
        path: str,
    ):
        base = BaseURIs(self.signal_service, self.phone_number)
        uris = uris_class(base)
        expected = (
            f"{scheme}://{self.signal_service}"
            f"{path.format(phone_number=self.phone_number)}"
        )
        assert getattr(uris, method_name)() == expected

    def test_uris_respect_use_https_false(self):
        base = BaseURIs(self.signal_service, self.phone_number, use_https=False)
        uris = ContactsURIs(base)
        assert uris.contacts_uri().startswith("http://")

    def test_sections_sharing_one_base_see_the_same_use_https(self):
        base = BaseURIs(self.signal_service, self.phone_number, use_https=True)
        contacts_uris = ContactsURIs(base)
        groups_uris = GroupsURIs(base)

        assert contacts_uris.contacts_uri().startswith("https://")
        assert groups_uris.groups_uri().startswith("https://")

        base.set_https(False)

        assert contacts_uris.contacts_uri().startswith("http://")
        assert groups_uris.groups_uri().startswith("http://")
