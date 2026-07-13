import re
from consts import ROUND_ERROR_LEEWAY, ONLY_DCHANGE_VALIDATIONS_FIELDS

# Physiological plausibility bounds — wide by design.
# Purpose: catch OCR errors (lost decimals, digit flips) that produce
# impossible values, NOT to flag clinically abnormal results.
# A value outside these bounds is flagged for human review only.
PLAUSIBILITY_BOUNDS = {
    "FVC":          (0.3, 8.0),    # liters
    "FEV1":         (0.2, 7.0),    # liters
    "FEV 1 % FVC":  (15, 100),     # percent
    "TLC":          (1.5, 12.0),   # liters
    "RV":           (0.3, 7.0),    # liters
    "DLCO SB":      (1.0, 20.0),   # mmol/min/kPa
    "DLCOc SB":     (1.0, 20.0),
    "Height":       (120, 220),    # cm
    "Age":          (5, 120),      # years
    "Weight":       (20, 250),     # kg
}


def validate_dchange(pre, post, dchange):
    return abs(post - round(((100 + dchange) * pre) / 100, 2)) < ROUND_ERROR_LEEWAY


def validate_post_pred_percent(post, pred, percent):
    return abs(post - round((pred * percent) / 100, 2)) < ROUND_ERROR_LEEWAY


def validate_pre_pred_percent(pre, pred, percent):
    return abs(pre - round((pred * percent) / 100, 2)) < ROUND_ERROR_LEEWAY


def get_full_values(value, fmt=None):
    parts = value.split()
    n = len(parts)

    fmt_str = str(fmt).upper() if fmt is not None else ""
    is_old = "OLD" in fmt_str
    is_new = "NEW" in fmt_str

    if is_old:
        # Pred | LLN | Pre | Pre%Pred | Post | Post%Pred | D%Change  (7 tokens)
        padded = parts + [None] * max(0, 7 - n)
        pred, _, pre, pred_pre_percent, post, pred_post_percent, dchange = padded[:7]
        return pred, pre, pred_pre_percent, post, pred_post_percent, dchange

    if is_new:
        # Ref(Pred) | Pre | %Ref | Post | %Ref | %Pre  (6 tokens, no LLN)
        padded = parts + [None] * max(0, 6 - n)
        pred, pre, pred_pre_percent, post, pred_post_percent, dchange = padded[:6]
        return pred, pre, pred_pre_percent, post, pred_post_percent, dchange

    # Fallback: format unknown — original count-based behavior
    if n == 7:
        pred, _, pre, pred_pre_percent, post, pred_post_percent, dchange = parts
    elif n == 6:
        pred, pre, pred_pre_percent, post, pred_post_percent, dchange = parts
    else:
        padded = parts + [None] * (6 - n)
        pred, pre, pred_pre_percent, post, pred_post_percent, dchange = padded[:6]
    return pred, pre, pred_pre_percent, post, pred_post_percent, dchange


def validate_all(validation_errors, value_name, value, fmt=None):
    pred, pre, pred_pre_percent, post, pred_post_percent, dchange = get_full_values(value, fmt)

    if pred is None or pre is None:
        validation_errors += "Incomplete OCR data for {}, ".format(value_name)
        return validation_errors

    def _f(x):
        try:
            return float(x)
        except (ValueError, TypeError):
            return None

    fpred, fpre, fpost = _f(pred), _f(pre), _f(post)
    fprepct, fpostpct, fdchange = _f(pred_pre_percent), _f(pred_post_percent), _f(dchange)

    if None not in (fpost, fpred, fpostpct):
        if not validate_post_pred_percent(fpost, fpred, fpostpct):
            validation_errors += "Failed pred/post percent validation for {}, ".format(value_name)
    if None not in (fpre, fpred, fprepct):
        if not validate_pre_pred_percent(fpre, fpred, fprepct):
            validation_errors += "Failed pre/pred percent validation for {}, ".format(value_name)
    if None not in (fpre, fpost, fdchange):
        if not validate_dchange(fpre, fpost, fdchange):
            validation_errors += "Failed dchange validation for {}, ".format(value_name)

    return validation_errors


def get_dchange_values(value):
    if value.count(' ') == 3:
        _, pre, post, dchange = value.split(' ')
    elif value.count(' ') == 2:
        pre, post, dchange = value.split(' ')
    else:
        pre = value.strip()
        post, dchange = None, None

    return pre, post, dchange


def validate_only_dhcange(validation_errors, value_name, value):
    pre, post, dchange = get_dchange_values(value)
    if None in (post, dchange):
        return validation_errors
    if not validate_dchange(float(pre), float(post), float(dchange)):
        validation_errors += "Failed dchange validation for {}, ".format(value_name)

    return validation_errors


def get_pred_pre_values(value):
    if value.count(' ') == 3:
        pred, _, pre, pred_pre_percent = value.split(' ')
    else:
        pred, pre, pred_pre_percent = value.split(' ')

    return pred, pre, pred_pre_percent


