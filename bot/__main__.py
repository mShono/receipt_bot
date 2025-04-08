import logging

import os
from dotenv import load_dotenv
import requests

from telebot import TeleBot, types

from . import messages
from . import state
from .bot_utils import process_price_edit, process_name_edit, category_creation, get_category_id, collecting_data_to_post_expence, collecting_data_to_get_products, collecting_data_to_post_item
from .buttons import price_name_buttons
from .django_interaction import post_data_info, get_data_info
from .file_operations import file_saving
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
# PRESENT_IN_DATABASE = []

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
    bot.send_message(
        call.message.chat.id,
        f"Current price for \"{editted_list_position["name"]}\" is {editted_list_position["price"]} € "\
        "Please enter the correct price:",
        reply_markup=force_reply
    )
    bot.register_next_step_handler(
        call.message,
        lambda message: process_price_edit(message, editted_list_position, state.PRODUCTS_ABSENT_IN_DATABASE))


@bot.callback_query_handler(func=lambda call: call.data.startswith("Nothing_to_edit_after_PRESENT_IN_DATABASE"))
def callback_price_edit(call):
    context = state.UserContext[call.message.chat.id]
    context.stage = "products_absent_in_database"
    logger.info(f"ABSENT_IN_DATABASE = {context.products_absent_in_database}")
    if context.products_absent_in_database:
        markup = price_name_buttons(context)
        bot.send_message(
            call.message.chat.id,
            messages.RECOGNIZED_PRODUCTS_MISSING_IN_DATABASE,
            reply_markup=markup)
        logger.info("Sent the absent in database products and asked for edition")


@bot.callback_query_handler(func=lambda call: call.data.startswith("Nothing_to_edit_after_ABSENT_IN_DATABASE"))
def callback_price_edit(call):
    context = state.UserContext[call.message.chat.id]
    bot.send_message(
        call.message.chat.id,
        messages.UPLOAD_EXPENCE)
    post_expence_status, expence_id = collecting_data_to_post_expence(call.message)
    if not post_expence_status:
        bot.send_message(
            call.message.chat.id,
            messages.UNSUCCESSFUL_UPLOAD_EXPENCE)
        return

    collecting_data_to_post_item(call)
    # post_item_status = collecting_data_to_post_item(call)
    # if context.new_expense:
    #     return
    # if not post_item_status:
    #     bot.send_message(
    #         call.message.chat.id,
    #         messages.UNSUCCESSFUL_UPLOAD_EXPENCE)
    #     return
    # else:
    #     messages.send_final_message(context)


@bot.callback_query_handler(func=lambda call: call.data.startswith("exist_cat"))
# here we should also ask about the price!
def callback_existing_category(call):
    context = state.UserContext[call.message.chat.id]
    try:
        category_info, product_info = call.data.split(",", 1)
        _, category_name = category_info.split(":", 1)
        _, product_name = product_info.split(":", 1)
        logger.debug(f"category_name = {category_name}")
        logger.debug(f"product_name = {product_name}")
    except Exception as e:
        logger.error(f"Error parsing callback_data: {call.data} - {e}")
        return

    logger.info(f"The user assigns the category \"{category_name}\" for the following product: \"{product_name}\"")
    category_id = get_category_id(category_name, context)
    logger.debug(f"posting data info from exist_cat")
    status, _ = post_data_info("product", {"name": f"{product_name}", "category": category_id})
    if status:
        if context.stage == "new_expense":
            bot.send_message(
            call.message.chat.id,
            f"The category \"{category_name}\" successfully set for the product {product_name}.")
            collecting_data_to_post_item(call)
            # Here I need to return back in collecting_data_to_post_item
        elif "absent" in context.stage:
            bot.send_message(
                call.message.chat.id,
                f"The category \"{category_name}\" successfully set for the product {product_name}. "\
                "Please correct the other products.",
                reply_markup=price_name_buttons(context)
            )
        # else:
        #     bot.send_message(
        #     call.message.chat.id,
        #     f"The category \"{category_name}\" successfully set for the product {product_name}.")
        #     post_item_status = collecting_data_to_post_item(call)
            # if not context.new_expense:
            #     messages.send_final_message(context)
            # if not post_item_status:
            #     bot.send_message(
            #         call.message.chat.id,
            #         messages.UNSUCCESSFUL_UPLOAD_EXPENCE)
            #     return
            # else:
            #     messages.send_final_message(context)


