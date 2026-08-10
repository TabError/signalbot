from collections.abc import Callable

from pytest_mock import MockType

from signalbot._client import SignalAPI
from signalbot._generated import Receipt, ReceiptType
from tests.conftest import PHONE_NUMBER
from tests.unit.client.conftest import HTTP_OK


async def test_send(
    signal_api: SignalAPI, mock_json_response: Callable[[str, dict | list], MockType]
):
    mock = mock_json_response("post", {})

    request = Receipt(
        receipt_type=ReceiptType.READ,
        recipient=PHONE_NUMBER,
        timestamp=1638715559464,
    )
    resp = await signal_api.receipts.send(request)

    assert mock.call_count == 1
    assert resp.status == HTTP_OK
