import logging

import os
from decimal import Decimal
from dotenv import load_dotenv
import requests

from telebot import TeleBot, types

from . import state
from . import messages

load_dotenv()

DJANGO_API_URL = os.getenv("DJANGO_API_URL")
bot = TeleBot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

headers = {
    "Authorization": f"Token {os.getenv("DJANGO_BOT_TOKEN")}",
    "Content-Type": "application/json",
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
                logger.info(f"int_floor_part =  {int_floor_part}")
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
    if not validity:
        logger.info("Invalid price entered.")
        bot.send_message(
        message.chat.id,
        f"Can't set a {validated_price} price to \"{editted_list_position['name']}\". "\
        "Please, enter a correct price with two digits after point",
        reply_markup=create_buttons())
    else:
        for list_position in state.PRESENT_IN_DATABASE:
            if list_position == editted_list_position:
                list_position["price"] = validated_price
                break
        logger.info(f"Updated {list_position['name']} price to {list_position['price']}")
        logger.info(f"PRESENT_IN_DATABASE = {state.PRESENT_IN_DATABASE}")
        bot.send_message(
            message.chat.id,
            f"Price for \"{editted_list_position['name']}\" updated to {validated_price}. "\
            "Do you want to correct some other price?",
            reply_markup=create_buttons())


def float_to_int(price):
    decim_price = Decimal(f"{price}")
    return int(decim_price*100)


def int_to_float_str(price):
    str_int_price = str(price)
    return str_int_price[:-2] + "." + str_int_price[-2:]


def create_buttons():
    if state.PRESENT_IN_DATABASE:
        logger.info("Starting to form the buttons")
        markup = types.InlineKeyboardMarkup()
        buttons_in_a_row = []
        len_present_in_database = len(state.PRESENT_IN_DATABASE)
        for list_position in state.PRESENT_IN_DATABASE:
            price = int_to_float_str(list_position["price"])
            list_position["price"] = price
            buttons_in_a_row.append(types.InlineKeyboardButton(
                f"{list_position["name"]}: {list_position["price"]} €",
                callback_data=f"{list_position["name"]}: {list_position["price"]} €")
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




