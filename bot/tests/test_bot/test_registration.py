from ...__main__ import callback_register, wake_up
from ...messages import SUCCESSFUL_REGISTRATION, ALREADY_REGISTERED, UNSUCCESSFUL_REGISTRATION


def test_handle_start(monkeypatch, fake_message_factory, mock_send_message):
    fake_message = fake_message_factory(chat_id=12345, text="/start")
    wake_up(fake_message)

    assert len(mock_send_message) == 1
    _, _, markup = mock_send_message[0]
    for row in markup.keyboard:
        for button in row:
            assert button.callback_data == "Register"


def test_handle_register_successful_registration(mock_send_message, fake_callback_query_factory, mock_get_data_info_negative, mock_post_data_info_positive):
    fake_call = fake_callback_query_factory(chat_id=12345, callback_data="Register")
    
    callback_register(fake_call)
    
    assert len(mock_send_message) == 2
    _, msg_text, _ = mock_send_message[0]
    assert msg_text == SUCCESSFUL_REGISTRATION
    _, _, markup = mock_send_message[1]
    for row in markup.keyboard:
        for button in row:
            assert button.callback_data == "Upload receipt"


def test_handle_register_already_registered(monkeypatch, fake_callback_query_factory, mock_get_data_info_positive, mock_send_message):
    fake_call = fake_callback_query_factory(chat_id=12345, callback_data="Register")
    
    callback_register(fake_call)
    
    assert len(mock_send_message) == 2
    _, msg_text, _ = mock_send_message[0]
    assert msg_text == ALREADY_REGISTERED
    _, _, markup = mock_send_message[1]
    for row in markup.keyboard:
        for button in row:
            assert button.callback_data == "Upload receipt"


def test_handle_register_unsuccessful_registration(monkeypatch, fake_callback_query_factory, mock_send_message, mock_get_data_info_negative, mock_post_data_info_negative):
    fake_call = fake_callback_query_factory(chat_id=12345, callback_data="Register")
    
    callback_register(fake_call)
    
    assert len(mock_send_message) == 1
    _, msg_text, _ = mock_send_message[0]
    assert msg_text == UNSUCCESSFUL_REGISTRATION
