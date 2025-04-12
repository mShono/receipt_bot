import logging

import json

import os
from dotenv import load_dotenv
import requests

from .conversions import float_to_int
from .file_operations import response_saving
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
RESPONSE_FOLDER = "database_responses"


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
            response_saving(RESPONSE_FOLDER, f"{endpoint}_get_data", response.text)
            return False, None
    except Exception as e:
        logger.error(f"Reading the json file with {endpoint} failed: {e}")
        response_saving(RESPONSE_FOLDER, f"{endpoint}_get_data", response.text)
        raise e


def check_existent_categories(context):
    logger.info("Checking the categories existing in the database")
    try:
        response = requests.get(f"{DJANGO_API_URL}category/", headers=headers)
        if response.status_code != 200:
            logger.info(f"Received an unpredictable response from Django database: {response.status_code}")
            response_saving(RESPONSE_FOLDER, f"check_existent_categories", response.text)
            return None
    except Exception as e:
        logger.error(f"The request for database for existent categories failed: {e}")
        response_saving(RESPONSE_FOLDER, f"check_existent_categories", response.text)
        return None
    context.existing_categories.clear()
    context.existing_categories_with_id.clear()
    try:
        context.existing_categories_with_id.extend(json.loads(response.text))
        for category in json.loads(response.text):
            context.existing_categories.append(category["name"])
        logger.info(f"existing_categories = {context.existing_categories}")
        logger.info(f"existing_categories_with_id = {context.existing_categories_with_id}")
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
            new_item = response.json()
            return True, new_item["id"]
        else:
            logger.info(f"Posting {endpoint} data \"{data}\" to the database was unsuccessfull")
            logger.info(f"response.status_code = {response.status_code}")
            response_saving(RESPONSE_FOLDER, f"{endpoint}_post_data", response.text)
            return False, None
    except Exception as e:
        logger.error(f"Error posting {endpoint} data: {e}")
        response_saving(RESPONSE_FOLDER, f"{endpoint}_post_data", response.text)
        raise e

# filepath = "/home/masher/development/receipt_bot/uploaded_receipts/382807642_receipt_product_ai.json"
# check_products_existence(filepath)
