import logging
import os
from dotenv import load_dotenv

from telebot import TeleBot, types

from .buttons import price_name_buttons

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bot = TeleBot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
# Registration
INVITATION_TO_REGISTER = "Sign up for a recipe bot that will help you keep track of your expenses!👇"
WARNING_BEFORE_EMAIL_ASKING = """I'll help you register now. Enter the information correctly❗ The data will be used to log in in web version"""
EMAIL_ENTERING = "Please, enter your email"
SUCCESSFUL_REGISTRATION = "Your registration was successful! ✅"
ALREADY_REGISTERED = "You are already registered in our database ✅"
UNSUCCESSFUL_REGISTRATION = "Unfortunately, we haven't been able to register you yet 🙁 Please try again later."
# Unrecoginized message
UNRECOGNIZED_MESSAGE_REPLY = "Sorry, I don't have a prepared response to such a message yet 🤷‍♂️"
# Receipt uploading
UPLOAD_RECEIRT_FIRST = "Do you want to upload your first receipt?"
UPLOAD_RECEIRT = "Please, upload the receipt photo"
RECEIPT_INST_IS_DOC = "You've uploaded receipt photo as a document. Please, upload it as a photo"
SUCCESSFUL_RECEIPT_UPLOADING = "Your receipt receiving was successful! ✅"
UNSUCCESSFUL_RECEIPT_UPLOADING = "Unfortunately, we were unable to receive your receipt right now 😔"
# Recognition
SUCCESSFUL_RECOGNITION = "The following products were recognised successfully 😌 Do you want to edit the price?"
UNSUCCESSFUL_RECOGNITION = "Unfortunately, we were unable to recognize any products in that receipt 😔"
RECOGNIZED_PRODUCTS_MISSING_IN_DATABASE = "The following products are missing from our database. 🤷‍♂️ Please correct the name if needed before adding them."
PPODUCT_MISSING_IN_DATABASE = "The product \"{name}\" is not in our database. "\
    "Please enter it's category."
# Name correct
CORRECTING_NAME = "Current name for the product is \"{name}\". "\
                "Please enter the correct name:"
SUCCESSFUL_NAME_UPDATE = "Updated \"{old_name}\" to \"{new_name}\". "\
            "Please correct the other products."
# Category correct
SUGGESTION_TO_ENTER_CATEGORY_FOR_PRODUCT = "Please, enter a category for the product \"{product_name}\""
SUCCESSFUL_CATEGORY_CORRECT = "The category \"{category_name}\" successfully set for the product {product_name}."
UNSUCCESSFUL_CATEGORY_CREATION = "Something went wrong while creating category for \"{product_name}\". Please, try again:"
# Price correct
CORRECTING_PRICE = "Current price for \"{name}\" is {price} € "\
        "Please enter the correct price:"
ASKING_IF_THE_PRICE_EDITION_IS_NEEDED = "Do you want to edit the other product price?"
WRONG_PRICE = "Can't set a {price} price to \"{product}\". "\
        "Please, enter a correct price with two digits after point"
SUCCESSFUL_PRICE_UPDATE = "Price for \"{product}\" updated to {price}. "\
            "Do you want to correct something else?"
# Post the poduct
UNSUCCESSFUL_PPRODUCT_CREATION = "Something went wrong while posting new product \"{product_name}\". Please, try again:"
# Receipt uploading to database
UPLOAD_EXPENSE = "Uploading receipt to database"
SUCCESSFUL_UPLOAD_EXPENSE = "Your receipt was successfully uploaded to database! ✅"
UNSUCCESSFUL_UPLOAD_EXPENSE = "Unfortunately, we were unable to upload your receipt right now 😔"
# Receipt receiving from database
UNSUCCESSFUL_EXPENSE_REQUEST = "Unfortunately, we were unable to receive your receipts right now 😔"
NO_RECEIPTS = "There're no receipts for the requested period"
# Expense receiving from database
NO_EXPENSES = "There're no expenses for the requested period"
EXPENSES_BY_CATEGORIES = "Expenses by categories"
# Error messages
UNEXPECTED_ERROR = "Sorry, an unexpected error has occurred 🤷‍♂️"
# Keyboard messages
BUTTON_SUGGESTION = "Please, choose an action"



def send_reply_markup_message(chat, text_template, reply_markup = None, **kwargs):
    message_text = text_template.format(**kwargs)
    bot.send_message(chat.id, message_text, reply_markup=reply_markup)


def send_error_message(message, product_name, context, error_post_request):
    force_reply = types.ForceReply(selective=True)
    if error_post_request == "category":
        bot.send_message(
            message.chat.id,
            UNSUCCESSFUL_CATEGORY_CREATION.format(product_name=product_name),
            # f"Something went wrong while creating category for \"{product_name}\". Please, try again:",
            reply_markup=force_reply
        )
    elif error_post_request == "product":
        bot.send_message(
            message.chat.id,
            UNSUCCESSFUL_PPRODUCT_CREATION.format(product_name=product_name),
            # f"Something went wrong while posting new product \"{product_name}\". Please, try again:",
            reply_markup=force_reply
        )
    stage = context.stage
    if "present" in stage or "absent" in stage:
        bot.send_message(
            message.chat.id,
            reply_markup=price_name_buttons(context)
        )
