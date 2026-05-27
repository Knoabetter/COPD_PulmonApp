import os
import re
import cv2
import logging
import psutil
import pandas as pd
from typing import List
from pdf2image import convert_from_path
import pytesseract
pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_PATH', 'tesseract')
import easyocr
from consts import *
from save_data import append_data
from verification import verify_data_results

def log_memory(label):
    mb = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    print(f"[MEM] {label}: {mb:.0f} MB")

log_memory("module load")

def group_easyocr_results_by_row(ocr_results, y_threshold=15):
    detections = []
    for detection in ocr_results:
        bbox, text, conf = detection
        avg_y = sum(point[1] for point in bbox) / len(bbox)
        detections.append((bbox, text, conf, avg_y))

    detections.sort(key=lambda item: item[3])

    rows = []
    current_row = []
    current_row_y = None

    for detection in detections:
        bbox, text, conf, avg_y = detection
        if current_row_y is None:
            current_row_y = avg_y
            current_row.append(detection)
        elif abs(avg_y - current_row_y) <= y_threshold:
            current_row.append(detection)
        else:
            current_row.sort(key=lambda item: min(pt[0] for pt in item[0]))
            rows.append(current_row)
            current_row = [detection]
            current_row_y = avg_y

    if current_row:
        current_row.sort(key=lambda item: min(pt[0] for pt in item[0]))
        rows.append(current_row)

    organized_rows = '\n'.join([' '.join([text for _, text, _, _ in row]) for row in rows])
    return organized_rows

def easyocr_get_recognized_text(image_path, threshold=170, reader=None):
    import gc
    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    if reader is None:
        model_dir = os.environ.get('EASYOCR_MODULE_PATH', None)
        reader = easyocr.Reader(['en'], gpu=False, model_storage_directory=model_dir)
        results = reader.readtext(binary)
        del reader
        gc.collect()
    else:
        results = reader.readtext(binary)
    return group_easyocr_results_by_row(results) + "\n"

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
        pages = convert_from_path(file_path, poppler_path=os.environ.get('POPPLER_PATH', None), dpi=150)
    except Exception as e:
        msg = str(e)
        print(f"[pdf2image ERROR] {type(e).__name__}: {msg}")
        print(f"[pdf2image] poppler_path={os.environ.get('POPPLER_PATH', 'NOT SET')}")
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

def tesseract_get_recognized_text(image_path, threshold=170):
    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return pytesseract.image_to_string(binary, config='--oem 1') + "\n"

def tesseract_get_recognized_text_otsu(image_path, _threshold=None):
    """Single-call OCR using Otsu's optimal binary threshold — no iteration needed."""
    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return pytesseract.image_to_string(binary, config='--oem 1') + "\n"

def analyze_images(images_path, get_text_func, base_threshold_level=170, num_of_thresholds=40, reader=None):

    best_threshold = ({}, 0, "", -1)
    no_improve_streak = 0

    for i in range(base_threshold_level + 1, base_threshold_level + num_of_thresholds + 1, 3):
        text = ""
        for image_path in images_path:
            if reader is not None:
                text += get_text_func(image_path, i, reader)
            else:
                text += get_text_func(image_path, i)

        data, value, num = extract_text(text)

        if value > best_threshold[1]:
            best_threshold = (data, value, text, num)
            print(i, value, num)
            no_improve_streak = 0
            if value == num:
                break
        else:
            no_improve_streak += 1
            if no_improve_streak >= 8:
                print(f"Early stop: no improvement for 8 iterations at threshold {i}")
                break

    return best_threshold

