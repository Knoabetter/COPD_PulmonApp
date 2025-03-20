from consts import ROUND_ERROR_LEEWAY, ONLY_DCHANGE_VALIDATIONS_FIELDS


def validate_dchange(pre, post, dchange):
    return abs(post - round(((100 + dchange) * pre) / 100, 2)) < ROUND_ERROR_LEEWAY


def validate_post_pred_percent(post, pred, percent):
    return abs(post - round((pred * percent) / 100, 2)) < ROUND_ERROR_LEEWAY


def validate_pre_pred_percent(pre, pred, percent):
    return abs(pre - round((pred * percent) / 100, 2)) < ROUND_ERROR_LEEWAY


def get_full_values(value):
    if value.count(' ') == 6:
        pred, _, pre, pred_pre_percent, post, pred_post_percent, dchange = value.split(' ')
    else:
        pred, pre, pred_pre_percent, post, pred_post_percent, dchange = value.split(' ')

    return pred, pre, pred_pre_percent, post, pred_post_percent, dchange


def validate_all(validation_errors, value_name, value):
    pred, pre, pred_pre_percent, post, pred_post_percent, dchange = get_full_values(value)

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


def verify_numeric_results(value_name, value):
    validation_errors = ""
    if value is None:
        return "No value to validate for {},".format(value_name)
    try:
        if value_name in ONLY_DCHANGE_VALIDATIONS_FIELDS:
            validation_errors += validate_only_dhcange(validation_errors, value_name, *value.split(' '))
        elif value.count(' ') == 2 or value.count(' ') == 3:
            validation_errors += validate_only_pre_pred(validation_errors, value_name, value)
        else:
            validation_errors += validate_all(validation_errors, value_name, value)
    except Exception as e:
        print(e)
        validation_errors += "Failed numeric validation for {}, ".format(value_name)
        return validation_errors

    return validation_errors


def verify_data_results(data, numeric_fields_to_validate):
    for key in data.keys():
        if key in numeric_fields_to_validate:
            validation_errors = verify_numeric_results(key, data[key])

            if data[key] is not None and len([item for item in data[key].split(" ") if item.endswith('.')]) != 0:
                validation_errors += "Failed missing after dot validation for {}, ".format(key)

            data["Validator"] += validation_errors

    if data["Validator"] == "":
        data["Validator"] = "OK"

    return data
