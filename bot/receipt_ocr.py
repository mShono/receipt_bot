import logging
import os
from tesserocr import PyTessBaseAPI, PSM
from PIL import Image

# print(tesserocr.get_languages())  # prints tessdata path and list of available languages

TESSDATA_PREFIX = "/usr/share/tesseract-ocr/5/tessdata/"
UPLOAD_DIR = os.path.join(os.getcwd(), "uploaded_receipts")

def receipt_ocr(receipt_photo_path, file_name):
    try:
        logging.info(f"Opening image from: {receipt_photo_path}")
        image = Image.open(receipt_photo_path)
    except Exception as e:
        logging.error(f"Image opening error: {e}")
        return None
    try:
        logging.info(f"Receipt recognition launched")
        with PyTessBaseAPI(path = TESSDATA_PREFIX, psm = PSM.SINGLE_COLUMN) as api:
            api.SetImage(image)
            text = api.GetUTF8Text()
        logging.info(f"Receipt was recognized successfully")
    except Exception as e:
        logging.error(f"Recognition error: {e}")
        return None
    try:
        logging.info(f"File saving launched")
        filepath = os.path.join(UPLOAD_DIR, file_name)
        with open(f"{filepath}_6.txt", "w") as file:
            file.write(text)
            logging.info(f"Receipt saved successfully")
    except Exception as e:
        logging.error(f"File saving error: {e}")
        return None

    return text
