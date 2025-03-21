import base64
import logging
import os

from .file_saving import file_saving
from .receipt_open_ai_mini import open_ai_mini
from .receipt_open_ai_turbo import open_ai_turbo
from tesserocr import PyTessBaseAPI, PSM
from PIL import Image

# print(tesserocr.get_languages())  # prints tessdata path and list of available languages
TESSDATA_PREFIX = "/usr/share/tesseract-ocr/5/tessdata/"
UPLOAD_FOLDER = "uploaded_receipts"


def receipt_ocr(image):
    try:
        logging.info(f"Receipt recognition launched")
        with PyTessBaseAPI(path = TESSDATA_PREFIX, lang='fin') as api:
            # psm = PSM.SINGLE_COLUMN
            api.SetImage(image)
            text = api.GetUTF8Text()
        logging.info(f"Receipt was recognized successfully")
    except Exception as e:
        logging.error(f"Recognition error: {e}")
        return None

    return text


def recognition_ocr_mini(file_name):
    filepath = os.path.join(UPLOAD_FOLDER, f"{file_name}.jpg")
    try:
        logging.info(f"Opening image from: {filepath}")
        image = Image.open(filepath)
    except Exception as e:
        logging.error(f"Image opening error: {e}")
        return None
    text = receipt_ocr(image)
    file_saving(UPLOAD_FOLDER, file_name, text, "w", "ocr")

    # json_text = open_ai_request(text)
    # file_saving(UPLOAD_FOLDER, file_name, json_text, "w", "ai")


def recognition_turbo(file_name):
    filepath = os.path.join(UPLOAD_FOLDER, f"{file_name}.jpg")
    try:
        logging.info(f"Opening image from: {filepath}")
        with open(filepath, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        logging.error(f"Image opening error: {e}")
        return None
    json_text = open_ai_turbo(base64_image)
    file_saving(UPLOAD_FOLDER, file_name, json_text, "w", "ai")