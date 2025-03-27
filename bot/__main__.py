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
PRESENT_IN_DATABASE = []

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

        elif call.data == "Upload receipt":
            bot.send_message(
                chat.id,
                messages.UPLOAD_RECEIRT)
            logger.info("Asked for receipt uploading")

        elif call.data == "Nothing to edit":
            bot.send_message(
                chat.id,
                messages.UPLOAD_RECEIRT)
            logger.info("Asked for receipt uploading")

        for list_position in PRESENT_IN_DATABASE:
            pushed_button = f"{list_position['name']}: {list_position['price']} €"
            if call.data == pushed_button:
                logger.info(f"The user wants to edit {pushed_button}")
                force_reply = types.ForceReply(selective=True)
                bot.send_message(
                    chat.id,
                    f"Current price for \"{list_position['name']}\" is {list_position['price']} €. "\
                    "Please enter the correct price:",
                    reply_markup=force_reply
                )
                bot.register_next_step_handler(call.message, lambda message: process_price_edit(message, list_position))
                return


def price_validation(price):
    try:
        validated_price = int(price)
        if validated_price <= 0:
            logger.info(f"price = {int(price)} which is less or equal to 0")
            return False, price
        else:
            logger.info(f"The price \"{price}\" could be converted to int and isn't less or equal to 0")
            return True, validated_price
    except Exception as e:
        logger.error(f"The price \"{price}\" couldn't be converted to int")
    try:
        if "." in price:
            try:
                logger.info(f"Trying splitting \"{price}\" to floor and fractional part")
                floor_part, fractional_part = price.split(".")
                int_floor_part = int(floor_part)
            except Exception as e:
                logging.error(f"Splitting the price that user entered \"{price}\" with a '.' failed: {e}")
                return False, price
        elif "," in price:
            try:
                logger.info(f"Trying splitting \"{price}\" to floor and fractional part")
                floor_part, fractional_part = price.split(",")
                int_floor_part = int(floor_part)
                price = "".join([floor_part, ".", fractional_part])
            except Exception as e:
                logging.error(f"Splitting the price that user entered \"{price}\" with a ',' failed: {e}")
                return False, price
        else:
            logging.info(f"Turning the price that user entered {price} into a float failed")
            return False, price
    except Exception as e:
        logger.error(f"The price \"{price}\" couldn't be splited neighter with '.', nor with ','")
        return False, price
    if (len(fractional_part) > 2) or (int_floor_part < 0):
        logger.info(f"len(fractional_part) = {len(fractional_part)} which is more then 2, "\
                    f"or int(floor_part) = {int(floor_part)} which is less then 0")
        return False, price
    else:
        try:
            validated_price = float(price)
        except Exception as e:
            logging.error(f"Turning the price that user entered {price} into a float failed: {e}")
            return False, price
        logger.info(f"validated_price = {validated_price}")
        return True, validated_price


def process_price_edit(message, editted_list_position):
    logger.info(f"For {editted_list_position} the user set the following price \"{message.text}\". Price validation launched")
    new_price = message.text
    validity, validated_price = price_validation(new_price)
    logger.info(f"validity =  {validity}")
    if validity == False:
        logger.info("validity == False")
        markup = create_buttons()
        bot.send_message(
        message.chat.id,
        f"Can't set a {validated_price} price to \"{editted_list_position['name']}\". "\
        "Please, enter a correct price with two digits after point",
        reply_markup=markup)
    else:
        global PRESENT_IN_DATABASE, ABSENT_IN_DATABASE
        for list_position in PRESENT_IN_DATABASE:
            if list_position == editted_list_position:
                list_position["price"] = validated_price
                break
            else:
                pass
        logger.info(f"Updated {list_position['name']} price to {list_position['price']}")
        logger.info(f"PRESENT_IN_DATABASE = {PRESENT_IN_DATABASE}")
        markup = create_buttons()
        bot.send_message(
            message.chat.id,
            f"Price for \"{editted_list_position['name']}\" updated to {validated_price}. "\
            "Do you want to correct some other price?",
            reply_markup=markup)


def create_buttons():
    if PRESENT_IN_DATABASE:
        logger.info("Starting to form the buttons")
        markup = types.InlineKeyboardMarkup()
        buttons_in_a_row = []
        len_present_in_database = len(PRESENT_IN_DATABASE)
        for list_position in PRESENT_IN_DATABASE:
            buttons_in_a_row.append(types.InlineKeyboardButton(
                f"{list_position['name']}: {list_position['price']} €",
                callback_data=f"{list_position['name']}: {list_position['price']} €")
            )
            if len(buttons_in_a_row) == 2:
                markup.row(*buttons_in_a_row)
                buttons_in_a_row = []
            elif (len(buttons_in_a_row) == 1) and (len_present_in_database == 1):
                markup.add(*buttons_in_a_row)
            len_present_in_database -= 1
        no_button = types.InlineKeyboardButton("Nothing to edit", callback_data="Nothing to edit")
        markup.add(no_button)
    return markup


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
    # filepath = recognition_turbo(file_name)
    global PRESENT_IN_DATABASE, ABSENT_IN_DATABASE
    # PRESENT_IN_DATABASE, ABSENT_IN_DATABASE = check_products_existence(filepath)
    PRESENT_IN_DATABASE = [{'name': 'Apples', 'price': 3.12}, {'name': 'Tea', 'price': 1.14}, {'name': 'Coffee', 'price': 5.35}, {'name': 'Bananas', 'price': 2.11}]
    logger.info(f"PRESENT_IN_DATABASE = {PRESENT_IN_DATABASE}")
    if PRESENT_IN_DATABASE:
        markup = create_buttons()
        bot.send_message(
            message.chat.id,
            messages.SUCCESSFUL_RECOGNITION,
            reply_markup=markup)
        logger.info("Sent the present in database products and asked if the price edition is needed")



@bot.message_handler(content_types=["text"])
def send_welcome(message):
    logger.info("Received an unrecoginzed message")
    bot.reply_to(message, text=messages.UNRECOGNIZED_MESSAGE_REPLY)
    logger.info("An unrecoginzed message reply sent")

bot.polling()
