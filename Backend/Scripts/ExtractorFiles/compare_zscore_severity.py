#!/usr/bin/env python3
"""
Bug 3 check: how many tests change ERS 2022 severity when the approximate z-score
    z ~ (meas - pred) / ((pred - LLN) / 1.645)
is replaced by the exact GLI 2012 LMS z-score
    z = ((meas / M)^L - 1) / (L * S).

Uses the same branch logic as ClinicalInterpreter.interpret_ers2022_algorithm:
  FEV1/FVC < LLN            -> severity from FEV1 z   (Mild >= -2.5, Moderate >= -4, Severe < -4)
  FEV1/FVC >= LLN, FVC < LLN -> severity from FVC z   (Borderline >= -1.645, then the same bands)
  otherwise                 -> Normal (no z grading)

Usage:  python compare_zscore_severity.py copd_extracted_data_trial.xlsx
Output: counts on screen + zscore_severity_comparison.csv (one row per usable test)
"""
import io
import sys
import contextlib

import numpy as np
import pandas as pd

from working_calculator import WorkingGLI2012Calculator, gli_z_score

AGE_RANGE, HEIGHT_RANGE, RATIO_RANGE = (18, 95), (120, 220), (0.20, 1.00)


def grade(z, borderline=False):
    if z is None or np.isnan(z):
        return 'Unknown'
    if borderline and z >= -1.645:
        return 'Borderline'
    if z >= -2.5:
        return 'Mild'
    if z >= -4.0:
        return 'Moderate'
    return 'Severe'


def approx_z(meas, pred, lln):
    if not (pred > 0 and lln > 0 and pred > lln):
        return None
    return (meas - pred) / ((pred - lln) / 1.645)


def num(row, key):
    v = pd.to_numeric(row.get(key), errors='coerce')
    return None if pd.isna(v) else float(v)


def main(path):
    df = pd.read_excel(path)
    gli = WorkingGLI2012Calculator()
    with contextlib.redirect_stdout(io.StringIO()):
        if not gli.load_gli_tables():
            sys.exit("GLI tables failed to load")

    out, skipped = [], 0
    for i, row in df.iterrows():
        age, height = num(row, 'Age'), num(row, 'Height')
        sex = str(row.get('Sex', '')).strip().upper()[:1]
        fev1, fvc = num(row, 'FEV1_PRE'), num(row, 'FVC_PRE')
        ratio = num(row, 'FEV 1 % FVC_PRE')
        if ratio is not None and ratio > 1.5:
            ratio /= 100.0
        if ratio is None and fev1 and fvc:
            ratio = fev1 / fvc
        if (age is None or height is None or sex not in ('M', 'F') or not fev1 or not fvc or ratio is None
                or not AGE_RANGE[0] <= age <= AGE_RANGE[1] or not HEIGHT_RANGE[0] <= height <= HEIGHT_RANGE[1]
                or not RATIO_RANGE[0] <= ratio <= RATIO_RANGE[1]):
            skipped += 1
            continue

        with contextlib.redirect_stdout(io.StringIO()):
            g = gli.calculate_patient(age, sex, height)

        z = {}
        for p, m in (('FEV1', fev1), ('FVC', fvc), ('FEV1_FVC', ratio)):
            z[p, 'exact'] = gli_z_score(m, g[f'{p}_GLI_M'], g[f'{p}_GLI_S'], g[f'{p}_GLI_L'])
            z[p, 'approx'] = approx_z(m, g[f'{p}_GLI_pred'], g[f'{p}_GLI_LLN'])

        obstructed = ratio < g['FEV1_FVC_GLI_LLN']
        fvc_low = fvc < g['FVC_GLI_LLN']
        if obstructed:
            branch = 'Obstruction'
            sev_old, sev_new = grade(z['FEV1', 'approx']), grade(z['FEV1', 'exact'])
        elif fvc_low:
            branch = 'Low FVC'
            sev_old = grade(z['FVC', 'approx'], borderline=True)
            sev_new = grade(z['FVC', 'exact'], borderline=True)
        else:
            branch, sev_old, sev_new = 'Normal', 'Normal', 'Normal'

        out.append({
            'row': i + 2, 'Format': row.get('Format'), 'Age': age, 'Sex': sex, 'Height': height,
            'branch': branch,
            'FEV1_z_approx': z['FEV1', 'approx'], 'FEV1_z_exact': z['FEV1', 'exact'],
            'FVC_z_approx': z['FVC', 'approx'], 'FVC_z_exact': z['FVC', 'exact'],
            'ratio_z_approx': z['FEV1_FVC', 'approx'], 'ratio_z_exact': z['FEV1_FVC', 'exact'],
            'severity_approx': sev_old, 'severity_exact': sev_new,
            'changed': sev_old != sev_new,
        })

    res = pd.DataFrame(out)
    res.round(3).to_csv('zscore_severity_comparison.csv', index=False)
    print(f"Usable tests: {len(res)}   (skipped: {skipped} — missing/out-of-range values)")
    if res.empty:
        return
    print(f"\nBranch counts:\n{res['branch'].value_counts().to_string()}")
    print(f"\nSeverity changed: {int(res['changed'].sum())} of {len(res)}")
    if res['changed'].any():
        print(res.loc[res['changed'], ['row', 'branch', 'FEV1_z_approx', 'FEV1_z_exact', 'FVC_z_approx',
                                       'FVC_z_exact', 'severity_approx', 'severity_exact']].round(2).to_string(index=False))
    print("\nCross-table (rows = approx, columns = exact):")
    print(pd.crosstab(res['severity_approx'], res['severity_exact']).to_string())
    for p in ('FEV1', 'FVC', 'ratio'):
        d = (res[f'{p}_z_exact'] - res[f'{p}_z_approx']).abs()
        print(f"{p:5s} |exact - approx| z: median {d.median():.3f}, max {d.max():.3f}")
    print("\nSaved: zscore_severity_comparison.csv")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
