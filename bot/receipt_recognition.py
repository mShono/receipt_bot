import logging
import os

from file_saving import file_saving
from receipt_open_ai import open_ai_request
from tesserocr import PyTessBaseAPI, PSM
from PIL import Image

# print(tesserocr.get_languages())  # prints tessdata path and list of available languages
TESSDATA_PREFIX = "/usr/share/tesseract-ocr/5/tessdata/"
UPLOAD_DIR = os.path.join(os.getcwd(), "uploaded_receipts")


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


def recognition(file_name):
    filepath = os.path.join(UPLOAD_DIR, f"{file_name}.jpg")
    try:
        logging.info(f"Opening image from: {filepath}")
        image = Image.open(filepath)
    except Exception as e:
        logging.error(f"Image opening error: {e}")
        return None
    text = receipt_ocr(image)
    file_saving(file_name, text, "w", "ocr")

    # json_text = open_ai_request(text)
    # file_saving(file_name, json_text, "w", "ai")
