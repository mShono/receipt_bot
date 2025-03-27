import base64
import logging
import os

from .file_saving import file_saving
from .receipt_open_ai_mini import open_ai_mini
from .receipt_open_ai_turbo import image_recognition_turbo, product_recognition_turbo
from tesserocr import PyTessBaseAPI, PSM
from PIL import Image

# print(tesserocr.get_languages())  # prints tessdata path and list of available languages
TESSDATA_PREFIX = "/usr/share/tesseract-ocr/5/tessdata/"
UPLOAD_FOLDER = "uploaded_receipts"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def receipt_ocr(image):
    try:
        logger.info(f"Receipt recognition launched")
        with PyTessBaseAPI(path = TESSDATA_PREFIX, lang='fin') as api:
            # psm = PSM.SINGLE_COLUMN
            api.SetImage(image)
            text = api.GetUTF8Text()
        logger.info(f"Receipt was recognized successfully")
    except Exception as e:
        logger.error(f"Recognition error: {e}")
        return None

    return text


def recognition_ocr_mini(file_name):
    filepath = os.path.join(UPLOAD_FOLDER, f"{file_name}.jpg")
    try:
        logger.info(f"Opening image from: {filepath}")
        image = Image.open(filepath)
    except Exception as e:
        logger.error(f"Image opening error: {e}")
        return None
    text = receipt_ocr(image)
    file_saving(UPLOAD_FOLDER, file_name, text, "w", "ocr")

    # json_text = open_ai_request(text)
    # file_saving(UPLOAD_FOLDER, file_name, json_text, "w", "ai")


def check_openai_response(text):
    logger.info("Сhecking if AI has recognized the image")
    lines = text.splitlines()

    try:
        if lines and lines[1]:
            lines = lines[1:]
            logger.info("Image recognition was successful")
            return "\n".join(lines)

    except Exception as e:
        logger.error(f"Text splitting for lines error: {e}")
        return None


def clean_openai_response(text):
    logger.info("Geting rid of the markers in AI response")
    lines = text.splitlines()

    if lines and lines[0].strip() == "```json":
        lines = lines[1:]
    else:
        logger.info("There were no markers in AI response")
        return None

    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)


def recognition_turbo(file_name):
    filepath = os.path.join(UPLOAD_FOLDER, f"{file_name}.jpg")
    try:
        logger.info(f"Opening image from: {filepath}")
        with open(filepath, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        logger.error(f"Image opening error: {e}")
        return None
    recognized_image = image_recognition_turbo(base64_image)
    checked_recognized_image = check_openai_response(recognized_image)
    if checked_recognized_image == None:
        logger.info(f"Ai wasn't able to recognize the image, response: {recognized_image}")
        file_saving(UPLOAD_FOLDER, file_name, recognized_image, "w", "image_ai")
    else:
        file_saving(UPLOAD_FOLDER, file_name, checked_recognized_image, "w", "image_ai")
        logger.info("Making the second request to AI to find the products")
        json_text = product_recognition_turbo(checked_recognized_image)
        cleaned_text = clean_openai_response(json_text)
        _, filepath = file_saving(UPLOAD_FOLDER, file_name, cleaned_text, "w", "product_ai")
    return filepath