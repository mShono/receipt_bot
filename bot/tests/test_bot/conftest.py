import os
import pytest
from .mocks import FakeChat, FakeMessage, FakeCallbackQuery, FakePhotoMessage
from ...state import Context, UserContext

from telebot import apihelper, util, types


def fake_request_sender(method, url, **kwargs):
    response_json = '{"ok": true, "result": {' \
    '"message_id": 1, ' \
    '"chat": {"id": 12345, "type": "private"}, ' \
    '"date": 1234567890, ' \
    '"text": "Fake response"}}'
    return util.CustomRequestResponse(response_json)


@pytest.fixture(autouse=True)
def disable_real_requests(monkeypatch):
    monkeypatch.setattr(apihelper, "CUSTOM_REQUEST_SENDER", fake_request_sender)


@pytest.fixture
def real_image_bytes():
    path = os.path.join(os.getcwd(), "test_receipts", "K_market_2025-03-18_2.jpg")
    with open(path, "rb") as f:
        return f.read()


@pytest.fixture(autouse=True)
def disable_file_requests(monkeypatch, real_image_bytes):
    def fake_get_file(file_id):
        return types.File(
            file_id=file_id,
            file_unique_id="unique-"+file_id,
            file_path=os.path.join(os.getcwd(), "test_receipts", "K_market_2025-03-18_2.jpg")
        )

    def fake_download_file(path):
        return real_image_bytes

    monkeypatch.setattr("bot.__main__.bot.get_file", fake_get_file)
    monkeypatch.setattr("bot.__main__.bot.download_file", fake_download_file)


@pytest.fixture(autouse=True)
def isolate_context():
    UserContext.clear()
    yield
    UserContext.clear()


@pytest.fixture
def fake_context():
    context = Context()
    context.chat_id = 42
    context.stage = "products_present_in_database"
    eggs = {"name": "Eggs", "price": 100}
    tea = {"name":"Tea",  "price":200}
    context.products_present_in_database = [eggs]
    context.products_absent_in_database = [tea]
    UserContext[42] = context
    return context


@pytest.fixture
def fake_message_factory():
    def _factory(chat_id=12345, text="/start"):
        return FakeMessage(chat_id, text)
    return _factory


@pytest.fixture
def fake_callback_query_factory():
    def _factory(chat_id=12345, callback_data="Register", username="tester", first_name="Test", last_name="User"):
        return FakeCallbackQuery(chat_id, callback_data, username=username, first_name=first_name, last_name=last_name)
    return _factory


@pytest.fixture
def mock_get_data_info_positive(monkeypatch):
    def fake_get_data_info_positive(endpoint, data):
        if endpoint == "users":
            return True, {
                "chat_id": 12345,
                "username": data,
                "first_name": "Test",
                "last_name": "User",
            }
        return
    monkeypatch.setattr("bot.bot_utils.get_data_info", fake_get_data_info_positive)
    return fake_get_data_info_positive


@pytest.fixture
def mock_get_data_info_negative(monkeypatch):
    def fake_data_info_negative(endpoint, data):
        return False, None
    monkeypatch.setattr("bot.bot_utils.get_data_info", fake_data_info_negative)
    return fake_data_info_negative


@pytest.fixture
def mock_get_data_info(monkeypatch, request):
    data_map = request.param
    def fake_get_data_info(endpoint, data):
        return data_map.get(data, (False, None))
    monkeypatch.setattr("bot.bot_utils.get_data_info", fake_get_data_info)
    return fake_get_data_info


@pytest.fixture
def mock_post_data_info_positive(monkeypatch):
    def fake_post_data_info_positive(endpoint, data):
        if endpoint == "users":
            return True, 1
        return
    monkeypatch.setattr("bot.bot_utils.post_data_info", fake_post_data_info_positive)
    return fake_post_data_info_positive


@pytest.fixture
def mock_post_data_info_negative(monkeypatch):
    def fake_data_info_negative(endpoint, data):
        return False, None
    monkeypatch.setattr("bot.bot_utils.post_data_info", fake_data_info_negative)
    return fake_data_info_negative


@pytest.fixture
def mock_send_message(monkeypatch):
    sent_messages = []
    def fake_send_message(chat_id, text, reply_markup=None):
        sent_messages.append((chat_id, text, reply_markup))
        return {"ok": True, "result": {
            "message_id": 1,
            "chat": {"id": chat_id, "type": "private"},
            "date": 1234567890,
            "text": text
            }
        }
    monkeypatch.setattr("bot.__main__.bot.send_message", fake_send_message)
    monkeypatch.setattr("bot.messages.bot.send_message", fake_send_message)
    return sent_messages


@pytest.fixture
def mock_photo_message():
    return FakePhotoMessage(chat_id=42, file_id="PHOTO123")


@pytest.fixture
def mock_buttons():
    return object()


@pytest.fixture
def captured_calls(monkeypatch, mock_buttons):
    calls = []
    def fake_send_reply_markup_message(chat, text, markup, **kwargs):
        calls.append((chat.id, text, markup, kwargs))
    monkeypatch.setattr("bot.bot_utils.send_reply_markup_message", fake_send_reply_markup_message)

    monkeypatch.setattr("bot.bot_utils.price_name_buttons", lambda ctx: mock_buttons)
    return calls


@pytest.fixture
def captured_register_handler(monkeypatch):
    captured = {}
    def fake_register_next_step_handler(msg, handler):
        captured['message'] = msg
        captured['handler'] = handler
    monkeypatch.setattr("bot.__main__.bot.register_next_step_handler",
                        fake_register_next_step_handler)
    return captured