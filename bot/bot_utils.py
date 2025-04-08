import logging

import os
from dotenv import load_dotenv
import requests

from telebot import TeleBot, types

from . import messages
from . import state
from .buttons import price_name_buttons, category_buttons
from .conversions import float_to_int
from .django_interaction import get_data_info, check_existent_categories, post_data_info
from .file_operations import file_opening

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
    context = state.UserContext[message.chat.id]
    stage = context.stage
    if "present" in stage:
        buttons_list = context.products_present_in_database
    elif "absent" in stage:
        buttons_list = context.products_absent_in_database
    logger.info(f"For {editted_list_position} the user set the following price \"{message.text}\". Price validation launched")
    new_price = message.text
    status, validated_price = price_validation(new_price)
    logger.info(f"price validation status =  {status}")
    if not status:
        logger.info("Invalid price entered.")
        bot.send_message(
        message.chat.id,
        f"Can't set a {validated_price} price to \"{editted_list_position["name"]}\". "\
        "Please, enter a correct price with two digits after point",
        reply_markup=price_name_buttons(context))
    else:
        for list_position in buttons_list:
            if list_position == editted_list_position:
                list_position["price"] = float_to_int(validated_price)
        logger.info(f"Updated {list_position["name"]} price to {list_position["price"]}")
        logger.info(f"buttons_list = {buttons_list}")
        bot.send_message(
            message.chat.id,
            f"Price for \"{editted_list_position["name"]}\" updated to {validated_price}. "\
            "Do you want to correct something else?",
            reply_markup=price_name_buttons(context))


def process_name_edit(message, editted_list_position):
    context = state.UserContext[message.chat.id]
    stage = context.stage
    if "present" in stage:
        buttons_list = context.products_present_in_database
    elif "absent" in stage:
        buttons_list = context.products_absent_in_database
    logger.info(f"For \"{editted_list_position}\" the user set the following name \"{message.text}\".")
    old_name = editted_list_position["name"]
    for list_position in buttons_list:
        if list_position == editted_list_position:
            list_position["name"] = message.text
    logger.info(f"Updated {old_name} to {editted_list_position["name"]}")
    status, _ = get_data_info("product", message.text)
    if not status:
        check_existent_categories(context)
        bot.send_message(
            message.chat.id,
            f"The product \"{message.text}\" is not in our database. "\
            "Please enter it's category.",
            reply_markup=category_buttons(editted_list_position["name"], context))
    else:
        bot.send_message(
            message.chat.id,
            f"Updated \"{old_name}\" to \"{message.text}\". "\
            "Please correct the other products.",
            reply_markup=price_name_buttons(context))

    # price edition will be te future feature
    # logger.info(f"buttons_list = {buttons_list}")
    # bot.send_message(
    #     message.chat.id,
    #     f"Updated \"{old_name}\" to {message.text}. "\
    #     f"Do you need to correct its price \"{editted_list_position["price"]}\"?",
    #     reply_markup=yes_no_buttons(editted_list_position))


def collecting_data_to_get_products(filepath, context):
    shopping_list = file_opening(filepath)
    logger.info("Start collecting poduct data")
    products_present_in_database = context.products_present_in_database
    products_absent_in_database = context.products_absent_in_database
    for list_position in shopping_list:
        try:
            product_name = list_position["name"]
            price = list_position["price"]
        except Exception as e:
            logger.error(f"Reading the json file with products failed: {e}")
            raise e
        integer_price = float_to_int(price)
        list_position["price"] = integer_price
        status, product_info = get_data_info("product", product_name)
        if status == True:
            list_position["id"] = product_info["id"]
            products_present_in_database.append(list_position)
        else:
            products_absent_in_database.append(list_position)
    logger.info(f"products_present_in_database = {products_present_in_database}")
    logger.info(f"products_absent_in_database = {products_absent_in_database}")
    return