@bot.callback_query_handler(func=lambda call: call.data.startswith("categ_cr"))
def callback_category_creation(call):
    try:
        _, product_info = call.data.split(",", 1)
        _, product_name = product_info.split(":", 1)
        logger.info(f"product_name = {product_name}")
    except Exception as e:
        logger.error(f"Error parsing callback_data: {call.data} - {e}")
        return

    force_reply = types.ForceReply(selective=True)
    bot.send_message(
        call.message.chat.id,
        f"Please, enter a category for the product \"{product_name}\"",
        reply_markup=force_reply
    )
    bot.register_next_step_handler(call.message, lambda message: category_creation(message, product_name))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    message = call.message
    if not call.message:
        return

    context = state.UserContext[message.chat.id]

    if call.data == "Register":
        user_info = {
            "chat_id": message.chat.id,
            "username": message.chat.username,
            "first_name": message.chat.first_name,
            "last_name": message.chat.last_name,
        }
        logger.info(f"Information has been collected, user_info = {user_info}")
        response = requests.post(f"{DJANGO_API_URL}users/", json=user_info, headers=headers)
        if response.status_code == 201:
            logger.info(f"Registration successful, response.status_code = {response.status_code}")
        else:
            bot.send_message(message.chat.id, messages.UNSUCCESSFUL_REGISTRATION)
            logger.info(f"Registratipon failed, response.text = {response.text}")
            logger.error(f"response.status_code = {response.status_code}")
            return
        bot.send_message(message.chat.id, messages.SUCCESSFUL_REGISTRATION)
        markup = types.InlineKeyboardMarkup()
        upload_receipt_button = types.InlineKeyboardButton("Upload receipt", callback_data="Upload receipt")
        markup.add(upload_receipt_button)
        bot.send_message(
            chat_id=message.chat.id,
            text=messages.UPLOAD_RECEIRT_FIRST,
            reply_markup=markup)
        logger.info("Showed the 'Upload receipt' button")

    elif call.data == "Upload receipt":
        bot.send_message(
            message.chat.id,
            messages.UPLOAD_RECEIRT)
        logger.info("Asked for receipt uploading")

    for list_position in context.products_present_in_database:
        pushed_button = f"{list_position['name']}"
        if call.data == pushed_button:
            logger.info(f"The user wants to edit the price of the following product {pushed_button}")
            force_reply = types.ForceReply(selective=True)
            bot.send_message(
                message.chat.id,
                f"Current price for \"{list_position['name']}\" is {list_position['price']} €. "\
                "Please enter the correct price:",
                reply_markup=force_reply
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
            force_reply = types.ForceReply(selective=True)
            bot.send_message(
                message.chat.id,
                f"Current name for the product is \"{list_position['name']}\". "\
                "Please enter the correct name:",
                reply_markup=force_reply
            )
            bot.register_next_step_handler(call.message, lambda message: process_name_edit(
                message,
                list_position)
                # state.PRODUCTS_ABSENT_IN_DATABASE,
                # "ABSENT_IN_DATABASE")
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
    # filepath = recognition_turbo(file_name)
    # check_list_of_products_existence(filepath)
    filepath = "/home/masher/development/receipt_bot/uploaded_receipts/382807642_receipt_product_ai.json"
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
        # Here I need a logic if there're no buttons absent_in_database
        return
    else:
        bot.send_message(
            message.chat.id,
            messages.UNSUCCESSFUL_RECOGNITION,
            reply_markup=markup)
        logger.info("Sent the message that we were unable to recognize any products in the receipt")
        return



@bot.message_handler(content_types=["text"])
def unknown_message_answer(message):
    logger.info("Received an unrecoginzed message")
    bot.reply_to(message, text=messages.UNRECOGNIZED_MESSAGE_REPLY)
    logger.info("An unrecoginzed message reply sent")

bot.polling()
