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
        return None


def check_list_of_products_existence(filepath):
    shopping_list = file_opening(filepath)
    logger.info("Start sending requests to Django database")
    for list_position in shopping_list:
        try:
            product = list_position["name"]
            price = list_position["price"]
        except Exception as e:
            logger.error(f"Reading the json file with products failed: {e}")
            return None
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
                logger.info(f"response.text = {response.text}")
        except Exception as e:
            logger.error(f"An unexpected error occurred when requesting Django: {e}")
            return None
    logger.info(f"PRODUCTS_PRESENT_IN_DATABASE = {state.PRODUCTS_PRESENT_IN_DATABASE}")
    logger.info(f"PRODUCTS_ABSENT_IN_DATABASE = {state.PRODUCTS_ABSENT_IN_DATABASE}")
    return


def check_one_product_existence(product):
    logger.info(f"Checking the existance of the product \"{product}\" in the database")
    try:
        response = requests.get(f"{DJANGO_API_URL}product/?search={product}", headers=headers)
        if response.status_code == 200:
            logger.info(f"The product \"{product}\" is in the database")
            return True
        elif response.status_code == 404:
            logger.info(f"The product \"{product}\" is not in the database")
            return False
        else:
            logger.info(f"Received an unpredictable response from Django database: {response.status_code}")
            logger.info(f"response.text = {response.text}")
            return False
    except Exception as e:
        logger.error(f"Reading the json file with products failed: {e}")
        return None


def check_existent_categories():
    try:
        response = requests.get(f"{DJANGO_API_URL}category/", headers=headers)
        if response.status_code == 200:
            state.EXISTING_CATEGORIES_WITH_ID.clear()
            state.EXISTING_CATEGORIES_WITH_ID.extend(json.loads(response.text))
            logger.info(f"EXISTING_CATEGORIES_WITH_ID = {state.EXISTING_CATEGORIES_WITH_ID}")
        elif response.status_code == 404:
            logger.info("There are not any categories in a database")
            logger.info(f"response.text = {response.text}")
        else:
            logger.info(f"Received an unpredictable response from Django database: {response.status_code}")
            logger.info(f"response.text = {response.text}")
    except Exception as e:
        logger.error(f"The request for database for existent categories failed: {e}")
        return None
    state.EXISTING_CATEGORIES.clear()
    try:
        for category in json.loads(response.text):
            state.EXISTING_CATEGORIES.append(category["name"])
        logger.info(f"EXISTING_CATEGORIES = {state.EXISTING_CATEGORIES}")
    except Exception as e:
        logger.error(f"Converting response.text with existant categories to json failed: {e}")
    return


def post_category_product(endpoint, data):
    logger.info(f"Posting to the endpoint \"{endpoint}\" the following data \"{data}\"")
    url = f"{DJANGO_API_URL}{endpoint}/"
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            logger.info(f"The {endpoint} data \"{data}\" was successfully posted to the database")
            return True
        elif response.status_code == 404:
            logger.info(f"Posting {endpoint} data \"{data}\" to the database was unsuccessfull")
            return False
        else:
            logger.info(f"Received an unpredictable response from Django database: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Reading the json file with products failed: {e}")
        return None

# filepath = "/home/masher/development/receipt_bot/uploaded_receipts/382807642_receipt_product_ai.json"
# check_products_existence(filepath)
