#!/usr/bin/env python3
"""
One-time repair for rows saved before the save_data.py fix for 2-value FEV1/FVC rows.

Bug: NEW-format reports print the FEV1/FVC row as "Ref Pre" when there is no post-BD
value. save_data.py stored them as PRE / POST, so 'FEV 1 % FVC_PRE' held the PREDICTED
ratio and 'FEV 1 % FVC_POST' held the MEASURED one.

Affected rows are recognised by the signature the old code left behind:
  Format starts with "NEW", FEV 1 % FVC_PRED empty, _PRE and _POST filled, _DCHANGE empty.
Repair:  PRED <- old PRE,  PRE <- old POST,  POST <- empty.

Usage:
  python fix_ratio_two_value_rows.py path/to/copd_extracted_data_trial.xlsx           # dry run
  python fix_ratio_two_value_rows.py path/to/copd_extracted_data_trial.xlsx --apply   # writes, keeps a backup
"""
import shutil
import sys
from datetime import datetime

import openpyxl
import pandas as pd

K = "FEV 1 % FVC"


def find_rows(df):
    empty = lambda c: df[c].isna() | (df[c].astype(str).str.strip().isin(["", "None", "nan"]))
    return (
        df["Format"].astype(str).str.startswith("NEW")
        & empty(f"{K}_PRED")
        & ~empty(f"{K}_PRE")
        & ~empty(f"{K}_POST")
        & empty(f"{K}_DCHANGE")
    )


def main(path, apply):
    df = pd.read_excel(path, engine="openpyxl")
    for c in (f"{K}_PRED", f"{K}_PRE", f"{K}_POST", f"{K}_DCHANGE", "Format"):
        if c not in df.columns:
            sys.exit(f"Column missing: {c}")

    rows = find_rows(df)
    print(f"Rows to repair: {int(rows.sum())} of {len(df)}")
    print(df.loc[rows, "Format"].value_counts().to_string())
    if not rows.any():
        return

    preview = df.loc[rows, [f"{K}_PRE", f"{K}_POST"]].rename(
        columns={f"{K}_PRE": "old PRE -> new PRED", f"{K}_POST": "old POST -> new PRE"})
    print(preview.to_string())

    if not apply:
        print("\nDry run only. Re-run with --apply to write the changes.")
        return

    backup = f"{path}.backup_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    shutil.copy2(path, backup)

    # Edit only the three ratio cells per affected row, so every other cell
    # (IDs with leading zeros, text fields) stays exactly as it was.
    wb = openpyxl.load_workbook(path)
    ws = wb.worksheets[0]
    header = {c.value: c.column for c in ws[1]}
    c_pred, c_pre, c_post = header[f"{K}_PRED"], header[f"{K}_PRE"], header[f"{K}_POST"]
    for idx in df.index[rows]:
        r = idx + 2  # +1 header row, +1 because Excel rows start at 1
        old_pre, old_post = ws.cell(r, c_pre).value, ws.cell(r, c_post).value
        ws.cell(r, c_pred).value = old_pre
        ws.cell(r, c_pre).value = old_post
        ws.cell(r, c_post).value = None
    wb.save(path)
    print(f"\nRepaired {int(rows.sum())} rows. Backup: {backup}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], "--apply" in sys.argv[2:])
