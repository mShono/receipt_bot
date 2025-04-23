import os
from .mocks import FakePhotoMessage
from ...__main__ import handle_receipt_photo
from ...messages import SUCCESSFUL_RECOGNITION
from ...state import UserContext


def test_handle_receipt_photo_with_photo(monkeypatch, mock_send_message, mock_get_data_info):
    monkeypatch.chdir(os.getcwd())
    fake_photo_msg = FakePhotoMessage(chat_id=42, file_id="PHOTO123")
    test_filepath = os.path.join(os.getcwd(), "test_receipts", "test_recognised_receipt.json")
    monkeypatch.setattr(
        "bot.__main__.recognition_turbo", 
        lambda file_name: test_filepath
    )
    handle_receipt_photo(fake_photo_msg)

    assert mock_send_message
    chat_id, text, _ = mock_send_message[-1]
    context = UserContext[42]
    assert context.products_present_in_database == [{"name": "Eggs", "price": 3.14, "id": 1}, {"name": "Apples", "price": 3.12, "id": 2}]
    assert context.products_absent_in_database == [{"name": "Tea", "price": 114}, {"name": "Coffee", "price": 550}]
    assert chat_id == 42
    assert text == SUCCESSFUL_RECOGNITION

