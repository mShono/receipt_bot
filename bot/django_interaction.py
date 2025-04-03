import logging

import json

import os
from dotenv import load_dotenv
import requests

from .conversions import float_to_int
from . import state

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()

headers = {
    "Authorization": f"Token {os.getenv("DJANGO_BOT_TOKEN")}",
    "Content-Type": "application/json",
}

DJANGO_API_URL = os.getenv("DJANGO_API_URL")
UPLOAD_FOLDER = "uploaded_receipts"


def file_opening(filepath):
    try:
        logger.info(f"Opening the json ai response {filepath}")
        with open(filepath) as f:
            shopping_list = json.load(f)
        logger.info(f"file_content = {shopping_list}")
        return shopping_list
    except Exception as e:
        logger.error(f"Opening the json file with products failed: {e}")
        raise e


def check_list_of_products_existence(filepath):
    shopping_list = file_opening(filepath)
    logger.info("Start sending requests to Django database")
    for list_position in shopping_list:
        try:
            product = list_position["name"]
            price = list_position["price"]
        except Exception as e:
            logger.error(f"Reading the json file with products failed: {e}")
            raise e
        integer_price = float_to_int(price)
        list_position["price"] = integer_price
        try:
            response = requests.get(f"{DJANGO_API_URL}product/?search={product}", headers=headers)
            if response.status_code == 200:
                state.PRODUCTS_PRESENT_IN_DATABASE.append(list_position)
            elif response.status_code == 404:
                state.PRODUCTS_ABSENT_IN_DATABASE.append(list_position)
            else:
                logger.info(f"Received an unpredictable response from Django database: {response.status_code}")
        except Exception as e:
            logger.error(f"An unexpected error occurred when requesting Django: {e}")
            raise e
    logger.info(f"PRODUCTS_PRESENT_IN_DATABASE = {state.PRODUCTS_PRESENT_IN_DATABASE}")
    logger.info(f"PRODUCTS_ABSENT_IN_DATABASE = {state.PRODUCTS_ABSENT_IN_DATABASE}")
    return


def check_one_product_existence(product):
    logger.info(f"Checking the existance of the product \"{product}\" in the database")
    try:
        response = requests.get(f"{DJANGO_API_URL}product/?search={product}", headers=headers)
        if response.status_code == 200:
            # product_info = []
            logger.info(f"The product \"{product}\" is in the database")
            # product_info.extend(json.loads(response.text))
            product_info = json.loads(response.text)
            return True, product_info[0]
        elif response.status_code == 404:
            logger.info(f"The product \"{product}\" is not in the database")
            return False, None
        else:
            logger.info(f"Received an unpredictable response from Django database: {response.status_code}")
            return False, None
    except Exception as e:
        logger.error(f"Reading the json file with products failed: {e}")
        raise e


def check_existent_categories():
    try:
        response = requests.get(f"{DJANGO_API_URL}category/", headers=headers)
        if response.status_code == 200:
            logger.info(f"EXISTING_CATEGORIES_WITH_ID = {state.EXISTING_CATEGORIES_WITH_ID}")
        else:
            logger.info(f"Received an unpredictable response from Django database: {response.status_code}")
    except Exception as e:
        logger.error(f"The request for database for existent categories failed: {e}")
        return None
    state.EXISTING_CATEGORIES.clear()
    state.EXISTING_CATEGORIES_WITH_ID.clear()
    try:
        state.EXISTING_CATEGORIES_WITH_ID.extend(json.loads(response.text))
        for category in json.loads(response.text):
            state.EXISTING_CATEGORIES.append(category["name"])
        logger.info(f"EXISTING_CATEGORIES = {state.EXISTING_CATEGORIES}")
    except Exception as e:
        logger.error(f"Converting response.text with existant categories to json failed: {e}")
        raise e
    return


def post_category_product(endpoint, data):
    logger.info(f"Posting to the endpoint \"{endpoint}\" the following data \"{data}\"")
    url = f"{DJANGO_API_URL}{endpoint}/"
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            logger.info(f"The {endpoint} data \"{data}\" was successfully posted to the database")
            logger.info(f"response.text = {response.text}")
            new_item = response.json()
            return True, new_item["id"]
        else:
            logger.info(f"Posting {endpoint} data \"{data}\" to the database was unsuccessfull")
            logger.info(f"response.status_code = {response.status_code}")
            return False, None
    except Exception as e:
        logger.error(f"Error posting {endpoint} data: {e}")
        raise e

def get_user_info(username):
    logger.info(f"Getting the user's id from the database")
    try:
        response = requests.get(f"{DJANGO_API_URL}users/?search={username}", headers=headers)
        logger.info(f"username = {username}")
        if response.status_code == 200:
            logger.info(f"The \"{username}\" info successfully received from the database")
        elif response.status_code == 404:
            logger.info(f"The user \"{username}\" is not in the database")
            return False
        else:
            logger.info(f"Received an unpredictable response from Django database: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error geting the user data from the database: {e}")
        raise e
    try:
        for user_info in response.json():
            logger.info(f"user_info = {user_info}")
            logger.info(f"user_info['id'] = {user_info['id']}")
            return user_info["id"]
    except Exception as e:
        logger.error(f"Reading the json file with products failed: {e}")
        raise e


def post_expense(data):

    logger.info(f"Posting to the endpoint 'expense' the following data")
    url = f"{DJANGO_API_URL}expense/"
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            logger.info(f"The expense data \"{data}\" was successfully posted to the database")
            new_expense = response.json()
            return True, new_expense["id"]
        else:
            logger.info(f"Posting expense data \"{data}\" to the database was unsuccessfull")
            logger.info(f"response.status_code = {response.status_code}")
            return False, None
    except Exception as e:
        logger.error(f"Error posting expense data: {e}")
        raise e

# filepath = "/home/masher/development/receipt_bot/uploaded_receipts/382807642_receipt_product_ai.json"
# check_products_existence(filepath)
