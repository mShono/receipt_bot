import json
import logging
import os

from ..receipt_ocr_test import receipt_ocr
from ..file_saving import file_saving
from PIL import Image
from tesserocr import PSM

RECEIPT_PHOTO_PATH = os.path.join(os.getcwd(), "test_receipts")
UPLOAD_FOLDER = "recogized_test_receipts_ocr"
UPLOAD_DIR = os.path.join(os.getcwd(), UPLOAD_FOLDER)
PSM = [
    PSM.AUTO_OSD, PSM.AUTO_ONLY, PSM.AUTO, PSM.SINGLE_COLUMN, 
    PSM.SINGLE_BLOCK, PSM.SPARSE_TEXT,
]


RECEIPT_TO_TEXTS = {
    "K_market_2025-03-18_2": [
        "porsa"
    ],
    "K_market_2025-03-18":[
        "tomaatti", "ksylitoli", "täysksylit"
    ],
    "Lidl_kuitti_2025_03_18":[
        "Kurkku", "Tomaatti", "maito", "Kaurajuoma", "raejuusto",
        "Kiinankaali", "Porkkana", "Paprika", "Keräkaali", "Inkivääri"
    ]
}


def image_opening(image):
    try:
        logging.info(f"Opening {image.name} from: {RECEIPT_PHOTO_PATH}")
        return Image.open(image)
    except Exception as e:
        logging.error(f"{image.name} opening error: {e}")
        return None

def test_ocr():
    psm = [
        "auto_osd", "auto_only", "auto", "single_column",
        "single_block", "sparse_text",
    ]
    result_dict = {}
    entry_names = []

    for entry in os.scandir(RECEIPT_PHOTO_PATH):
        image = image_opening(entry)
        counter = 0
        for mode in PSM:
            text = receipt_ocr(image, mode)

            entry_name, _ = entry.name.split(".")
            entry_name_psm = f"{entry_name}_{psm[counter]}"
            logging.info(f"entry_name_psm = {entry_name_psm}")
            counter += 1
            # entry_name_psm_ocr = f"{entry_name_psm}_ocr"
            entry_names.append(entry_name_psm)
            logging.info(f"entry_names = {entry_names}")

            file_saving(UPLOAD_FOLDER, entry_name_psm, text, "w", "ocr")

            result_dict[entry_name_psm] = {}
            logging.info(f"result_dict = {result_dict}")

            expected_texts = RECEIPT_TO_TEXTS[entry_name]
            logging.info(f"expected_texts = {expected_texts}")
            for txt in expected_texts:
                txt_lower = txt.lower()
                if txt_lower in text:
                    logging.info(f"Texts compairing launched")
                    logging.info(f"txt_lower = {txt_lower}")
                    result_dict[entry_name_psm][txt_lower] = True
                else:
                    result_dict[entry_name_psm][txt_lower] = False

    with open(f"{os.path.join(UPLOAD_DIR, "result_dict")}.py", "w") as file:
        file.write(json.dumps(result_dict))
    logging.info(f"result_dict = {result_dict}")
    for entry_name in entry_names:
        for key in result_dict[entry_name].keys():
            assert result_dict[entry_name][key] == True

#  test_case prametrised (список аргументов)