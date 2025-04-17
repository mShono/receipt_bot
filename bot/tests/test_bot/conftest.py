import pytest
from .mocks import FakeChat, FakeMessage, FakeCallbackQuery

from telebot import apihelper, util


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
    monkeypatch.setattr("bot.bot_utils.post_data_info", fake_get_data_info_positive)
    return fake_get_data_info_positive


@pytest.fixture
def mock_get_data_info_negative(monkeypatch):
    def fake_data_info_negative(endpoint, data):
        return False, None
    monkeypatch.setattr("bot.bot_utils.get_data_info", fake_data_info_negative)
    return fake_data_info_negative


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
def mock_fake_send_message(monkeypatch):
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
