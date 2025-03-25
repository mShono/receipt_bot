import logging

import os
from dotenv import load_dotenv
import requests

from telebot import TeleBot, types
from . import messages

from .django_interaction import check_products_existence
from .file_saving import file_saving
from .receipt_recognition import recognition_ocr_mini, recognition_turbo


# settings.configure()
load_dotenv()



DJANGO_API_URL = os.getenv("DJANGO_API_URL")
bot = TeleBot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

headers = {
    "Authorization": f"Token {os.getenv("DJANGO_BOT_TOKEN")}",
    "Content-Type": "application/json",
}

UPLOAD_FOLDER = "uploaded_receipts"

user_states = {}
user_info = {}


logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.INFO)

logger.info("Receipt_bot launched")

@bot.message_handler(commands=["start"])
def wake_up(message):
    chat = message.chat
    markup = types.InlineKeyboardMarkup()
    # register_url_button = types.InlineKeyboardButton("Register", url="https://ya.ru")
    register_callback_button = types.InlineKeyboardButton("Register", callback_data="Register")
    markup.add(register_callback_button)
    bot.send_message(
        chat_id=chat.id,
        text=messages.INVITATION_TO_REGISTER,
        reply_markup=markup)
    logger.info("Invitation for registration sent")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat = call.message.chat
    if call.message:
        if call.data == "Register":
            user_info = {
                "chat_id": chat.id,
                "username": chat.username,
                "first_name": chat.first_name,
                "last_name": chat.last_name,
            }
            logger.info(f"Information has been collected, user_info = {user_info}")
            response = requests.post(f"{DJANGO_API_URL}users/", json=user_info, headers=headers)
            if response.status_code == 201:
                logger.info(f"Registration successful, response.status_code = {response.status_code}")
            else:
                bot.send_message(chat.id, messages.UNSUCCESSFUL_REGISTRATION)
                logger.info(f"Registratipon failed, response.text = {response.text}")
                logger.error(f"response.status_code = {response.status_code}")
                return
            bot.send_message(chat.id, messages.SUCCESSFUL_REGISTRATION)
            markup = types.InlineKeyboardMarkup()
            upload_receipt_button = types.InlineKeyboardButton("Upload receipt", callback_data="Upload receipt")
            markup.add(upload_receipt_button)
            bot.send_message(
                chat_id=chat.id,
                text=messages.UPLOAD_RECEIRT_FIRST,
                reply_markup=markup)
            logger.info("Showed the 'Upload receipt' button")
        if call.data == "Upload receipt":
            bot.send_message(
                chat.id,
                messages.UPLOAD_RECEIRT)
            logger.info("Asked for receipt uploading")

@bot.message_handler(content_types=['photo', 'document'])
def handle_receipt_photo(message):
    logger.info("Receiving a photo")
    if message.content_type == 'document':
        if not message.document.mime_type.startswith("image/"):
            logger.info("The uploaded file was not an image")
            bot.send_message(
                    message.chat.id,
                    messages.RECEIPT_INST_IS_DOC)
            return
        file_id = message.document.file_id
    else:
        file_id = message.photo[-1].file_id
    chat_id = message.chat.id
    file_info = bot.get_file(file_id)
    logger.info(f"file_info = {file_info}")
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = f"{chat_id}_receipt"
    saving_status, _ = file_saving(UPLOAD_FOLDER, file_name, downloaded_file, "wb", "image")

    if saving_status == True:
        bot.send_message(
            message.chat.id,
            messages.SUCCESSFUL_RECEIPT_UPLOADING)
        logger.info("Successful receipt uploading message sent")
    else:
        bot.send_message(
            message.chat.id,
            messages.UNSUCCESSFUL_RECEIPT_UPLOADING)
        logger.info("Unsuccessful receipt uploading message sent")
    # recognition_ocr_mini(file_name)
    filepath = recognition_turbo(file_name)
    check_products_existence(filepath)
    # response = requests.post(f"{DJANGO_API_URL}users/", json=user_info, headers=headers)


@bot.message_handler(content_types=["text"])
def send_welcome(message):
    logger.info("Received an unrecoginzed message")
    bot.reply_to(message, text=messages.UNRECOGNIZED_MESSAGE_REPLY)
    logger.info("An unrecoginzed message reply sent")

bot.polling()
