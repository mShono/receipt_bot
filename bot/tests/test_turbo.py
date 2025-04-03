import base64
import logging
import os

from ..receipt_open_ai_turbo import open_ai_turbo
from ..file_operations import file_saving
from PIL import Image

RECEIPT_PHOTO_PATH = os.path.join(os.getcwd(), "test_receipts")
RECOGNIZED_RECEIPT_PATH = os.path.join(os.getcwd(), "recogized_test_receipts_turbo")
UPLOAD_FOLDER = "recogized_test_receipts_turbo"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


RECEIPT_TO_TEXTS = {
    "K_market_2025-03-18_2_ai": [
        "porsa"
    ],
    "K_market_2025-03-18_ai":[
        "tomaatti", "ksylitoli", "täysksylit"
    ],
    "Lidl_kuitti_2025_03_18_ai":[
        "Kurkku", "Tomaatti", "maito", "Kaurajuoma", "raejuusto",
        "Kiinankaali", "Porkkana", "Paprika", "Keräkaali", "Inkivääri"
    ]
}


def base64_encode(image):
    try:
        logger.info(f"Opening {image.name} from: {RECEIPT_PHOTO_PATH}")
        with open(image, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        logger.error(f"{image.name} opening error: {e}")
        return None


def test_turbo():
    result_dict = {}
    entry_names = []

    for entry in os.scandir(RECEIPT_PHOTO_PATH):  
        if entry.is_file():
            base64_image = base64_encode(entry)
            text = open_ai_turbo(base64_image)

            entry_name, _ = entry.name.split(".")
            entry_name_ai = f"{entry_name}_ai"
            entry_names.append(entry_name_ai)

            file_saving(UPLOAD_FOLDER, entry_name, text, "w", "ai")

    #         result_dict[entry_name_ai] = {}

    #         expected_texts = RECEIPT_TO_TEXTS[entry_name_ai]
    #         for txt in expected_texts:
    #             if txt in text:
    #                 result_dict[entry_name_ai][txt] = True
    #             else:
    #                 result_dict[entry_name_ai][txt] = False
    # logger.info(f"result_dict = {result_dict}")
    # for entry_name in entry_names:
    #     for key in result_dict[entry_name].keys():
    #         assert result_dict[entry_name][key] == True

#  test_case prametrised (список аргументов)

test_turbo()

# def test_without_ai():
#     result_dict = {}
#     entry_names = []

#     for entry in os.scandir(RECOGNIZED_RECEIPT_PATH):  
#         if entry.is_file():
#             with open(entry, 'r') as file:
#                 text = file.read()

#             entry_name, _ = entry.name.split(".")
#             entry_name_ai = f"{entry_name}_ai"
#             entry_names.append(entry_name_ai)

#             result_dict[entry_name_ai] = {}

#             expected_texts = RECEIPT_TO_TEXTS[entry_name]
#             for txt in expected_texts:
#                 if txt in text:
#                     result_dict[entry_name_ai][txt] = True
#                 else:
#                     result_dict[entry_name_ai][txt] = False
#     logger.info(f"result_dict = {result_dict}")
#     for entry_name in entry_names:
#         for key in result_dict[entry_name].keys():
#             assert result_dict[entry_name][key] == True