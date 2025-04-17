import os
import pytest
from telebot import apihelper, TeleBot, util
from telebot.types import Chat, Message
from .mocks import FakeChat, FakeMessage
from ...__main__ import callback_register, wake_up
from ...messages import SUCCESSFUL_REGISTRATION, ALREADY_REGISTERED, UNSUCCESSFUL_REGISTRATION


def test_handle_start(monkeypatch, fake_message_factory):
    sent_messages = []

    def fake_send_message(chat_id, text, reply_markup=None):
        sent_messages.append((chat_id, text, reply_markup))
        return {"ok": True, "result": {"chat": {"id": chat_id}, "text": text}}

    monkeypatch.setattr("bot.__main__.bot.send_message", fake_send_message)

    fake_message = fake_message_factory(chat_id=12345, text="/start")
    wake_up(fake_message)

    assert len(sent_messages) == 1
    _, _, markup = sent_messages[0]
    for row in markup.keyboard:
        for button in row:
            assert button.callback_data == "Register"


def test_handle_register_successful_registration(mock_fake_send_message, fake_callback_query_factory, mock_get_data_info_negative, mock_post_data_info_positive):
    fake_call = fake_callback_query_factory(chat_id=12345, callback_data="Register")
    
    callback_register(fake_call)
    
    assert len(mock_fake_send_message) == 2
    _, msg_text, _ = mock_fake_send_message[0]
    assert msg_text == SUCCESSFUL_REGISTRATION
    _, _, markup = mock_fake_send_message[1]
    for row in markup.keyboard:
        for button in row:
            assert button.callback_data == "Upload receipt"


def test_handle_register_already_registered(monkeypatch, fake_callback_query_factory, mock_post_data_info_positive, mock_fake_send_message):
    fake_call = fake_callback_query_factory(chat_id=12345, callback_data="Register")
    
    callback_register(fake_call)
    
    assert len(mock_fake_send_message) == 2
    _, msg_text, _ = mock_fake_send_message[0]
    assert msg_text == ALREADY_REGISTERED
    _, _, markup = mock_fake_send_message[1]
    for row in markup.keyboard:
        for button in row:
            assert button.callback_data == "Upload receipt"


def test_handle_register_unsuccessful_registration(monkeypatch, fake_callback_query_factory, mock_fake_send_message, mock_get_data_info_negative, mock_post_data_info_negative):
    fake_call = fake_callback_query_factory(chat_id=12345, callback_data="Register")
    
    callback_register(fake_call)
    
    assert len(mock_fake_send_message) == 1
    _, msg_text, _ = mock_fake_send_message[0]
    assert msg_text == UNSUCCESSFUL_REGISTRATION
