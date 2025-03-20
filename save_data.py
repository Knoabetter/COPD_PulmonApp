import pandas as pd

from consts import DATABASE_FILE_NAME, ONLY_DCHANGE_VALIDATIONS_FIELDS, NUMERIC_WITH_POST_FIELDS, \
    EXPAND_PRED_PRE_PERCENT_FIELDS, NEW_NUMERIC_VALIDATE_FIELDS


def expand_full_numeric_row(data, key):
    if data[key] == None:
        data[key + '_PRED'] = None
        data[key + '_LLN'] = None
        data[key + '_PRE'] = None
        data[key + '_PRE_PERCENT'] = None
        data[key + '_POST'] = None
        data[key + '_POST_PERCENT'] = None
        data[key + '_DCHANGE'] = None
    elif len(data[key].split(' ')) == 3:
        pred, pre, pred_pre_percent = data[key].split(' ')
        data[key + '_PRED'] = pred
        data[key + '_LLN'] = None
        data[key + '_PRE'] = pre
        data[key + '_PRE_PERCENT'] = pred_pre_percent
        data[key + '_POST'] = None
        data[key + '_POST_PERCENT'] = None
        data[key + '_DCHANGE'] = None
    elif len(data[key].split(' ')) == 4:
        pred, LLN, pre, pred_pre_percent = data[key].split(' ')
        data[key + '_PRED'] = pred
        data[key + '_LLN'] = LLN
        data[key + '_PRE'] = pre
        data[key + '_PRE_PERCENT'] = pred_pre_percent
        data[key + '_POST'] = None
        data[key + '_POST_PERCENT'] = None
        data[key + '_DCHANGE'] = None
    elif len(data[key].split(' ')) == 6:
        pred, pre, pred_pre_percent, post, pred_post_percent, dchange = data[key].split(' ')

        data[key + '_PRED'] = pred
        data[key + '_PRE'] = pre
        data[key + '_PRE_PERCENT'] = pred_pre_percent
        data[key + '_POST'] = post
        data[key + '_POST_PERCENT'] = pred_post_percent
        data[key + '_DCHANGE'] = dchange
    elif len(data[key].split(' ')) == 7:
        pred, LLN, pre, pred_pre_percent, post, pred_post_percent, dchange = data[key].split(' ')

        data[key + '_PRED'] = pred
        data[key + '_LLN'] = LLN
        data[key + '_PRE'] = pre
        data[key + '_PRE_PERCENT'] = pred_pre_percent
        data[key + '_POST'] = post
        data[key + '_POST_PERCENT'] = pred_post_percent
        data[key + '_DCHANGE'] = dchange

    del data[key]

    return data

def expand_pred_pre_percent(data, key):
    if data[key] == None:
        data[key + '_PRED'] = None
        data[key + '_LLN'] = None
        data[key + '_PRE'] = None
        data[key + '_PRE_PERCENT'] = None
    elif len(data[key].split(' ')) == 2:
        pred, LLN = data[key].split(' ')

        data[key + '_PRED'] = pred
        data[key + '_LLN'] = LLN
        data[key + '_PRE'] = None
        data[key + '_PRE_PERCENT'] = None
    elif len(data[key].split(' ')) == 4:
        pred, LLN, pre, pred_pre_percent = data[key].split(' ')

        data[key + '_PRED'] = pred
        data[key + '_LLN'] = LLN
        data[key + '_PRE'] = pre
        data[key + '_PRE_PERCENT'] = pred_pre_percent

    del data[key]

    return data

def expand_pre_post_dchange(data, key):
    if data[key] == None:
        data[key + '_PRE'] = None
        data[key + '_POST'] = None
        data[key + '_DCHANGE'] = None
    elif len(data[key].split(' ')) == 3:
        pre, post, dchange = data[key].split(' ')

        data[key + '_PRE'] = pre
        data[key + '_POST'] = post
        data[key + '_DCHANGE'] = dchange
    elif len(data[key].split(' ')) == 4:
        pred, pre, post, dchange = data[key].split(' ')

        data[key + '_PRED'] = pred
        data[key + '_PRE'] = pre
        data[key + '_POST'] = post
        data[key + '_DCHANGE'] = dchange

    del data[key]

    return data

def expand_date(data):
    if data["Date"] == None:
        data["Date_PRE"], data["Date_POST"] = None, None
    elif len(data["Date"].split(' ')) == 1:
        data["Date_PRE"] = data["Date"]
        data["Date_POST"] = None
    elif len(data["Date"].split(' ')) == 2:
        data["Date_PRE"], data["Date_POST"] = data["Date"].split(' ')
    elif len(data["Date"].split(' ')) == 3:
        data["Date_PRE"] = '/'.join(data["Date"].split(' '))
        data["Date_POST"] = None

    del data["Date"]

    return data

def add_id_control_digit(id):
    if id == None:
        return None
    if len(id) == 7:
        id = '0' + id
    if len(id) == 6:
        id = '00' + id

    calculate_israeli_id_control_digit = lambda id_number: (10 - sum(
        (int(d) * (1 + i % 2)) // 10 + (int(d) * (1 + i % 2)) % 10 for i, d in enumerate(id_number)) % 10) % 10

    return id + str(calculate_israeli_id_control_digit(id))

def expand_data_keys(data):
    keys = list(data.keys())

    for key in keys:
        if key in ONLY_DCHANGE_VALIDATIONS_FIELDS:
            data = expand_pre_post_dchange(data, key)
        elif key in EXPAND_PRED_PRE_PERCENT_FIELDS:
            data = expand_pred_pre_percent(data, key)
        elif key in NUMERIC_WITH_POST_FIELDS or key in NEW_NUMERIC_VALIDATE_FIELDS:
            data = expand_full_numeric_row(data, key)
        elif key == "ID":
            data[key] = add_id_control_digit(data[key])
        elif key == "Date":
            data = expand_date(data)

    return data

def append_data(data):
    print(data)
    data = expand_data_keys(data)
    print(data)
    try:
        df = pd.read_excel(DATABASE_FILE_NAME, engine='openpyxl')
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([data])


    df.to_excel(DATABASE_FILE_NAME, index=False, engine='openpyxl')