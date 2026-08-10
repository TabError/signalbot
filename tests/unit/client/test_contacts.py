from collections.abc import Callable

from pytest_mock import MockType

from signalbot._client import SignalAPI
from signalbot.contacts import UpdateContact
from tests.conftest import PHONE_NUMBER


async def test_update_contact(
    signal_api: SignalAPI, mock_json_response: Callable[[str, dict | list], MockType]
):
    mock = mock_json_response("put", {})

    update_contact = UpdateContact(name="Bob")
    await signal_api.contacts.update(update_contact.to_generated(PHONE_NUMBER))

    assert mock.call_count == 1
