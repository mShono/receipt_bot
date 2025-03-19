import logging
import os

UPLOAD_DIR = os.path.join(os.getcwd(), "uploaded_receipts")

def file_saving(file_name, text, mode, recognition_stage):
    error = "File saving error: "

    if recognition_stage == "image":
        launch = "Image saving launched"
        ending = "Image saved successfully"
        filepath = f"{os.path.join(UPLOAD_DIR, file_name)}.jpg"
    if recognition_stage == "ocr":
        launch = "File saving launched"
        ending = "Receipt saved successfully"
        filepath = f"{os.path.join(UPLOAD_DIR, file_name)}_4.txt"
    if recognition_stage == "ai":
        launch = "Identified product saving in a file launched"
        ending = "Identified products saved successfully"
        filepath = f"{os.path.join(UPLOAD_DIR, file_name)}_4_openAI.json"

    try:
        logging.info(launch)
        with open(filepath, mode) as file:
            file.write(text)
            logging.info(f"{ending}, {filepath}")
    except Exception as e:
        logging.error(f"{error}, {e}")
        return None
