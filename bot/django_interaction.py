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


def get_data_info(endpoint, data):
    logger.info(f"Checking the existance of the {endpoint} \"{data}\" in the database")
    try:
        response = requests.get(f"{DJANGO_API_URL}{endpoint}/?search={data}", headers=headers)
        if response.status_code == 200:
            logger.info(f"\"{data}\" is in the database")
            data_info = json.loads(response.text)
            return True, data_info[0]
        elif response.status_code == 404:
            logger.info(f"\"{data}\" is not in the database")
            return False, None
        else:
            logger.info(f"Received an unpredictable response from Django database: {response.status_code}")
            return False, None
    except Exception as e:
        logger.error(f"Reading the json file with products failed: {e}")
        raise e


def check_existent_categories():
    logger.info("Checking the categories existing in the database")
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


def post_data_info(endpoint, data):
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
