import logging

from telebot import types

from . import state
from .conversions import int_to_float_str

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def yes_no_buttons(list_position):
    markup = types.InlineKeyboardMarkup()
    buttons_in_a_row = []
    buttons_in_a_row.append(types.InlineKeyboardButton("Yes", callback_data=f"price_edit_yes:{list_position["name"]}"))
    buttons_in_a_row.append(types.InlineKeyboardButton("No", callback_data="No"))
    markup.row(*buttons_in_a_row)
    return markup


def price_name_buttons(buttons_list, buttons_list_name): # the price should come here in int
    if buttons_list:
        logger.info(f"Starting to form the \"{buttons_list_name}\" buttons")
        markup = types.InlineKeyboardMarkup()
        buttons_in_a_row = []
        len_buttons_list = len(buttons_list)
        for list_position in buttons_list:
            price = int_to_float_str(list_position["price"])
            list_position["price"] = price
            buttons_in_a_row.append(types.InlineKeyboardButton(
                f"{list_position["name"]}: {list_position["price"]} €",
                callback_data=f"{list_position["name"]}: {list_position["price"]} €")
            )
            if len(buttons_in_a_row) == 2:
                markup.row(*buttons_in_a_row)
                buttons_in_a_row = []
            elif (len(buttons_in_a_row) == 1) and (len_buttons_list == 1):
                markup.add(*buttons_in_a_row)
            len_buttons_list -= 1
        if buttons_list_name == "PRESENT_IN_DATABASE":
            no_button = types.InlineKeyboardButton("Nothing to edit", callback_data="Nothing_to_edit_after_PRESENT_IN_DATABASE")
        elif buttons_list_name == "ABSENT_IN_DATABASE":
            no_button = types.InlineKeyboardButton("Nothing to edit", callback_data="Nothing_to_edit_after_ABSENT_IN_DATABASE")
        markup.add(no_button)
    logger.info(f"The \"{buttons_list_name}\" buttons were formed successfully")
    return markup


def category_buttons(product_requiring_category):
    if state.EXISTING_CATEGORIES:
        logger.info("Starting to form the category buttons")
        markup = types.InlineKeyboardMarkup()
        buttons_in_a_row = []
        len_buttons_list = len(state.EXISTING_CATEGORIES)
        for category in state.EXISTING_CATEGORIES:
            buttons_in_a_row.append(types.InlineKeyboardButton((category), 
                callback_data=f"existing_cat:{category}, prod:{product_requiring_category}"))
            if len(buttons_in_a_row) == 2:
                markup.row(*buttons_in_a_row)
                buttons_in_a_row = []
            elif (len(buttons_in_a_row) == 1) and (len_buttons_list == 1):
                markup.add(*buttons_in_a_row)
            len_buttons_list -= 1
        category_creation = types.InlineKeyboardButton("Create a new category",
            callback_data=f"category_creation, prod:{product_requiring_category}")
        markup.add(category_creation)
        logger.debug(f"markup.to_dict {markup.to_dict()}")
    return markup