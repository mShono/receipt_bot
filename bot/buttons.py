import logging
import datetime

from dateutil.relativedelta import relativedelta
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


def price_name_buttons(context):
    stage = context.stage
    if "present" in stage:
        buttons_list = context.products_present_in_database
    elif "absent" in stage:
        buttons_list = context.products_absent_in_database

    if buttons_list:
        logger.info(f"Starting to form the \"{stage}\" buttons")
        markup = types.InlineKeyboardMarkup()
        buttons_in_a_row = []
        len_buttons_list = len(buttons_list)
        for list_position in buttons_list:
            logger.info(f"list_position = {list_position}")
            price = int_to_float_str(list_position["price"])
            list_position["price"] = price
            buttons_in_a_row.append(types.InlineKeyboardButton(
                f"{list_position["name"]}: {list_position["price"]} €",
                callback_data=f'{list_position["name"]}')
            )
            if len(buttons_in_a_row) == 2:
                markup.row(*buttons_in_a_row)
                buttons_in_a_row = []
            elif (len(buttons_in_a_row) == 1) and (len_buttons_list == 1):
                markup.add(*buttons_in_a_row)
            len_buttons_list -= 1
        if "present" in stage:
            no_button = types.InlineKeyboardButton("Nothing to edit", callback_data="Nothing_to_edit_after_PRESENT_IN_DATABASE")
        elif "absent" in stage:
            no_button = types.InlineKeyboardButton("Nothing to edit", callback_data="Nothing_to_edit_after_ABSENT_IN_DATABASE")
        markup.add(no_button)
    logger.info(f"The \"{stage}\" buttons were formed successfully")
    return markup


def category_buttons(product_requiring_category, context):
    if context.existing_categories:
        logger.info("Starting to form the category buttons")
        markup = types.InlineKeyboardMarkup()
        buttons_in_a_row = []
        len_buttons_list = len(context.existing_categories)
        for category in context.existing_categories:
            buttons_in_a_row.append(types.InlineKeyboardButton((category), 
                callback_data=f"exist_cat:{category}, prod:{product_requiring_category}"))
            if len(buttons_in_a_row) == 2:
                markup.row(*buttons_in_a_row)
                buttons_in_a_row = []
            elif (len(buttons_in_a_row) == 1) and (len_buttons_list == 1):
                markup.add(*buttons_in_a_row)
            len_buttons_list -= 1
        category_creation = types.InlineKeyboardButton("Create a new category",
            callback_data=f"categ_cr, prod:{product_requiring_category}")
        markup.add(category_creation)
        logger.debug(f"markup.to_dict {markup.to_dict()}")
    return markup


def keyboard_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("📥 Upload new receipt"))
    keyboard.add(types.KeyboardButton("🧾 View my receipts"))
    keyboard.add(types.KeyboardButton("💰 View my expenses"))
    return keyboard


def submenu_buttons(button_type):
    logger.info(f"Starting to form the {button_type} buttons")
    today = datetime.date.today()
    three_days_ago = today - datetime.timedelta(days=3)
    week_ago = today - datetime.timedelta(weeks=1)
    markup = types.InlineKeyboardMarkup()
    row_1 = [
        types.InlineKeyboardButton(
            ("for 1 day"), callback_data=f"{button_type}:created_at={today}"
        ),
        types.InlineKeyboardButton(
            ("for 3 days"), callback_data=f"{button_type}:created_at__range={three_days_ago},{datetime.date.today()}"
        ),
        types.InlineKeyboardButton(
            ("for the week"), callback_data=f"{button_type}:created_at__range={week_ago},{datetime.date.today()}"
        )
    ]
    markup.add(*row_1)
    logger.debug(f"markup after days: {markup.to_dict()}")
    if button_type == "expense":
        one_month = today - relativedelta(months=1)
        three_months = today - relativedelta(months=3)
        six_months = today - relativedelta(months=6)
        one_year = today - relativedelta(years=1)
        row_2 = [
            types.InlineKeyboardButton(
                ("for the month"), callback_data=f"{button_type}:created_at={one_month}"
            ),
            types.InlineKeyboardButton(
                ("for 3 months"), callback_data=f"{button_type}:created_at__range={three_months},{datetime.date.today()}"
            ),
            types.InlineKeyboardButton(
                ("for 6 months"), callback_data=f"{button_type}:created_at__range={six_months},{datetime.date.today()}"
            )
        ]
        markup.add(*row_2)
        row_3 = [
            types.InlineKeyboardButton(
                ("for the year"), callback_data=f"{button_type}:created_at__range={one_year},{datetime.date.today()}"
            ),
            types.InlineKeyboardButton(
                ("for all time"), callback_data=f"{button_type}:")
        ]
        markup.add(*row_3)
    logger.debug(f"markup after year: {markup.to_dict()}")
    return markup

def category_sum_buttons(categories_sum, receipt_period, context):
    logger.info("Starting to form the categories_sum buttons")
    markup = types.InlineKeyboardMarkup()
    buttons_in_a_row = []
    len_buttons_list = len(categories_sum)
    for category_sum in categories_sum:
        logger.info(f"category_sum = {category_sum}")
        total_price_float = int_to_float_str(category_sum["total_price"])
        category_sum["total_price"] = total_price_float
        category_id = None
        for category_with_id in context.existing_categories_with_id:
            if category_with_id["name"] == category_sum["category"]:
                category_id = category_with_id['id']
                break
        callback_data = f'categ_sum:{category_id},{receipt_period}'
        logger.info(f"callback_data = {callback_data}")
        logger.info(f"len(callback_data) should be less then 64: {len(callback_data)}")
        # buttons_in_a_row.append(types.InlineKeyboardButton(
        #     f"{category_sum['category']}: {category_sum['total_price']} €",
        #     callback_data=f'categ_sum:category={category_id},range={receipt_period}')
        # )
        buttons_in_a_row.append(types.InlineKeyboardButton(
            f"{category_sum['category']}: {category_sum['total_price']} €",
            callback_data=callback_data)
        )
        if len(buttons_in_a_row) == 2:
            markup.row(*buttons_in_a_row)
            buttons_in_a_row = []
        elif (len(buttons_in_a_row) == 1) and (len_buttons_list == 1):
            markup.add(*buttons_in_a_row)
        len_buttons_list -= 1
    return markup