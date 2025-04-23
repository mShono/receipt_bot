import logging

import os
from dotenv import load_dotenv
import requests

from telebot import TeleBot, types

from . import messages
from . import state
from .bot_utils import process_price_edit, process_name_edit, post_category_product, get_category_id, collecting_data_and_post_expense, collecting_data_to_get_products, collecting_data_and_post_item, collecting_data_and_post_user
from .buttons import price_name_buttons
from .django_interaction import post_data_info
from .file_operations import file_saving
from .messages import send_reply_markup_message
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


@bot.callback_query_handler(func=lambda call: call.data == "Register")
def callback_register(call):
    message = call.message
    post_user_status, user_info = collecting_data_and_post_user(message)
    if not post_user_status:
        bot.send_message(message.chat.id, messages.UNSUCCESSFUL_REGISTRATION)
        return

    if type(user_info) is dict:
        bot.send_message(message.chat.id, messages.ALREADY_REGISTERED)
        logger.info("Sent an 'Already regestered' message")
    else:
        bot.send_message(message.chat.id, messages.SUCCESSFUL_REGISTRATION)
        logger.info("Sent a 'Successful registration' message")

    markup = types.InlineKeyboardMarkup()
    upload_receipt_button = types.InlineKeyboardButton("Upload receipt", callback_data="Upload receipt")
    markup.add(upload_receipt_button)
    send_reply_markup_message(
        message.chat,
        messages.UPLOAD_RECEIRT_FIRST,
        markup)
    logger.info("Showed the 'Upload receipt' button")


@bot.callback_query_handler(func=lambda call: call.data.startswith("price_edit_yes:"))
def callback_price_edit(call):
    try:
        _, product_name = call.data.split(":", 1)
    except Exception as e:
        logger.error(f"Error parsing callback_data: {call.data} - {e}")
        return

    editted_list_position = None
    for list_position in state.PRODUCTS_ABSENT_IN_DATABASE:
        if list_position["name"] == product_name:
            editted_list_position = list_position
            break

    logger.info(f"The user wants to edit the price of the following product: {editted_list_position}")
    force_reply = types.ForceReply(selective=True)
    send_reply_markup_message(
        call.message.chat,
        messages.CORRECTING_PRICE,
        force_reply,
        name = editted_list_position["name"],
        price = editted_list_position["price"]
    )
    bot.register_next_step_handler(
        call.message,
        lambda message: process_price_edit(message, editted_list_position, state.PRODUCTS_ABSENT_IN_DATABASE))


@bot.callback_query_handler(func=lambda call: call.data.startswith("Nothing_to_edit_after_PRESENT_IN_DATABASE"))
def callback_nothing_after_present(call):
    context = state.UserContext[call.message.chat.id]
    context.stage = "products_absent_in_database"
    logger.info(f"ABSENT_IN_DATABASE = {context.products_absent_in_database}")
    if context.products_absent_in_database:
        markup = price_name_buttons(context)
        send_reply_markup_message(
            call.message.chat,
            messages.RECOGNIZED_PRODUCTS_MISSING_IN_DATABASE,
            markup,
        )
        logger.info("Sent the absent in database products and asked for edition")

    else:
        bot.send_message(
            call.message.chat.id,
            messages.UPLOAD_EXPENCE)
        post_expense_status, _ = collecting_data_and_post_expense(call.message)
        if not post_expense_status:
            bot.send_message(
                call.message.chat.id,
                messages.UNSUCCESSFUL_UPLOAD_EXPENCE)
            return
        collecting_data_and_post_item(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("Nothing_to_edit_after_ABSENT_IN_DATABASE"))
def callback_nothing_after_absent(call):
    bot.send_message(
        call.message.chat.id,
        messages.UPLOAD_EXPENCE)
    post_expense_status, _ = collecting_data_and_post_expense(call.message)
    if not post_expense_status:
        bot.send_message(
            call.message.chat.id,
            messages.UNSUCCESSFUL_UPLOAD_EXPENCE)
        return

    collecting_data_and_post_item(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("exist_cat"))
