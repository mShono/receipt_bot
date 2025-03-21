import logging

from tesserocr import PyTessBaseAPI, PSM

TESSDATA_PREFIX = "/usr/share/tesseract-ocr/5/tessdata/"


def receipt_ocr(image, psm):
    try:
        logging.info(f"Receipt recognition launched")
        with PyTessBaseAPI(path = TESSDATA_PREFIX, psm = psm, lang='fin') as api:
            api.SetImage(image)
            text = api.GetUTF8Text()
        logging.info(f"Receipt was recognized successfully")
    except Exception as e:
        logging.error(f"Recognition error: {e}")
        return None

    return text