def add_format_parameters(text, format):
    parameters = {}

    if format == FORMATS.NEW:
        if re.findall(WITH_POST_IDENTIFIER, text, re.IGNORECASE):
            parameters.update(NEW_ONLY_SPIROMETRY_WITH_POST_SPECIFIC_REGEX_FIELDS)
            if re.findall(NEW_SPIROMETRY_FULL_IDENTIFIER, text, re.IGNORECASE):
                parameters.update(NEW_FULL_WITH_POST_SPECIFIC_REGEX_FIELDS)
        elif re.search(NEW_ONLY_SPIROMETRY_WITHOUT_POST_FORMAT_IDENTIFIER, text, re.IGNORECASE):
            parameters.update(NEW_ONLY_SPIROMETRY_WITHOUT_POST_SPECIFIC_REGEX_FIELDS)
            if re.findall(NEW_SPIROMETRY_FULL_IDENTIFIER, text, re.IGNORECASE):
                parameters.update(NEW_FULL_WITHOUT_POST_SPECIFIC_REGEX_FIELDS)

    elif format == FORMATS.OLD:
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
        patterns.update(add_format_parameters(text, FORMATS.OLD))
    elif re.findall(THIRD_FORMAT_IDENTIFIER, text, re.IGNORECASE):
        patterns = BASE_THIRD_REGEX_FEILDS.copy()
        patterns.update(add_format_parameters(text, FORMATS.THIRD.FULL))
    else:
        patterns = BASE_NEW_REGEX_FIELDS.copy()
        patterns.update(add_format_parameters(text, FORMATS.NEW))

    return patterns

def _fix_ocr_chars(raw: str) -> str:
    s = raw.lower()
    s = s.replace("o", "0").replace("l", "1")
    s = s.replace(",", ".").replace("~", "-").replace("..", ".")
    # Replace 's' only when it appears as a standalone token (isolated misread digit), not as a suffix
    s = re.sub(r'(?<!\d)s(?!\w)', '5', s)
    return s

def extract_text(text):
    data = {}

    patterns = get_regex_params(text)

    # Extract using regex
    for field, pattern in patterns.items():
        if field != "Format":
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if field not in TEXT_FIELDS:
                    data[field] = _fix_ocr_chars(" ".join(match.groups()))
                else:
                    data[field] = " ".join(match.groups())
            else:
                data[field] = None  # Default to None if not found
        else:
            data["Format"] = patterns["Format"]

    if data.get("Height") is None:
        lines = [l for l in text.splitlines() if any(k in l.lower() for k in ['height', 'ht', ' cm', 'weight', 'wt'])]
        print(f"[HEIGHT DEBUG] Height not matched. Relevant lines:\n" + "\n".join(lines[:10]))

    if data.get("FVC") is None or data.get("FEV1") is None:
        lines = [l for l in text.splitlines() if any(k in l.upper() for k in ['FVC', 'FEV'])]
        print(f"[FVC/FEV1 DEBUG] FVC={data.get('FVC')} FEV1={data.get('FEV1')}. Relevant OCR lines:\n" + "\n".join(lines[:20]))

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
        print("New format detected, using easyocr")
        return easyocr_get_recognized_text, 180, 35
    elif third_identifier and not old_identifier and not new_identifier:
        print("Third format detected, using tesseract")
        return tesseract_get_recognized_text, 150, 70
    else:
        print("Couldn't detect format. Defaulting to easyocr")
        return easyocr_get_recognized_text, 180, 35

def separate_new_from_old_format(images_path, reader=None):
    text = ""
    for image_path in images_path:
        text += easyocr_get_recognized_text(image_path, 180, reader)

    return get_new_or_old_format_from_text(text)

def process_file(pdf_path):
    import gc
    log_memory("start")
    debugging_data = ""
    img_path = convert_pdf_to_jpegs(pdf_path)
    log_memory("after convert")

    # Load EasyOCR once upfront — reused for format detection AND the full sweep
    model_dir = os.environ.get('EASYOCR_MODULE_PATH', None)
    reader = easyocr.Reader(['en'], gpu=False, model_storage_directory=model_dir)
    log_memory("after easyocr load")

    get_text_func, base_thresh, num_of_thresh = separate_new_from_old_format(img_path, reader)
    log_memory("after format detect")

    if get_text_func == easyocr_get_recognized_text:
        data, value, text, _ = analyze_images(img_path, get_text_func, base_thresh, num_of_thresh, reader)
    else:
        del reader
        gc.collect()
        reader = None
        data, value, text, _ = analyze_images(img_path, get_text_func, base_thresh, num_of_thresh)

    log_memory("after analyze")

    if reader is not None:
        del reader
        gc.collect()
        log_memory("after easyocr unload")

    debugging_data += ("Current pdf path: " + pdf_path + "\n\n")
    debugging_data += (text + "\n\n")
    t = verify_data_results(data, VALIDATION_FIELDS[data["Format"]])
    append_data(t)
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