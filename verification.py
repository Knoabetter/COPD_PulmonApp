from consts import FORMATS, NUMERIC_VALIDATE_FIELDS, NUMERIC_WITH_POST_FIELDS, ROUND_ERROR_LEEWAY, \
    ONLY_DCHANGE_VALIDATIONS_FIELDS, NEW_NUMERIC_VALIDATE_FIELDS


def validate_dchange(pre, post, dchange):
    return abs(post - round(((100 + dchange) * pre) / 100 ,2)) < ROUND_ERROR_LEEWAY

def validate_post_pred_percent(post, pred, percent):
    return abs(post - round((pred * percent) / 100 ,2)) < ROUND_ERROR_LEEWAY

def validate_pre_pred_percent(pre, pred, percent):
    return abs(pre - round((pred * percent) / 100 ,2)) < ROUND_ERROR_LEEWAY

def validate_all(validation_errors, value_name, pred, pre, pred_pre_percent, post, pred_post_percent, dchange):
    if not validate_post_pred_percent(float(post), float(pred), float(pred_post_percent)):
        validation_errors += "Failed pred/post percent validation for {}, ".format(value_name)
    if not validate_pre_pred_percent(float(pre), float(pred), float(pred_pre_percent)):
        validation_errors += "Failed pre/pred percent validation for {}, ".format(value_name)
    if not validate_dchange(float(pre), float(post), float(dchange)):
        validation_errors += "Failed dchange validation for {}, ".format(value_name)

    return validation_errors

def validate_only_dhcange(validation_errors, value_name, pre, post, dchange):
    if not validate_dchange(float(pre), float(post), float(dchange)):
        validation_errors += "Failed dchange validation for {}, ".format(value_name)

    return validation_errors

def validate_only_pre_pred(validation_errors, value_name, pred, LLN, pre, pred_pre_percent):
    if not validate_pre_pred_percent(float(pre), float(pred), float(pred_pre_percent)):
        validation_errors += "Failed pre/pred percent validation for {}, ".format(value_name)

    return validation_errors

def validate_only_pre_pred_new(validation_errors, value_name, pred, pre, pred_pre_percent):
    if not validate_pre_pred_percent(float(pre), float(pred), float(pred_pre_percent)):
        validation_errors += "Failed pre/pred percent validation for {}, ".format(value_name)

    return validation_errors

def check_pre_post_in_dchange_missing_after_dot(value_name, pre, post, dchange):
    validation_errors = ""

    if pre.endswith('.'):
        pre = round((post / (100 + dchange)) * 100 ,2)
        validation_errors += "Fixed missing after dot for pre in {}, ".format(value_name)

    if post.endswith('.'):
        post = round((pre * (100 + dchange)) / 100 ,2)
        validation_errors += "Fixed missing after dot for post in {}, ".format(value_name)

    return validation_errors, ' '.join([pre, post, dchange])

def check_pred_pre_in_pred_pre_percentage_missing_after_dot(value_name, pred, pre, pred_pre_percent):
    validation_errors = ""

    if pred.endswith('.'):
        pred = round((pre / pred_pre_percent) * 100 ,2)
        validation_errors += "Fixed missing after dot for pred in {}, ".format(value_name)

    if pre.endswith('.'):
        pre = round((pred * pred_pre_percent) / 100 ,2)
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

def verify_numeric_results(value_name, value, file_format):
    validation_errors = ""
    if value == None:
        return "No value to validate for {},".format(value_name)
    try:
        if file_format == FORMATS.OLD.value.FULL:
            if value_name in NUMERIC_WITH_POST_FIELDS:
                pred, _, pre, pred_pre_percent, post, pred_post_percent, dchange = value.split(' ')
                validation_errors += validate_all(validation_errors, value_name, pred, pre, pred_pre_percent, post, pred_post_percent, dchange)
            elif value_name in ONLY_DCHANGE_VALIDATIONS_FIELDS:
                validation_errors += validate_only_dhcange(validation_errors, value_name, *value.split(' '))
            else:
                validation_errors += validate_only_pre_pred(validation_errors, value_name, *value.split(' '))
        elif file_format == FORMATS.OLD.value.WITHOUT_POST:
            validation_errors += validate_only_pre_pred(validation_errors, value_name, *value.split(' '))
        elif file_format == FORMATS.OLD.value.ONLY_SPIROMETRY:
            pred, _, pre, pred_pre_percent, post, pred_post_percent, dchange = value.split(' ')
            validation_errors += validate_all(validation_errors, value_name, pred, pre, pred_pre_percent, post,
                                              pred_post_percent, dchange)
        elif file_format == FORMATS.NEW.value.ONLY_SPIROMETRY_WITHOUT_POST:
            validation_errors += validate_only_pre_pred_new(validation_errors, value_name, *value.split(' '))
        elif file_format == FORMATS.NEW.value.ONLY_SPIROMETRY_WITH_POST:
            if value_name in NUMERIC_WITH_POST_FIELDS:
                pred, pre, pred_pre_percent, post, pred_post_percent, dchange = value.split(' ')
                validation_errors += validate_all(validation_errors, value_name, pred, pre, pred_pre_percent, post,
                                                  pred_post_percent, dchange)
            elif value_name in ONLY_DCHANGE_VALIDATIONS_FIELDS:
                validation_errors += validate_only_dhcange(validation_errors, value_name, *value.split(' '))

    except Exception as e:
        print(e)
        validation_errors += "Failed numeric validation for {}, ".format(value_name)
        return validation_errors

    return validation_errors

def verify_old_data_results(data):
    for field in NUMERIC_VALIDATE_FIELDS:
        validation_errors = verify_numeric_results(field, data[field], data["Format"])

        if data[field] != None and len([item for item in data[field].split(" ") if item.endswith('.')]) != 0:
            validation_errors += "Failed missing after dot validation for {}, ".format(field)

        data["Validator"] += validation_errors

    if data["Validator"] == "":
        data["Validator"] = "OK"

    return data

def verify_new_data_results(data):
    for field in NEW_NUMERIC_VALIDATE_FIELDS:
        validation_errors = verify_numeric_results(field, data[field], data["Format"])

        if data[field] != None and len([item for item in data[field].split(" ") if item.endswith('.')]) != 0:
            validation_errors += "Failed missing after dot validation for {}, ".format(field)

        data["Validator"] += validation_errors

    if data["Validator"] == "":
        data["Validator"] = "OK"

    return data