import logging

import os
from dotenv import load_dotenv
import requests

from telebot import TeleBot, types

from . import messages
from . import state
from .buttons import price_name_buttons, category_buttons
from .conversions import float_to_int
from .django_interaction import check_one_product_existence, check_existent_categories, post_category_product

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


def process_price_edit(message, editted_list_position, buttons_list, buttons_list_name):
    logger.info(f"For {editted_list_position} the user set the following price \"{message.text}\". Price validation launched")
    new_price = message.text
    validity, validated_price = price_validation(new_price)
    logger.info(f"validity =  {validity}")
    if not validity:
        logger.info("Invalid price entered.")
        bot.send_message(
        message.chat.id,
        f"Can't set a {validated_price} price to \"{editted_list_position["name"]}\". "\
        "Please, enter a correct price with two digits after point",
        reply_markup=price_name_buttons())
    else:
        for list_position in buttons_list:
            price = list_position["price"]
            if list_position == editted_list_position:
                price = validated_price
            integer_price = float_to_int(price)
            list_position["price"] = integer_price
            logger.info(f"Updated {list_position["name"]} price to {list_position["price"]}")
        logger.info(f"buttons_list = {buttons_list}")
        bot.send_message(
            message.chat.id,
            f"Price for \"{editted_list_position["name"]}\" updated to {validated_price}. "\
            "Do you want to correct something else?",
            reply_markup=price_name_buttons(buttons_list, buttons_list_name))


def process_name_edit(message, editted_list_position, buttons_list):
    logger.info(f"For \"{editted_list_position}\" the user set the following name \"{message.text}\".")
    old_name = editted_list_position["name"]
    for list_position in buttons_list:
        # price = list_position["price"]
        # integer_price = float_to_int(price)
        # list_position["price"] = integer_price
        if list_position == editted_list_position:
            list_position["name"] = message.text
    logger.info(f"Updated {old_name} to {editted_list_position["name"]}")
    status = check_one_product_existence(product=message.text)
    if not status:
        check_existent_categories()
        bot.send_message(
            message.chat.id,
            f"The product \"{message.text}\" is not in our database. "\
            "Please enter it's category.",
            reply_markup=category_buttons(editted_list_position["name"]))
    else:
        bot.send_message(
            message.chat.id,
            f"Updated \"{old_name}\" to \"{message.text}\". "\
            "Please correct the other products.",
            reply_markup=price_name_buttons(state.PRODUCTS_ABSENT_IN_DATABASE, "ABSENT_IN_DATABASE"))
    # Here I need to add an algorithm in case the product name entered by the user is in the database.

    # price edition will be te future feature
    # logger.info(f"buttons_list = {buttons_list}")
    # bot.send_message(
    #     message.chat.id,
    #     f"Updated \"{old_name}\" to {message.text}. "\
    #     f"Do you need to correct its price \"{editted_list_position["price"]}\"?",
    #     reply_markup=yes_no_buttons(editted_list_position))


def category_creation(message, product_name):
    logger.info(f"For the product \"{product_name}\" the user set the following category \"{message.text}\".")
    try:
        post_category_status, new_category_id = post_category_product("category", {"name": f"{message.text}"})
        if not post_category_status:
            messages.send_error_message(message, product_name)
            return
        post_product_status, _ = post_category_product("product", {"name": f"{product_name}", "category": f"{new_category_id}"})
        if post_product_status:
            bot.send_message(
                message.chat.id,
                f"The category \"{message.text}\" successfully set for the product \"{product_name}\". "\
                "Please correct the other products.",
                reply_markup=price_name_buttons(state.PRODUCTS_ABSENT_IN_DATABASE, "ABSENT_IN_DATABASE"))
        else:
            messages.send_error_message(message, product_name)
            return
    except Exception as e:
        messages.send_error_message(message, product_name)


def get_category_id(category_name):
    for category in state.EXISTING_CATEGORIES_WITH_ID:
        logger.info(f"category_name = {category_name}")
        logger.info(f"category = {category}")
        if category["name"] == category_name:
            logger.info(f"Id for category \"{category["name"]}\" = {category["id"]}")
            return category["id"]
        break
