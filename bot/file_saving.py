import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
        return True
    except Exception as e:
        logger.error(f"{error}, {e}")
        return None
