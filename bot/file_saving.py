import logging
import os


def file_saving(UPLOAD_FOLDER, file_name, saving_item, mode, recognition_stage):
    upload_dir = os.path.join(os.getcwd(), UPLOAD_FOLDER)
    error = "File saving error: "

    if recognition_stage == "image":
        launch = "Image saving launched"
        ending = "Image saved successfully"
        filepath = f"{os.path.join(upload_dir, file_name)}.jpg"
    if recognition_stage == "ocr":
        launch = "File saving launched"
        ending = "Receipt saved successfully"
        filepath = f"{os.path.join(upload_dir, file_name)}.txt"
    if recognition_stage == "ai":
        launch = "Identified product saving in a file launched"
        ending = "Identified products saved successfully"
        filepath = f"{os.path.join(upload_dir, file_name)}_ai.json"

    try:
        logging.info(launch)
        with open(filepath, mode) as file:
            file.write(saving_item)
            logging.info(f"{ending}, {filepath}")
    except Exception as e:
        logging.error(f"{error}, {e}")
        return None
