import os
import re
import cv2
import logging
import psutil
import pandas as pd
import threading
from collections import Counter
from typing import List
from pdf2image import convert_from_path
import pytesseract
# TODO: hardcoded path — make configurable via env var before deployment
tesseract_path = os.environ.get('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
import easyocr
from consts import *
from save_data import append_data
from verification import verify_data_results

def log_memory(label):
    mb = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    print(f"[MEM] {label}: {mb:.0f} MB")

log_memory("module load")

_EASYOCR_READER = None
_EASYOCR_INIT_LOCK = threading.Lock()   # guards one-time construction
_EASYOCR_READ_LOCK = threading.Lock()   # serializes readtext calls

def _get_easyocr_reader():
    """Lazily construct a single shared EasyOCR Reader (weights load once)."""
    global _EASYOCR_READER
    if _EASYOCR_READER is None:
        with _EASYOCR_INIT_LOCK:
            if _EASYOCR_READER is None:  # double-checked: another thread may have built it
                model_dir = os.environ.get('EASYOCR_MODULE_PATH', None)
                _EASYOCR_READER = easyocr.Reader(['en'], gpu=False, model_storage_directory=model_dir)
    return _EASYOCR_READER

def _repair_spaced_decimal(text):
    """
    EasyOCR sometimes reads a decimal cell (e.g. '1.74') as a single token
    with an internal space instead of a decimal point (e.g. '1 74'). Within
    one OCR token this is always one number, never two separate values, so
    it is safe to convert the internal space to a decimal point.
    Only matches the spirometry decimal shape: 1-2 digits, one space, 1-2 digits.
    """
    if re.fullmatch(r"\d{1,2} \d{1,2}", text):
        return text.replace(" ", ".")
    return text

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

    organized_rows = '\n'.join([' '.join([_repair_spaced_decimal(text) for _, text, _, _ in row]) for row in rows])
    return organized_rows

def easyocr_get_recognized_text(image_path, threshold=170):
    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    reader = _get_easyocr_reader()
    with _EASYOCR_READ_LOCK:
        results = reader.readtext(binary)
    text = group_easyocr_results_by_row(results) + "\n"
    return text

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
        # TODO: hardcoded fallback path — set POPPLER_PATH env var in deployment
        pages = convert_from_path(file_path, poppler_path=os.environ.get('POPPLER_PATH', r"C:\Users\Noadi\Poppler\Library\bin"), dpi=150)
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

def _is_clean_value(val: str) -> bool:
    if val is None:
        return False
    # Reject if contains isolated dot (truncated number artifact)
    if re.search(r'(?<!\d)\.(?!\d)', val):
        return False
    # Reject if contains hyphen not preceded by digit or space (OCR dash artifact)
    if re.search(r'(?<!\d)-(?!\d)', val) and not val.strip().startswith('-'):
        return False
    return True

MODE_MERGE_FIELDS = {"Age", "Sex", "Height", "ID", "Date of Birth"}

# Measurement fields where the correct full-row string is the most frequent
# reading across thresholds.  Mode selection fixes OCR artifacts (e.g. "174"
# instead of "1.74") that first-clean-value would lock in from an early
# bad-threshold iteration.
MEASUREMENT_MODE_FIELDS = {
    "FVC", "FEV1", "TLC", "RV", "DLCO SB", "DLCOc SB", "DLCO/VA", "DLCOc/V",
    "VC", "IC", "ERV", "TGV", "PEF", "PIF",
    "MEF25", "MEF50", "MEF75", "MEF 75/25",
    "FEV6", "FEV1 % FEV6", "FEV 1 % FVC",
}

def analyze_images(images_path, get_text_func, base_threshold_level=170, num_of_thresholds=40):
    merged_data = {}
    candidate_lists = {}  # field -> list of all clean values across thresholds (mode-merge fields)
    best_text = ""
    best_value = 0
    best_num = 0
    no_improve_streak = 0

    for i in range(base_threshold_level + 1, base_threshold_level + num_of_thresholds + 1, 3):
        text = ""
        for image_path in images_path:
            text += get_text_func(image_path, i)

        data, value, num = extract_text(text)

        # Seed all keys from this iteration so unmatched fields appear as None
        for field in data:
            if field not in merged_data:
                merged_data[field] = None

        # Merge: mode selection for demographic and measurement fields,
        # first-clean-value for everything else (e.g. name, operator).
        for field, val in data.items():
            if field == 'Format':
                continue  # Format is set after the loop from best-scoring iteration
            if not _is_clean_value(val):
                continue
            if field in MODE_MERGE_FIELDS or field in MEASUREMENT_MODE_FIELDS:
                candidate_lists.setdefault(field, []).append(val)
            else:
                if merged_data.get(field) is None:
                    merged_data[field] = val

        # Track best text (highest-scoring single iteration) for debugging
        if value > best_value:
            best_value = value
            best_text = text
            best_num = num
            no_improve_streak = 0
            print(i, value, num)
            if value == num:
                break
        else:
            no_improve_streak += 1
            if no_improve_streak >= 8:
                print(f"Early stop: no improvement for 8 iterations at threshold {i}")
                break

    # Resolve mode-merge fields: pick most frequent clean value across all iterations
    for field, candidates in candidate_lists.items():
        if candidates:
            most_common_val, _ = Counter(candidates).most_common(1)[0]
            merged_data[field] = most_common_val

    if best_text:
        best_data, _, _ = extract_text(best_text)
        merged_data['Format'] = best_data.get('Format')
    else:
        merged_data['Format'] = None
    merged_data.setdefault('Format', None)

    merged_value = sum(1 for v in merged_data.values() if v is not None)
    return merged_data, merged_value, best_text, best_num

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
        if re.search(r"(Pred\s+LLN\s+Pre\s+Pre[t%]Pred\s+P[o0]?st)", text, re.IGNORECASE):
            has_lung_volumes = (
                re.search(r"[\nVCE]{3}\s+[\[\(\{c]{1,2}[ILulhbtrJ1]{1,3}[\]\)\}Jy]{0,2}\s+([\d.,Olt-]+)", text, re.IGNORECASE) or
                re.search(r"[\nTLC]{4}\s+[\[\(\{c]{1,2}[ILulhbtrJ1]{1,3}[\]\)\}Jy]{0,2}\s+([\d.,Olt-]+)", text, re.IGNORECASE) or
                re.search(r"[\nRV]{3}\s+[\[\(\{c]{1,2}[ILulhbtrJ1]{1,3}[\]\)\}Jy]{0,2}\s+([\d.,Olt-]+)", text, re.IGNORECASE)
            )
            if has_lung_volumes:
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
    s = s.replace(",", ".").replace("~", "-").replace("..", ".")     # Replace 's' only when it appears as a standalone token (isolated misread digit), not as a suffix
    s = re.sub(r'(?<!\d)s(?!\w)', '5', s)
    s = re.sub(r'(\d)-(\d)', r'\1.\2', s)
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
                    data[field] = _fix_ocr_chars(" ".join(g for g in match.groups() if g is not None))
                else:
                    data[field] = " ".join(g for g in match.groups() if g is not None)
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

    if data.get("TLC") is None:
        lines = [l for l in text.splitlines() if 'tlc' in l.lower()]
        print(f"[TLC DEBUG] TLC=None. Relevant OCR lines:")
        for line in lines[:5]:
            print(f"  {line}")

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

    if old_identifier and not new_identifier:
        print("Old format detected, using tesseract")
        return tesseract_get_recognized_text, 150, 70
    elif new_identifier and not old_identifier:
        print("New format identifier detected, using easyocr")
    elif third_identifier and not new_identifier and not old_identifier:
        print("Third format detected, using tesseract")
        return tesseract_get_recognized_text, 150, 70
    else:
        print("Couldn't detect format. Defaulting to easyocr")

    return easyocr_get_recognized_text, 180, 35

def separate_new_from_old_format(images_path):
    try:
        # First scan with EasyOCR — reliable for new format detection
        easyocr_text = ""
        for image_path in images_path:
            easyocr_text += easyocr_get_recognized_text(image_path, 180)

        new_identifier = re.findall(NEW_FORMAT_IDENTIFIER, easyocr_text, re.IGNORECASE)
        old_identifier = re.findall(OLD_FORMAT_IDENTIFIER, easyocr_text, re.IGNORECASE)
        third_identifier = re.findall(THIRD_FORMAT_IDENTIFIER, easyocr_text, re.IGNORECASE)

        # If EasyOCR clearly identifies new format, use it
        if new_identifier and not old_identifier and not third_identifier:
            print("New format detected via EasyOCR, using easyocr")
            return easyocr_get_recognized_text, 180, 35

        # For anything ambiguous or old-looking, try Tesseract
        print("EasyOCR ambiguous or old format suspected, trying Tesseract...")
        tesseract_text = ""
        for image_path in images_path:
            tesseract_text += tesseract_get_recognized_text(image_path, 150)

        new_id_t   = re.findall(NEW_FORMAT_IDENTIFIER, tesseract_text, re.IGNORECASE)
        old_id_t   = re.findall(OLD_FORMAT_IDENTIFIER, tesseract_text, re.IGNORECASE)
        third_id_t = re.findall(THIRD_FORMAT_IDENTIFIER, tesseract_text, re.IGNORECASE)

        if old_id_t and not new_id_t and not third_id_t:
            print("Old format detected via Tesseract, using tesseract")
            return tesseract_get_recognized_text, 150, 70
        elif third_id_t and not new_id_t and not old_id_t:
            print("Third format detected via Tesseract, using tesseract")
            return tesseract_get_recognized_text, 150, 70
        elif new_id_t and not old_id_t and not third_id_t:
            print("New format confirmed via Tesseract, using easyocr")
            return easyocr_get_recognized_text, 180, 35
        else:
            print("Could not detect format, defaulting to tesseract")
            return tesseract_get_recognized_text, 150, 70

    except Exception as e:
        print(f"Format detection error: {e}. Defaulting to tesseract.")
        return tesseract_get_recognized_text, 150, 70

def process_file(pdf_path):
    log_memory("start")
    debugging_data = ""
    img_path = convert_pdf_to_jpegs(pdf_path)
    log_memory("after convert")
    get_text_func, base_thresh, num_of_thresh = separate_new_from_old_format(img_path)
    log_memory("after format detect")
    data, value, text, _ = analyze_images(img_path, get_text_func, base_threshold_level=base_thresh, num_of_thresholds=num_of_thresh)
    log_memory("after analyze")
    debugging_data += ("Current pdf path: " + pdf_path + "\n\n")
    debugging_data += (text + "\n\n")
    fmt = data.get("Format")
    t = verify_data_results(data, VALIDATION_FIELDS.get(fmt, []) if fmt else [])
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