import os
import re

import cv2
import easyocr
from pdf2image import convert_from_path

from consts import *
from save_data import append_data
from verification import verify_data_results


def convert_pdf_to_jpegs(file_path: str) -> [str]:
    pages = convert_from_path(file_path)
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

def get_recognized_text(image_path, threshold=170):
    text = ""

    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    reader = easyocr.Reader(['en'])
    results = reader.readtext(binary)

    text += group_easyocr_results_by_row(results)
    text += "\n"

    return text

def analyze_images(images_path, base_threshold_level=170, num_of_thresholds=40):

    best_threshold = ({}, 0, "", -1)

    for i in range(base_threshold_level + 1, base_threshold_level + num_of_thresholds + 1, 3):
        text = ""
        for image_path in images_path:
            text += get_recognized_text(image_path, i)

        data, value, num = extract_text(text)

        if value > best_threshold[1]:
            best_threshold = (data, value, text, num)
            print(i, value, num)
            if value == num:
                break

    return best_threshold

def add_format_parameters(text):
    parameters = BASE_NEW_REGEX_FIELDS

    if re.findall(WITH_POST_IDENTIFIER, text, re.IGNORECASE):
        parameters.update(NEW_ONLY_SPIROMETRY_WITH_POST_SPECIFIC_REGEX_FIELDS)
        if re.findall(NEW_SPIROMETRY_FULL_IDENTIFIER, text, re.IGNORECASE):
            parameters.update(NEW_FULL_WITH_POST_SPECIFIC_REGEX_FIELDS)
    elif re.search(NEW_ONLY_SPIROMETRY_WITHOUT_POST_FORMAT_IDENTIFIER, text, re.IGNORECASE):
        parameters.update(NEW_ONLY_SPIROMETRY_WITHOUT_POST_SPECIFIC_REGEX_FIELDS)
        if re.findall(NEW_SPIROMETRY_FULL_IDENTIFIER, text, re.IGNORECASE):
            parameters.update(NEW_FULL_WITHOUT_POST_SPECIFIC_REGEX_FIELDS)

    return parameters

def get_regex_params(text):
    # Regex patterns for common fields
    patterns = BASE_NEW_REGEX_FIELDS

    patterns.update(add_format_parameters(text))

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
                    data[field] = " ".join(match.groups()).lower().replace("o","0").replace("l","1").replace(",", ".").replace("~", "-").replace('..', '.')
                else:
                    data[field] = " ".join(match.groups())
            else:
                data[field] = None  # Default to None if not found
        else:
            data["Format"] = patterns["Format"]

    data["Validator"] = ""
    return data, sum(1 for value in data.values() if value is not None), len(patterns.keys())

def delete_images(images_path):
    for image_path in images_path:
        os.remove(image_path)

def get_data_from_folder(folder_path):
    debugging_data = ""
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file)
            img_path = convert_pdf_to_jpegs(pdf_path)
            data, value, text, _ = analyze_images(img_path, base_threshold_level=180, num_of_thresholds=35)
            debugging_data += ("Current pdf path: " + pdf_path + "\n\n")
            debugging_data += (text + "\n\n")
            t = verify_data_results(data, VALIDATION_FIELDS[data["Format"]])
            append_data(t)
            delete_images(img_path)

    with open('debugging_data.txt', 'w') as f:
        f.write(debugging_data)


folder_path = r"C:\Users\danie\Documents\University\Biomediacl_engineering\final_project\data\new"
get_data_from_folder(folder_path)