# here we should also ask about the price!
def callback_existing_category(call):
    context = state.UserContext[call.message.chat.id]
    try:
        category_info, product_info = call.data.split(",", 1)
        _, category_name = category_info.split(":", 1)
        _, product_name = product_info.split(":", 1)
        logger.info("Successful parsing callback_data")
        logger.info(f"category_name = {category_name}")
        logger.info(f"product_name = {product_name}")
    except Exception as e:
        logger.error(f"Error parsing callback_data: {call.data} - {e}")
        return

    logger.info(f"The user assigns the category \"{category_name}\" for the following product: \"{product_name}\"")
    category_id = get_category_id(category_name, context)
    logger.debug(f"posting data info from exist_cat")
    status, _ = post_data_info("product", {"name": f"{product_name}", "category": category_id})
    if status:
        if context.stage == "new_expense":
            send_reply_markup_message(
                call.message.chat,
                messages.SUCCESSFUL_CATEGORY_CORRECT,
                category_name = category_name,
                product_name = product_name
            )
            collecting_data_and_post_item(call.message)
        elif "absent" in context.stage:
            send_reply_markup_message(
                call.message.chat,
                messages.SUCCESSFUL_CATEGORY_CORRECT,
                price_name_buttons(context),
                category_name = category_name,
                product_name = product_name
            )


@bot.callback_query_handler(func=lambda call: call.data.startswith("categ_cr"))
def callback_category_creation(call):
    try:
        _, product_info = call.data.split(",", 1)
        _, product_name = product_info.split(":", 1)
        logger.info("Successful parsing callback_data")
        logger.info(f"product_name = {product_name}")
    except Exception as e:
        logger.error(f"Error parsing callback_data: {call.data} - {e}")
        return

    send_reply_markup_message(
        call.message.chat,
        messages.SUGGESTION_TO_ENTER_CATEGORY_FOR_PRODUCT,
        types.ForceReply(selective=True),
        product_name = product_name
    )
    bot.register_next_step_handler(call.message, lambda message: post_category_product(message, product_name))


@bot.callback_query_handler(func=lambda call: call.data == "Upload receipt")
def callback_upload_receipt(call):
    bot.send_message(
            call.message.chat.id,
            messages.UPLOAD_RECEIRT)
    logger.info("Asked for receipt uploading")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    message = call.message
    if not call.message:
        return

    context = state.UserContext[message.chat.id]

    for list_position in context.products_present_in_database:
        pushed_button = f"{list_position['name']}"
        if call.data == pushed_button:
            logger.info(f"The user wants to edit the price of the following product {pushed_button}")
            send_reply_markup_message(
                call.message.chat,
                messages.CORRECTING_PRICE,
                types.ForceReply(selective=True),
                name = list_position['name'],
                price = list_position['price']
            )
            bot.register_next_step_handler(call.message, lambda message: process_price_edit(
                message,
                list_position)
            )
            return

    for list_position in context.products_absent_in_database:
        pushed_button = f"{list_position['name']}"
        if call.data == pushed_button:
            logger.info(f"The user wants to edit {pushed_button}")
            send_reply_markup_message(
                call.message.chat,
                messages.CORRECTING_NAME,
                types.ForceReply(selective=True),
                name = list_position['name'],
            )
            bot.register_next_step_handler(call.message, lambda message: process_name_edit(
                message,
                list_position)
            )
            return


@bot.message_handler(content_types=['photo', 'document'])
def handle_receipt_photo(message):
    chat_id = message.chat.id
 
    context = state.Context()
    context.chat_id = chat_id
    state.UserContext[chat_id] = context

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
    # filepath = "/home/masher/development/receipt_bot/uploaded_receipts/382807642_receipt_product_ai.json"
    # filepath = "/home/masher/development/receipt_bot/uploaded_receipts/test_unrecognised_receipt.json"
    collecting_data_to_get_products(filepath, context)
    if context.products_present_in_database:
        context.stage = "products_present_in_database"
        logger.info(f"stage = {context.stage}")
        markup = price_name_buttons(context)
        bot.send_message(
            message.chat.id,
            messages.SUCCESSFUL_RECOGNITION,
            reply_markup=markup)
        logger.info("Sent the present in database products and asked if the price edition is needed")
    elif context.products_absent_in_database:
        context.stage = "products_absent_in_database"
        logger.info(f"stage = {context.stage}")
        markup = price_name_buttons(context)
        bot.send_message(
            message.chat.id,
            messages.RECOGNIZED_PRODUCTS_MISSING_IN_DATABASE,
            reply_markup=markup)
        logger.info("Sent the absent in database products and asked for edition")
        return
    else:
        bot.send_message(
            message.chat.id,
            messages.UNSUCCESSFUL_RECOGNITION
        )
        logger.info("Sent the message that we were unable to recognize any products in the receipt")
        return



@bot.message_handler(content_types=["text"])
def unknown_message_answer(message):
    logger.info("Received an unrecoginzed message")
    bot.reply_to(message, text=messages.UNRECOGNIZED_MESSAGE_REPLY)
    logger.info("An unrecoginzed message reply sent")

# bot.polling()

if __name__ == "__main__":
    bot.polling()
