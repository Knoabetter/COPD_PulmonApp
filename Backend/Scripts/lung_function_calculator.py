import pandas as pd
import numpy as np
import os
from scipy.interpolate import interp1d

# ---------- CONFIGURATION ----------
BASE_DIR = r"C:\Users\Noadi\COPD_PulmonWebApp\Backend\Scripts\Data"
INPUT_FILE = os.path.join(BASE_DIR, "copd_extracted_data_AppDev.xlsx")
OUTPUT_FILE = os.path.join(BASE_DIR, "lung_function_predictions_GLI_based.xlsx")
FILE_LV = os.path.join(BASE_DIR, "inline-supplementary-material-2.xlsx")
FILE_TLCO = os.path.join(BASE_DIR, "inline-supplementary-material-3.xlsx")
FILE_SPIRO = os.path.join(BASE_DIR, "lookuptables.xlsx")

# ---------- HELPERS ----------
def check_file_exists(path, label):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ {label} not found: {path}")

def load_lms_tables(file_path, index_mapping):
    xls = pd.ExcelFile(file_path)
    lms_data = {}
    for index, sex_sheets in index_mapping.items():
        lms_data[index] = {}
        for sex, sheet in sex_sheets.items():
            df = xls.parse(sheet)
            df.columns = [c.strip().lower() for c in df.columns]
            lms_data[index][sex] = df[['age', 'mspline', 'sspline', 'lspline']]
    return lms_data

def load_gli_2012_lms(file_path):
    sheet_map = {
        'FEV1': {'M': 'FEV1 males', 'F': 'FEV1 females'},
        'FVC': {'M': 'FVC males', 'F': 'FVC females'},
        'FEV1_FVC': {'M': 'FEV1FVC males', 'F': 'FEV1FVC females'}
    }
    xls = pd.ExcelFile(file_path)
    lms_data = {}
    for index, sheets in sheet_map.items():
        lms_data[index] = {}
        for sex, sheet in sheets.items():
            df = xls.parse(sheet, skiprows=1)
            df.columns = [c.strip().lower() for c in df.columns]
            df = df[['age', 'lspline', 'mspline', 'sspline']].dropna()
            df = df[df['age'].apply(lambda x: isinstance(x, (int, float)))]
            lms_data[index][sex] = df.reset_index(drop=True)
    return lms_data

def interpolate_lms(index, sex, age, lms_all):
    df = lms_all[index][sex]
    M = interp1d(df['age'], df['mspline'], fill_value="extrapolate")(age)
    S = interp1d(df['age'], df['sspline'], fill_value="extrapolate")(age)
    L = interp1d(df['age'], df['lspline'], fill_value="extrapolate")(age)
    return float(M), float(S), float(L)

def compute_predicted_lln(M, S, L):
    try:
        if L != 0:
            term = 1 - 1.645 * L * S  # Corrected formula
            if term <= 0:
                return np.nan, np.nan
            LLN = M * (term)**(1/L)
        else:
            LLN = M * np.exp(-1.645 * S)
        
        # Ensure positive values
        if M <= 0 or LLN <= 0:
            return np.nan, np.nan
            
    except:
        LLN = np.nan
    return M, LLN

def process_patient_row(row, lms_all, gli_2012_lms):
    age = row['Age']
    height = row['Height_cm']
    sex = str(row['Sex']).strip().upper()
    ethnicity = row['Ethnicity'] if 'Ethnicity' in row and pd.notna(row['Ethnicity']) else 'Caucasian'

    if sex not in ['M', 'F']:
        print(f"⚠️ Invalid sex '{sex}' for patient ID {row.get('ID', 'Unknown')}")
        return pd.Series()

    results = {}

    for index in lms_all.keys():
        try:
            M, S, L = interpolate_lms(index, sex, age, lms_all)
            pred, lln = compute_predicted_lln(M, S, L)
        except:
            pred, lln = np.nan, np.nan
        results[f'{index}_predicted'] = pred
        results[f'{index}_LLN'] = lln

    for index in gli_2012_lms.keys():
        try:
            M, S, L = interpolate_lms(index, sex, age, gli_2012_lms)
            pred, lln = compute_predicted_lln(M, S, L)
        except:
            pred, lln = np.nan, np.nan
        results[f'{index}_predicted'] = pred
        results[f'{index}_LLN'] = lln

    return pd.Series(results)

# ---------- MAIN ----------
def main():
    for f, name in [(INPUT_FILE, "Patient data"), (FILE_LV, "GLI 2021 Lung Volumes"),
                    (FILE_TLCO, "GLI 2021 TLCO"), (FILE_SPIRO, "GLI 2012 Spirometry")]:
        check_file_exists(f, name)

    df = pd.read_excel(INPUT_FILE, engine="openpyxl")
    if 'Height' in df.columns:
        df.rename(columns={"Height": "Height_cm"}, inplace=True)

    if not all(col in df.columns for col in ['Age', 'Sex', 'Height_cm']):
        raise ValueError("Missing one of the required columns: Age, Sex, Height_cm")

    if 'Ethnicity' not in df.columns:
        print("ℹ️ No Ethnicity column found — defaulting to 'Caucasian'")

    lms_lv = load_lms_tables(FILE_LV, {
        'FRC': {'M': 'frc_m_lookuptable', 'F': 'frc_f_lookuptable'},
        'TLC': {'M': 'tlc_m_lookuptable', 'F': 'tlc_f_lookuptable'},
        'RV': {'M': 'rv_m_lookuptable', 'F': 'rv_f_lookuptable'},
        'RV_TLC': {'M': 'rvtlc_m_lookuptable', 'F': 'rvtlc_f_lookuptable'},
        'ERV': {'M': 'erv_m_lookuptable', 'F': 'erv_f_lookuptable'},
        'IC': {'M': 'ic_m_lookuptable', 'F': 'ic_f_lookuptable'},
        'VC': {'M': 'vc_m_lookuptable', 'F': 'vc_f_lookuptable'}
    })

    lms_tlco = load_lms_tables(FILE_TLCO, {
        'DLCO': {'M': 'DLCO_m', 'F': 'DLCO_f'},
        'KCO': {'M': 'KCO_m', 'F': 'KCO_f'},
        'VA': {'M': 'VA_m', 'F': 'VA_f'}
    })

    gli_2012_lms = load_gli_2012_lms(FILE_SPIRO)
    lms_all = {**lms_lv, **lms_tlco}

    print(f"🔄 Processing {len(df)} patients...")
    results = df.apply(lambda row: process_patient_row(row, lms_all, gli_2012_lms), axis=1)
    results_df = pd.concat([df, results], axis=1)
    results_df.to_excel(OUTPUT_FILE, index=False)

    print(f"✅ Done! Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
