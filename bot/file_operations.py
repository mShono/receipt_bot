import logging
import json
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def file_opening(filepath):
    try:
        logger.info(f"Opening the json ai response {filepath}")
        with open(filepath) as f:
            shopping_list = json.load(f)
        logger.info(f"file_content = {shopping_list}")
        return shopping_list
    except Exception as e:
        logger.error(f"Opening the json file with products failed: {e}")
        raise e


def file_saving(UPLOAD_FOLDER, file_name, saving_item, mode, recognition_stage):
    upload_dir = os.path.join(os.getcwd(), UPLOAD_FOLDER)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir) 
        logger.info(f"Created a folder {UPLOAD_FOLDER} at {os.getcwd()}")
    error = "File saving error: "

    if recognition_stage == "image":
        launch = "Image saving launched"
        ending = "Image saved successfully"
        filepath = f"{os.path.join(upload_dir, file_name)}.jpg"
    if recognition_stage == "ocr":
        launch = "File saving launched"
        ending = "Receipt saved successfully"
        filepath = f"{os.path.join(upload_dir, file_name)}.txt"
    if recognition_stage == "image_ai":
        launch = "Recognized text saving in a file launched"
        ending = "Recognized text saved successfully"
        filepath = f"{os.path.join(upload_dir, file_name)}_image_ai.txt"
    if recognition_stage == "product_ai":
        launch = "Identified product saving in a file launched"
        ending = "Identified products saved successfully"
        filepath = f"{os.path.join(upload_dir, file_name)}_product_ai.json"

    try:
        logger.info(launch)
        with open(filepath, mode) as file:
            file.write(saving_item)
            logger.info(f"{ending}, {filepath}")
        return True, filepath
    except Exception as e:
        logger.error(f"{error}, {e}")
        return None

def response_saving(RESPONSE_FOLDER, file_name, saving_item):
    upload_dir = os.path.join(os.getcwd(), RESPONSE_FOLDER)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir) 
        logger.info(f"Created a folder {RESPONSE_FOLDER} at {os.getcwd()}")

    error = "File saving error: "
    filepath = f"{os.path.join(upload_dir, file_name)}.txt"

    try:
        logger.info("Response saving launched")
        with open(filepath, "w") as file:
            file.write(saving_item)
            logger.info(f"Response saved successfully, {filepath}")
        return True, filepath
    except Exception as e:
        logger.error(f"{error}, {e}")
        return None
