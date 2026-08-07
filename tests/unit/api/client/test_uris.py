import pytest

from signalbot import SignalAPI
from signalbot.api.client.attachments import AttachmentsURIs
from signalbot.api.client.base import BaseURIs
from signalbot.api.client.contacts import ContactsURIs
from signalbot.api.client.general import GeneralURIs
from signalbot.api.client.groups import GroupsURIs
from signalbot.api.client.messages import MessagesURIs
from signalbot.api.client.polls import PollsURIs
from signalbot.api.client.reactions import ReactionsURIs
from signalbot.api.client.receipts import ReceiptsURIs


class TestURIs:
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"
    group_id = "group.OyZzqio1xDmYiLsQ1VsqRcUFOU4tK2TcECmYt2KeozHJwglMBHAPS7jlkrm="

    @pytest.fixture(autouse=True)
    def _use_signal_api(self, signal_api: SignalAPI) -> None:
        self.signal_api = signal_api

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

        base.use_https = False

        assert contacts_uris.contacts_uri().startswith("http://")
        assert groups_uris.groups_uri().startswith("http://")
