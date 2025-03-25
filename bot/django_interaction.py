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
    logger.info(f"filepath = {filepath}")
    # with open(filepath, "w") as f:

    try:
        with open(filepath) as f:
            file_content = json.load(f)
        logger.info(f"file_content = {file_content}")
    except Exception as e:
        logging.error(f"Reading the json file with products failed: {e}")
        return None
    # response = requests.get(f"{DJANGO_API_URL}product/", headers=headers)


# filepath = "/home/masher/development/receipt_bot/uploaded_receipts/382807642_receipt_product_ai.json"
# check_products_existence(filepath)
