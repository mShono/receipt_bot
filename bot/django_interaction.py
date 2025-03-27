import logging

import json

import os
from dotenv import load_dotenv
import requests

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

def check_products_existence(filepath):
    present_in_database = []
    absent_in_database = []

    try:
        logger.info(f"Opening the json ai response {filepath}")
        with open(filepath) as f:
            shopping_list = json.load(f)
        logger.info(f"file_content = {shopping_list}")
    except Exception as e:
        logger.error(f"Opening the json file with products failed: {e}")
        return None
    for list_position in shopping_list:
        try:
            product = list_position["name"]
        except Exception as e:
            logger.error(f"Reading the json file with products failed: {e}")
            return None
        logger.info("Start sending requests to Django database")
        try:
            response = requests.get(f"{DJANGO_API_URL}product/?search={product}", headers=headers)
            if response.status_code == 200:
                present_in_database.append(list_position)
            elif response.status_code == 404:
                absent_in_database.append(list_position)
            else:
                logger.info(f"Received an unpredictable response from Django database: {response.status_code}")
                logger.info(f"response.text = {response.text}")
        except Exception as e:
            logger.error(f"Reading the json file with products failed: {e}")
            return None
    logger.info(f"present_in_database = {present_in_database}")
    logger.info(f"absent_in_database = {absent_in_database}")
    return present_in_database, absent_in_database



# filepath = "/home/masher/development/receipt_bot/uploaded_receipts/382807642_receipt_product_ai.json"
# check_products_existence(filepath)