def validate_only_pre_pred(validation_errors, value_name, value):
    pred, pre, pred_pre_percent = get_pred_pre_values(value)

    if not validate_pre_pred_percent(float(pre), float(pred), float(pred_pre_percent)):
        validation_errors += "Failed pre/pred percent validation for {}, ".format(value_name)

    return validation_errors


def check_pre_post_in_dchange_missing_after_dot(value_name, pre, post, dchange):
    validation_errors = ""

    if pre.endswith('.'):
        pre = round((post / (100 + dchange)) * 100, 2)
        validation_errors += "Fixed missing after dot for pre in {}, ".format(value_name)

    if post.endswith('.'):
        post = round((pre * (100 + dchange)) / 100, 2)
        validation_errors += "Fixed missing after dot for post in {}, ".format(value_name)

    return validation_errors, ' '.join([pre, post, dchange])


def check_pred_pre_in_pred_pre_percentage_missing_after_dot(value_name, pred, pre, pred_pre_percent):
    validation_errors = ""

    if pred.endswith('.'):
        pred = round((pre / pred_pre_percent) * 100, 2)
        validation_errors += "Fixed missing after dot for pred in {}, ".format(value_name)

    if pre.endswith('.'):
        pre = round((pred * pred_pre_percent) / 100, 2)
        validation_errors += "Fixed missing after dot for pre in {}, ".format(value_name)

    return validation_errors, ' '.join([pred, pre, pred_pre_percent])


def check_and_fix_missing_after_dot_data(value_name, value):
    validation_errors = ""
    params = value.split(' ')

    if len(params) == 3:
        validation_errors, params = check_pre_post_in_dchange_missing_after_dot(value_name, *params)
    elif len(params) == 4:
        validation_errors, params = check_pred_pre_in_pred_pre_percentage_missing_after_dot(value_name, *params)
    elif len(params) == 6:
        pass
        # TODO
    return validation_errors, params


def remove_mistaken_missing_values_warning(missing_values):
    messages_to_remove = [
        "No value to validate for MEF25,",
        "No value to validate for MEF50,",
        "No value to validate for MEF75,"
    ]

    if all(msg in missing_values for msg in messages_to_remove):
        for msg in messages_to_remove:
            missing_values = missing_values.replace(msg, "")

    return missing_values


def verify_numeric_results(value_name, value, fmt=None):
    validation_errors = ""
    if value is None:
        return "", "No value to validate for {},".format(value_name)
    try:
        if value_name in ONLY_DCHANGE_VALIDATIONS_FIELDS:
            validation_errors += validate_only_dhcange(validation_errors, value_name, value)
        elif value.count(' ') == 2 or value.count(' ') == 3:
            validation_errors += validate_only_pre_pred(validation_errors, value_name, value)
        else:
            validation_errors += validate_all(validation_errors, value_name, value, fmt)
    except Exception as e:
        print(e)
        validation_errors += "Failed numeric validation for {}, ".format(value_name)
        return validation_errors, ""

    return validation_errors, ""


def _has_truncated_decimal(value_str):
    if value_str is None:
        return False
    for token in value_str.split(" "):
        if re.fullmatch(r"\d+\.", token):
            return True
    return False


def _check_plausibility(field, value_str, fmt=None):
    """
    Flag (never modify) implausible physiological values. Checks the liter-
    measurement columns (Pred, Pre, Post) parsed via get_full_values against
    the field's bounds. Percent columns are not checked. Returns a warning
    string listing any out-of-range column, or "" if all are plausible or
    the field has no bounds.
    """
    if field not in PLAUSIBILITY_BOUNDS or value_str is None:
        return ""

    low, high = PLAUSIBILITY_BOUNDS[field]

    try:
        pred, pre, _, post, _, _ = get_full_values(value_str, fmt)
    except (ValueError, TypeError):
        # If the value can't be parsed into columns, fall back to scanning
        # tokens and flag the first out-of-range numeric token.
        for tok in value_str.split(" "):
            try:
                num = float(tok)
            except (ValueError, TypeError):
                continue
            if num < low or num > high:
                return "Implausible value for {} ({}) — possible OCR error, ".format(field, tok)
            break
        return ""

    warnings = ""
    for label, val in (("Pred", pred), ("Pre", pre), ("Post", post)):
        if val is None:
            continue
        try:
            num = float(val)
        except (ValueError, TypeError):
            continue
        if num < low or num > high:
            warnings += "Implausible {} value for {} ({}) — possible OCR error, ".format(label, field, val)
    return warnings


def verify_data_results(data, numeric_fields_to_validate):
    fmt = data.get("Format")
    for key in data.keys():
        if key in numeric_fields_to_validate:
            validation_errors, missing_values = verify_numeric_results(key, data[key], fmt)

            if _has_truncated_decimal(data[key]):
                validation_errors += "Failed missing after dot validation for {}, ".format(key)

            plausibility_warning = _check_plausibility(key, data[key], fmt)
            if plausibility_warning:
                validation_errors += plausibility_warning

            data["Validator"] += validation_errors
            data["Missing"] += missing_values

    if data["Validator"] == "":
        data["Validator"] = "OK"

    data["Missing"] = remove_mistaken_missing_values_warning(data["Missing"])

    return data

