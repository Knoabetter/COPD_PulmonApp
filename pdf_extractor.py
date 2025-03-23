import os
import re

import cv2
import pytesseract
from pdf2image import convert_from_path

from consts import TEXT_FIELDS, BASE_OLD_REGEX_FIELDS, OLD_WITHOUT_POST_SPECIFIC_REGEX_FIELDS, \
    IMPOSSIBLE_REGEX_FIELDS, OLD_FULL_SPECIFIC_REGEX_FIELDS, OLD_ONLY_SPIROMETRY_SPECIFIC_REGEX_FIELDS, \
    OLD_FULL_BASE_REGEX_FIELDS
from save_data import append_data
from verification import verify_old_data_results

def convert_pdf_to_jpegs(file_path: str) -> [str]:
    pages = convert_from_path(file_path)
    images_path = []

    for i, page in enumerate(pages):
        img_path = file_path.replace('.pdf', f"_page_{i+1}.jpg")
        page.save(img_path, "JPEG")
        images_path.append(img_path)

    return images_path

def get_recognized_text(image_path, threshold=170):
    text = ""

    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    text += pytesseract.image_to_string(binary)
    text += "\n"

    return text

def analyze_images(images_path, base_threshold_level=170, num_of_thresholds=40):

    best_threshold = ({}, 100, "")

    for i in range(base_threshold_level + 1, base_threshold_level + num_of_thresholds + 1):
        text = ""
        for image_path in images_path:
            text += get_recognized_text(image_path, i)

        data, value = extract_text(text)

        if value <= best_threshold[1]:
            best_threshold = (data, value, text)
            print(i, value)
            if value == 0:
                break

    return best_threshold

def add_format_parameters(text):
    parameters = BASE_OLD_REGEX_FIELDS
    if re.search(r"(Pred\s+LLN\s+Pre\s+Pre[t%]Pred\s+Post)",text, re.IGNORECASE):
        if re.search(r"[\nVCE]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt-]+)\s+([\d.,Olt-]+)\s+([\d.,Olt-]+)\s+([\d.,Olt-]+)[\s+%&3¢]{2}", text, re.IGNORECASE):
            parameters.update(OLD_FULL_BASE_REGEX_FIELDS)
            parameters.update(OLD_FULL_SPECIFIC_REGEX_FIELDS)
        else:
            parameters.update(OLD_ONLY_SPIROMETRY_SPECIFIC_REGEX_FIELDS)
    elif re.search(r"(Pred\s+LLN\s+Pre\s+Pre[t%]Pred)", text, re.IGNORECASE):
        parameters.update(OLD_FULL_BASE_REGEX_FIELDS)
        parameters.update(OLD_WITHOUT_POST_SPECIFIC_REGEX_FIELDS)
    else:
        return IMPOSSIBLE_REGEX_FIELDS

    return parameters

def get_regex_params(text):
    # Regex patterns for common fields
    patterns = BASE_OLD_REGEX_FIELDS

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
                    data[field] = " ".join(match.groups()).lower().replace("o","0").replace("l","1").replace(",", ".")
                else:
                    data[field] = " ".join(match.groups())
            else:
                data[field] = None  # Default to None if not found
        else:
            data["Format"] = patterns["Format"]

    data["Validator"] = ""
    return data, sum(1 for value in data.values() if value is None)

def delete_images(images_path):
    for image_path in images_path:
        os.remove(image_path)

def get_data_from_folder(folder_path):
    debugging_data = ""
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file)
            img_path = convert_pdf_to_jpegs(pdf_path)
            data, value, text = analyze_images(img_path, base_threshold_level=150, num_of_thresholds=70)
            debugging_data += ("Current pdf path: " + pdf_path + "\n\n")
            debugging_data += (text + "\n\n")
            t = verify_old_data_results(data)
            append_data(t)
            delete_images(img_path)

    with open('debugging_data.txt', 'w') as f:
        f.write(debugging_data)


folder_path = r"C:\Users\danie\Documents\University\Biomediacl_engineering\final_project\data\test"
get_data_from_folder(folder_path)



pdf_path = r"C:\Users\danie\Documents\University\Biomediacl_engineering\final_project\ViewDocument{num}.pdf"

"""
debugging_data = ""


for i in range(1,4):
    img_path = convert_pdf_to_jpegs(pdf_path.format(num=i))
    data, value, text = analyze_images(img_path, base_threshold_level=150, num_of_thresholds=90)
    debugging_data += ("Current pdf path: " + pdf_path.format(num=i) + "\n\n")
    debugging_data += (text + "\n\n")
    t = verify_old_data_results(data)
    append_data(t)
    delete_images(img_path)

with open('debugging_data.txt', 'w') as f:
    f.write(debugging_data)
"""
"""
img_path = convert_pdf_to_jpegs(pdf_path.format(num=3))
data, value, text = analyze_images(img_path, base_threshold_level=200, num_of_thresholds=5)
t = extract_text(text)
t = verify_old_data_results(t[0])
append_data(t)
delete_images(img_path)
print(t)
"""
"""
img_path = convert_pdf_to_jpegs("data/new_spirometry_only_pre.pdf")
data, value, text = analyze_images(img_path, base_threshold_level=150, num_of_thresholds=90)
print(data, value)"""