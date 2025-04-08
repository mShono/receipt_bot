import logging
import os
from dotenv import load_dotenv

from telebot import TeleBot, types

from . import state
from .buttons import price_name_buttons
from .django_interaction import get_data_info

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bot = TeleBot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

INVITATION_TO_REGISTER = "Sign up for a recipe bot that will help you keep track of your expenses!👇"
WARNING_BEFORE_EMAIL_ASKING = """I'll help you register now. Enter the information correctly❗ The data will be used to log in in web version"""
EMAIL_ENTERING = "Please, enter your email"
SUCCESSFUL_REGISTRATION = "Your registration was successful! ✅"
UNSUCCESSFUL_REGISTRATION = "Unfortunately, we haven't been able to register you yet 🙁 Please try again later."
UNRECOGNIZED_MESSAGE_REPLY = "Sorry, I don't have a prepared response to such a message yet 🤷‍♂️"
UPLOAD_RECEIRT_FIRST = "Do you want to upload your first receipt?"
UPLOAD_RECEIRT = "Please, upload the receipt photo"
RECEIPT_INST_IS_DOC = "You've uploaded receipt photo as a document. Please, upload it as a photo"
SUCCESSFUL_RECEIPT_UPLOADING = "Your receipt uploaded was successful! ✅"
UNSUCCESSFUL_RECEIPT_UPLOADING = "Unfortunately, we were unable to upload your receipt right now 😔"
SUCCESSFUL_RECOGNITION = "The following products were recognised successfully 😌 Do you want to edit the price?"
RECOGNIZED_PRODUCTS_MISSING_IN_DATABASE = "The following products are missing from our database. 🤷‍♂️ Do you want to add them?"
UNSUCCESSFUL_RECOGNITION = "Unfortunately, we were unable to recognize any products in that receipt 😔"
ASKING_IF_THE_PRICE_EDITION_IS_NEEDED = "Do you want to edit the other product price?"
UPLOAD_EXPENCE = "Uploading expense to database"
SUCCESSFUL_UPLOAD_EXPENCE = "Your expense was successfully uploaded to database! ✅"
UNSUCCESSFUL_UPLOAD_EXPENCE = "Unfortunately, we were unable to upload your expense right now 😔"
UNEXPECTED_ERROR = "Sorry, an unexpected error has occurred 🤷‍♂️"


def send_error_message(message, product_name):
    force_reply = types.ForceReply(selective=True)
    bot.send_message(
        message.chat.id,
        f"Something went wrong while creating category for \"{product_name}\". Please, try again:",
        reply_markup=force_reply
    )
    bot.send_message(
        message.chat.id,
        reply_markup=price_name_buttons(state.PRODUCTS_ABSENT_IN_DATABASE, "ABSENT_IN_DATABASE")
    )


def send_final_message(context):
    if not context.new_expense:
        bot.send_message(
            context.user_id,
            SUCCESSFUL_UPLOAD_EXPENCE)
        _, expense_info = get_data_info("expense", context.expence_id)
        context.expence_id = None
        logger.info(f"expense info = {expense_info}")
