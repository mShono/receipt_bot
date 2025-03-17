import logging
from logging import StreamHandler

import os
from dotenv import load_dotenv
import requests

from telebot import TeleBot, types
import messages

import django
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.views.decorators.csrf import csrf_exempt


settings.configure()
django.setup()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
handler = StreamHandler()
logger.addHandler(handler)

load_dotenv()
DJANGO_API_URL = os.getenv("DJANGO_API_URL")
bot = TeleBot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

headers = {
    "Authorization": f"Token {os.getenv("DJANGO_BOT_TOKEN")}",
    "Content-Type": "application/json",
}

user_states = {}
user_info = {}

@bot.message_handler(commands=["start"])
def wake_up(message):
    chat = message.chat
    name = chat.first_name
    last_name = chat.last_name
    markup = types.InlineKeyboardMarkup()
    register_url_button = types.InlineKeyboardButton("Register", url="https://ya.ru")
    register_callback_button = types.InlineKeyboardButton("Register", callback_data="Register")
    markup.add(register_callback_button)
    bot.send_message(
        chat_id=chat.id,
        text=messages.INVITATION_TO_REGISTER,
        reply_markup=markup)
    logging.info("Invitation for registration sent")
    # keyboard = types.ReplyKeyboardMarkup()
    # button_newcat = types.KeyboardButton('/Register')
    # keyboard.add(button_newcat)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat = call.message.chat
    if call.message:
        if call.data == "Register":
            user_states[chat.id] = "awaiting_email"
            bot.send_message(
                chat.id,
                messages.WARNING_BEFORE_EMAIL_ASKING)
            bot.send_message(
                chat.id,
                messages.EMAIL_ENTERING)
            logging.info(f"Asked for email entering, user_states = {user_states}")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "awaiting_email")
def process_email(message):
    chat_id = message.chat.id
    try:
        validate_email(message.text)
        logging.info("Email validation successful")
    except ValidationError as e:
        bot.send_message(chat_id, f"{e.message}❌")
        return

    user_info = {
        "chat_id": chat_id,
        "email": message.text,
        "username": message.chat.username,
        "first_name": message.chat.first_name,
        "last_name": message.chat.last_name,
        }
    del user_states[chat_id]
    response = requests.post(f"{DJANGO_API_URL}users/", json=user_info, headers=headers)
    if response.status_code == 201:
        logging.info(f"response if = {response.status_code}")
    else:
        bot.send_message(chat_id, messages.UNSUCCESSFUL_REGISTRATION)
        logging.info(f"response else = {response.text}")
        handler.flush()
        logging.error(f"response else = {response.status_code}")
        return
    handler.flush()
    bot.send_message(chat_id, messages.SUCCESSFUL_REGISTRATION)
    logging.info("Registration successful")
    logging.info(f"user_info = {user_info}")


@bot.message_handler(func=lambda message: isinstance(user_states.get(message.chat.id), dict) and user_states[message.chat.id].get("state") == "awaiting_password")
def process_password(message):
    """Registration throught message."""
    chat_id = message.chat.id
    user_data = user_states.get(chat_id)
    if user_data:
        user_states[message.chat.id]["password"] = message.text
        user_states[message.chat.id].pop("state", None)
        user_states[message.chat.id]["first_name"] = message.chat.first_name
        user_states[message.chat.id]["last_name"] = message.chat.last_name
        user_states[message.chat.id]["username"] = message.chat.username
        bot.send_message(chat_id, "Your registration was successful! \U00002705")
        logging.info(user_states)


@bot.message_handler(content_types=["text"])
def send_welcome(message):
    chat = message.chat
    bot.reply_to(message, text=messages.UNRECOGNIZED_MESSAGE_REPLY)


bot.polling()
