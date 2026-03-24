import os
import re
import cv2
import easyocr
import logging

_easyocr_reader = None

def _get_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        _easyocr_reader = easyocr.Reader(['en'])
    return _easyocr_reader
import pandas as pd
from typing import List
from pdf2image import convert_from_path
import pytesseract
pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_PATH', 'tesseract')
from consts import *
from save_data import append_data
from verification import verify_data_results

def extract_file_paths_from_excel(excel_path: str = DATABASE_FILE_NAME, sheet_name: str = 0) -> List[str]:
    """
    Load an Excel file into a pandas DataFrame, extract values from the 'file path' column,
    and return them as a list of strings.

    @param excel_path: Path to the Excel file.
    @param sheet_name: Sheet name or index (default is 0, the first sheet).
    @return: List of strings from the 'file path' column.
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name, usecols=["scan_path"])
        return df['file path'].dropna().astype(str).tolist()
    except Exception as e:
        raise []

def convert_pdf_to_jpegs(file_path: str) -> [str]:
    import pathlib
    try:
        pages = convert_from_path(file_path, poppler_path=os.environ.get('POPPLER_PATH', None))
    except Exception as e:
        msg = str(e)
        if 'page count' in msg.lower() or 'pdfinfo' in msg.lower():
            raise ValueError(
                "Cannot read this PDF — it may be encrypted, password-protected, or use an unsupported format. "
                "Please open the PDF in Adobe Acrobat or a PDF viewer and re-save it as a standard PDF before uploading."
            ) from e
        raise
    images_path = []

    for i, page in enumerate(pages):
        img_path = file_path.replace('.pdf', f"_page_{i+1}.jpg")
        page.save(img_path, "JPEG")
        images_path.append(img_path)

    return images_path

def group_easyocr_results_by_row(ocr_results, y_threshold=15):
    """
    Groups EasyOCR results into rows, sorting each row's items from left to right.

    Parameters:
        ocr_results (list): List of OCR results from EasyOCR, where each result is
            [bbox, text, confidence]. 'bbox' is a list of four points [[x1, y1], [x2, y2], [x3, y3], [x4, y4]].
        y_threshold (int): Maximum vertical distance (in pixels) between detections to consider them in the same row.

    Returns:
        List of rows, where each row is a list of tuples (bbox, text, confidence) sorted by the left x coordinate.
    """
    # First, compute the average y coordinate for each detection
    detections = []
    for detection in ocr_results:
        bbox, text, conf = detection
        avg_y = sum(point[1] for point in bbox) / len(bbox)
        detections.append((bbox, text, conf, avg_y))

    # Sort detections by the average y coordinate (top-to-bottom)
    detections.sort(key=lambda item: item[3])

    # Group detections that are on the same row (i.e. close in the y axis)
    rows = []
    current_row = []
    current_row_y = None

    for detection in detections:
        bbox, text, conf, avg_y = detection
        if current_row_y is None:
            # start first row
            current_row_y = avg_y
            current_row.append(detection)
        elif abs(avg_y - current_row_y) <= y_threshold:
            # Same row: add the detection
            current_row.append(detection)
        else:
            # New row: sort the previous row by left-most x coordinate and start a new row group
            current_row.sort(key=lambda item: min(pt[0] for pt in item[0]))
            rows.append(current_row)
            current_row = [detection]
            current_row_y = avg_y

    # Append the last row (if not empty) after sorting
    if current_row:
        current_row.sort(key=lambda item: min(pt[0] for pt in item[0]))
        rows.append(current_row)

    # Remove the average y from the result for clarity
    organized_rows = '\n'.join([' '.join([text for _, text, _, _ in row]) for row in rows])
    return organized_rows

def easyocr_get_recognized_text(image_path, threshold=170):
    text = ""

    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    reader = _get_easyocr_reader()
    results = reader.readtext(binary)

    text += group_easyocr_results_by_row(results)
    text += "\n"

    return text

def tesseract_get_recognized_text(image_path, threshold=170):
    text = ""

    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    text += pytesseract.image_to_string(binary)
    text += "\n"

    return text

def analyze_images(images_path, get_text_func, base_threshold_level=170, num_of_thresholds=40):

    best_threshold = ({}, 0, "", -1)

    for i in range(base_threshold_level + 1, base_threshold_level + num_of_thresholds + 1, 3):
        text = ""
        for image_path in images_path:
            text += get_text_func(image_path, i)

        data, value, num = extract_text(text)

        if value > best_threshold[1]:
            best_threshold = (data, value, text, num)
            print(i, value, num)
            if value == num:
                break

    return best_threshold

def add_format_parameters(text, format):
    parameters = {}

    if format == FORMATS.NEW.FULL_WITH_POST or format == FORMATS.NEW.FULL_WITHOUT_POST or format == FORMATS.NEW.ONLY_SPIROMETRY_WITH_POST or format == FORMATS.NEW.ONLY_SPIROMETRY_WITHOUT_POST:
        if re.findall(WITH_POST_IDENTIFIER, text, re.IGNORECASE):
            parameters.update(NEW_ONLY_SPIROMETRY_WITH_POST_SPECIFIC_REGEX_FIELDS)
            if re.findall(NEW_SPIROMETRY_FULL_IDENTIFIER, text, re.IGNORECASE):
                parameters.update(NEW_FULL_WITH_POST_SPECIFIC_REGEX_FIELDS)
        elif re.search(NEW_ONLY_SPIROMETRY_WITHOUT_POST_FORMAT_IDENTIFIER, text, re.IGNORECASE):
            parameters.update(NEW_ONLY_SPIROMETRY_WITHOUT_POST_SPECIFIC_REGEX_FIELDS)
            if re.findall(NEW_SPIROMETRY_FULL_IDENTIFIER, text, re.IGNORECASE):
                parameters.update(NEW_FULL_WITHOUT_POST_SPECIFIC_REGEX_FIELDS)

    elif format == FORMATS.OLD.FULL or format == FORMATS.OLD.ONLY_SPIROMETRY_WITH_POST or format == FORMATS.OLD.ONLY_SPIROMETRY_WITHOUT_POST:
        if re.search(r"(Pred\s+LLN\s+Pre\s+Pre[t%]Pred\s+Post)", text, re.IGNORECASE):
            if re.search(
                    r"[\nVCE]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt-]+)\s+([\d.,Olt-]+)\s+([\d.,Olt-]+)\s+([\d.,Olt-]+)[\s+%&3¢]{2}",
                    text, re.IGNORECASE):
                parameters.update(OLD_FULL_BASE_REGEX_FIELDS)
                parameters.update(OLD_FULL_SPECIFIC_REGEX_FIELDS)
            else:
                parameters.update(OLD_ONLY_SPIROMETRY_SPECIFIC_REGEX_FIELDS)
        elif re.search(r"(Pred\s+LLN\s+Pre\s+Pre[t%]Pred)", text, re.IGNORECASE):
            parameters.update(OLD_FULL_BASE_REGEX_FIELDS)
            parameters.update(OLD_WITHOUT_POST_SPECIFIC_REGEX_FIELDS)

    elif format == FORMATS.THIRD.FULL:
        parameters.update(BASE_THIRD_REGEX_FEILDS)
        parameters.update(THIRD_SPECIFIC_REGEX_FIELDS)

    return parameters

def get_regex_params(text):
    if re.findall(OLD_FORMAT_IDENTIFIER, text, re.IGNORECASE):
        patterns = BASE_OLD_REGEX_FIELDS.copy()
        patterns.update(add_format_parameters(text, FORMATS.OLD.FULL))
    elif re.findall(THIRD_FORMAT_IDENTIFIER, text, re.IGNORECASE):
        patterns = BASE_THIRD_REGEX_FEILDS.copy()
        patterns.update(add_format_parameters(text, FORMATS.THIRD.FULL))
    else:
        patterns = BASE_NEW_REGEX_FIELDS.copy()
        patterns.update(add_format_parameters(text, FORMATS.NEW.FULL_WITH_POST))

    return patterns

def extract_text(text):
    data = {}

    patterns = get_regex_params(text)

    # Extract using regex
    for field, pattern in patterns.items():
        if field != "Format":
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if field not in TEXT_FIELDS:
                    data[field] = " ".join(match.groups()).lower().replace("o","0").replace("l","1").replace(",", ".").replace("~", "-").replace('..', '.').replace('s', '5')
                else:
                    data[field] = " ".join(match.groups())
            else:
                data[field] = None  # Default to None if not found
        else:
            data["Format"] = patterns["Format"]

    data["Validator"] = ""
    data["Missing"] = ""
    return data, sum(1 for value in data.values() if value is not None), len(data.keys())

def delete_images(images_path):
    for image_path in images_path:
        os.remove(image_path)

def get_new_or_old_format_from_text(text):
    new_identifier = re.findall(NEW_FORMAT_IDENTIFIER, text, re.IGNORECASE)
    old_identifier = re.findall(OLD_FORMAT_IDENTIFIER, text, re.IGNORECASE)
    third_identifier = re.findall(THIRD_FORMAT_IDENTIFIER, text, re.IGNORECASE)

    if old_identifier and not new_identifier and not third_identifier:
        print("Old format detected, using tesseract")
        return tesseract_get_recognized_text, 150, 70
    elif new_identifier and not old_identifier and not third_identifier:
        print("New format identifier detected, using easyocr")
    elif third_identifier and not old_identifier and not new_identifier:
        print("Third format identifier detected, using tesseract")
        return tesseract_get_recognized_text, 150, 70
    else:
        print("Couldn't detect format. Defaulting to easyocr")

    return easyocr_get_recognized_text, 180, 35

def separate_new_from_old_format(images_path):
    text = ""
    for image_path in images_path:
        text += easyocr_get_recognized_text(image_path, 180)

    return get_new_or_old_format_from_text(text)

def process_file(pdf_path):
    debugging_data = ""
    img_path = convert_pdf_to_jpegs(pdf_path)
    get_text_func, base_thresh, num_of_thresh = separate_new_from_old_format(img_path)
    data, value, text, _ = analyze_images(img_path, get_text_func, base_threshold_level=base_thresh,
                                          num_of_thresholds=num_of_thresh)
    debugging_data += ("Current pdf path: " + pdf_path + "\n\n")
    debugging_data += (text + "\n\n")
    try:
        t = verify_data_results(data, VALIDATION_FIELDS[data["Format"]])
        append_data(t)
    except Exception as e:
        t= "Bad!"

    delete_images(img_path)
    return t, debugging_data

def get_data_from_folder(folder_path):
    debugging_data = ""
    already_processed = extract_file_paths_from_excel()
    bad_files = []

    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file)

            if pdf_path not in already_processed:
                e, debug = process_file(pdf_path)
                debugging_data += debug
                if "Bad!" in e:
                    bad_files.append(pdf_path)

    with open("bad_files.txt", "w") as g:
        g.write('\n'.join(bad_files))

    with open('debugging_data.txt', 'w') as f:
        f.write(debugging_data)

def get_data_from_file(pdf_path):
    extracted_data, debugging_data = process_file(pdf_path)

    with open('debugging_data.txt', 'a') as f:
        f.write(debugging_data)

    return extracted_data

# folder_path = r"C:\Users\danie\Documents\University\Biomediacl_engineering\final_project\data\test"
# logging.getLogger("easyocr").setLevel(logging.ERROR)
# get_data_from_folder(folder_path)