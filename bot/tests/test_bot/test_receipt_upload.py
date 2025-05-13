import os
from ...__main__ import handle_receipt_photo
from ...messages import SUCCESSFUL_RECOGNITION, RECOGNIZED_PRODUCTS_MISSING_IN_DATABASE, UNSUCCESSFUL_RECOGNITION
from ...state import UserContext


def run_receipt_test(monkeypatch, mock_photo_message, mock_send_message,
    incoming_data, expected_present, expected_absent, expected_message, test_filepath):
    monkeypatch.setattr(
        "bot.bot_utils.get_data_info",
        lambda endpoint, data: incoming_data.get(data, (False, None))
    )
    monkeypatch.setattr("bot.__main__.recognition_turbo", lambda file_name: test_filepath)
    handle_receipt_photo(mock_photo_message)
    context = UserContext[mock_photo_message.chat.id]
    assert context.products_present_in_database == expected_present
    assert context.products_absent_in_database  == expected_absent
    chat_id, text, _ = mock_send_message[-1]
    assert chat_id == mock_photo_message.chat.id
    assert text == expected_message


def test_handle_receipt_present(monkeypatch, mock_photo_message, mock_send_message):
    incoming_data = {
        "Eggs":   (True,  {"id": 1}),
        "Apples": (True,  {"id": 2}),
        "Tea":    (False, None),
        "Coffee": (False, None),
    }
    test_filepath = os.path.join(os.getcwd(), "test_receipts", "test_recognised_receipt.json")
    run_receipt_test(
        monkeypatch, mock_photo_message, mock_send_message,
        incoming_data,
        expected_present=[{"name":"Eggs","price":100,"id":1}, {"name":"Apples","price":200,"id":2}],
        expected_absent=[{"name":"Tea","price":114},{"name":"Coffee","price":550}],
        expected_message=SUCCESSFUL_RECOGNITION,
        test_filepath=test_filepath
    )


def test_handle_receipt_absent(monkeypatch, mock_photo_message, mock_send_message):
    incoming_data = {k:(False,None) for k in ("Eggs","Apples","Tea","Coffee")}
    test_filepath = os.path.join(os.getcwd(), "test_receipts", "test_recognised_receipt.json")
    run_receipt_test(
        monkeypatch, mock_photo_message, mock_send_message,
        incoming_data,
        expected_present=[],
        expected_absent=[
            {"name":"Eggs","price":3.14},
            {"name":"Apples","price":3.12},
            {"name":"Tea","price":1.14},
            {"name":"Coffee","price":5.50},
        ],
        expected_message=RECOGNIZED_PRODUCTS_MISSING_IN_DATABASE,
        test_filepath=test_filepath
    )


def test_handle_receipt_false(monkeypatch, mock_photo_message, mock_send_message):
    data = {}
    test_filepath = os.path.join(os.getcwd(), "test_receipts", "test_unrecognised_receipt.json")
    run_receipt_test(
        monkeypatch, mock_photo_message, mock_send_message,
        data,
        expected_present=[],
        expected_absent=[],
        expected_message=UNSUCCESSFUL_RECOGNITION,
        test_filepath=test_filepath
    )