def category_creation(message, product_name):
    context = state.UserContext[message.chat.id]
    logger.info(f"For the product \"{product_name}\" the user set the following category \"{message.text}\".")
    try:
        post_category_status, new_category_id = post_data_info("category", {"name": f"{message.text}"})
        if not post_category_status:
            messages.send_error_message(message, product_name, context, "category")
            return
    except Exception as e:
        messages.send_error_message(message, product_name, context,"category")
    try:
        post_product_status, _ = post_data_info("product", {"name": f"{product_name}", "category": f"{new_category_id}"})
        if not post_product_status:
            messages.send_error_message(message, product_name, context, "product")
            return
        bot.send_message(
                message.chat.id,
                f"The category \"{message.text}\" successfully set for the product \"{product_name}\". "\
                "Please correct the other products.",
                reply_markup=price_name_buttons(context))
    except Exception as e:
        messages.send_error_message(message, product_name, context, "product")


def get_category_id(category_name, context):
    for category in context.existing_categories_with_id:
        if category["name"] == category_name:
            logger.info(f"Id for category \"{category["name"]}\" = {category["id"]}")
            return category["id"]
        break


def collecting_data_and_post_user(message):
    user_info = {
        "chat_id": message.chat.id,
        "username": message.chat.username,
        "first_name": message.chat.first_name,
        "last_name": message.chat.last_name,
    }
    logger.info(f"Information has been collected, user_info = {user_info}")
    post_user_status, user_info = post_data_info("users", user_info)
    return post_user_status, user_info


def collecting_data_and_post_expense(message):
    context = state.UserContext[message.chat.id]
    if not context.new_expense:
        get_user_info_status, user_info = get_data_info("users", message.chat.username)
        if not get_user_info_status:
            post_user_status, user_id = collecting_data_and_post_user(message)
            if not post_user_status:
                return False, None
        else:
            user_id = user_info["id"]
        logger.info(f"user_id = {user_id}")
    context.stage = "new_expense"
    context.new_expense.extend(context.products_present_in_database)
    context.products_present_in_database.clear()
    context.new_expense.extend(context.products_absent_in_database)
    context.products_absent_in_database.clear()
    logger.info(f"new_expense = {context.new_expense}")
    expense_dict = {}

    try:
        expense_dict["user"] = user_id
        logger.info(f"expense_dict['user'] = {expense_dict['user']}")
    except Exception as e:
        logger.error(f"Reading the json file response with user info failed: {e}")
        raise e
    post_expense_status, expense_id = post_data_info("expense", expense_dict)
    if not post_expense_status:
        return False, None
    context.expense_id = expense_id
    return True, expense_id


def collecting_data_and_post_item(message):
    context = state.UserContext[message.chat.id]
    expense_id = context.expense_id
    statuses = []
    logger.info(f"context.new_expense = {context.new_expense}")
    while context.new_expense:
        item = context.new_expense.pop(0)
        status, product_info = get_data_info("product", item["name"])
        if status:
            logger.info(f"product_info = {product_info}")
            item["expense"] = expense_id
            item["product"] = product_info["id"]
            item["price"] = float_to_int(item["price"])
            item.pop("name")
            if item.get("id"):
                logger.info(f"Item  \"{product_info["name"]}\" exists in database")
                item.pop("id")
            post_item_status, _ = post_data_info("expense_item", item)
            statuses.append(post_item_status)
        else:
            context.new_expense.insert(0, item)
            check_existent_categories(context)
            bot.send_message(
            message.chat.id,
            f"The product \"{item["name"]}\" is not in our database. "\
            "Please enter it's category.",
            reply_markup=category_buttons(item["name"], context))
            return
            # break
    if False in statuses:
        bot.send_message(
            message.chat.id,
            messages.UNSUCCESSFUL_UPLOAD_EXPENCE)
        # return False
    else:
        bot.send_message(
            context.chat_id,
            messages.SUCCESSFUL_UPLOAD_EXPENCE)
        _, expense_info = get_data_info("expense", context.expense_id)
        context.expense_id = None
        logger.info(f"expense info = {expense_info}")
        # return True
