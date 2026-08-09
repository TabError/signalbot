import pytest

from signalbot._client.attachments import AttachmentsURIs
from signalbot._client.base import BaseURIs
from signalbot._client.contacts import ContactsURIs
from signalbot._client.general import GeneralURIs
from signalbot._client.groups import GroupsURIs
from signalbot._client.messages import MessagesURIs
from signalbot._client.polls import PollsURIs
from signalbot._client.reactions import ReactionsURIs
from signalbot._client.receipts import ReceiptsURIs
from signalbot.client import SignalAPI
from tests.conftest import GROUP_ID, PHONE_NUMBER, SIGNAL_SERVICE


def test_receive_uri(signal_api: SignalAPI):
    expected_uri = f"wss://{SIGNAL_SERVICE}/v1/receive/{PHONE_NUMBER}"
    assert signal_api.messages._uris.receive_ws_uri() == expected_uri


def test_send_uri(signal_api: SignalAPI):
    expected_uri = f"https://{SIGNAL_SERVICE}/v2/send"
    assert signal_api.messages._uris.send_uri() == expected_uri


def test_poll_uri(signal_api: SignalAPI):
    expected_uri = f"https://{SIGNAL_SERVICE}/v1/polls/{PHONE_NUMBER}"
    assert signal_api.polls._uris.poll_uri() == expected_uri


def test_attachment_uri(signal_api: SignalAPI):
    expected_uri = f"https://{SIGNAL_SERVICE}/v1/attachments"
    assert signal_api.attachments._uris.attachment_uri() == expected_uri


def test_groups_uri(signal_api: SignalAPI):
    expected_uri = f"https://{SIGNAL_SERVICE}/v1/groups/{PHONE_NUMBER}"
    assert signal_api.groups._uris.groups_uri() == expected_uri


def test_group_id_uri(signal_api: SignalAPI):
    expected_uri = f"https://{SIGNAL_SERVICE}/v1/groups/{PHONE_NUMBER}/{GROUP_ID}"
    assert signal_api.groups._uris.group_id_uri(GROUP_ID) == expected_uri


def test_contacts_uri(signal_api: SignalAPI):
    expected_uri = f"https://{SIGNAL_SERVICE}/v1/contacts/{PHONE_NUMBER}"
    assert signal_api.contacts._uris.contacts_uri() == expected_uri


def test_react_uri(signal_api: SignalAPI):
    expected_uri = f"https://{SIGNAL_SERVICE}/v1/reactions/{PHONE_NUMBER}"
    assert signal_api.reactions._uris.react_uri() == expected_uri


def test_receipts_uri(signal_api: SignalAPI):
    expected_uri = f"https://{SIGNAL_SERVICE}/v1/receipts/{PHONE_NUMBER}"
    assert signal_api.receipts._uris.receipts_uri() == expected_uri


def test_typing_indicator_uri(signal_api: SignalAPI):
    expected_uri = f"https://{SIGNAL_SERVICE}/v1/typing-indicator/{PHONE_NUMBER}"
    assert signal_api.messages._uris.typing_indicator_uri() == expected_uri


def test_remote_delete_uri(signal_api: SignalAPI):
    expected_uri = f"https://{SIGNAL_SERVICE}/v1/remote-delete/{PHONE_NUMBER}"
    assert signal_api.messages._uris.remote_delete_uri() == expected_uri


def test_health_check_uri(signal_api: SignalAPI):
    expected_uri = f"https://{SIGNAL_SERVICE}/v1/health"
    assert signal_api.general._uris.health_check_uri() == expected_uri


def test_about_uri(signal_api: SignalAPI):
    expected_uri = f"https://{SIGNAL_SERVICE}/v1/about"
    assert signal_api.general._uris.about_uri() == expected_uri


class TestURIsComposition:
    """Each per-tag `*URIs` class composes a `BaseURIs` (passed into its
    constructor) rather than inheriting from it, so it only ever needs that
    one object to build its URIs — no reliance on being combined with other
    `*URIs` classes via multiple inheritance.
    """

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
        base = BaseURIs(SIGNAL_SERVICE, PHONE_NUMBER)
        uris = uris_class(base)
        expected = (
            f"{scheme}://{SIGNAL_SERVICE}{path.format(phone_number=PHONE_NUMBER)}"
        )
        assert getattr(uris, method_name)() == expected

    def test_uris_respect_use_https_false(self):
        base = BaseURIs(SIGNAL_SERVICE, PHONE_NUMBER, use_https=False)
        uris = ContactsURIs(base)
        assert uris.contacts_uri().startswith("http://")

    def test_sections_sharing_one_base_see_the_same_use_https(self):
        base = BaseURIs(SIGNAL_SERVICE, PHONE_NUMBER, use_https=True)
        contacts_uris = ContactsURIs(base)
        groups_uris = GroupsURIs(base)

        assert contacts_uris.contacts_uri().startswith("https://")
        assert groups_uris.groups_uri().startswith("https://")

        base.use_https = False

        assert contacts_uris.contacts_uri().startswith("http://")
        assert groups_uris.groups_uri().startswith("http://")
