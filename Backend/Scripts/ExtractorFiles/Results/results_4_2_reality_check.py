# results_4_2_reality_check.py
"""
VALIDATION: Agreement with reality (continuous only) + Bland–Altman
- Patient_ID is derived from the extracted (measured) data and mirrored in validation.
- Strict inner join on the derived Patient_ID.

Inputs (same folder):
  - real_extracted_validation_results.csv   # has murray_* and gli_* predictions + Age/Sex/Height
  - copd_extracted_data_trial.xlsx          # measured spirometry values + Age/Sex/Height

Outputs:
  - table_method_vs_measured.csv
  - figure_scatter_measured_vs_GLI.png
  - figure_scatter_measured_vs_Murray.png
  - figure_bland_altman_measured_vs_GLI.png
  - figure_bland_altman_measured_vs_Murray.png
"""

import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
VALIDATION_FILE = "real_extracted_validation_results.csv"
MEASURED_FILE   = "copd_extracted_data_trial.xlsx"

TABLE_OUT       = "table_method_vs_measured.csv"
SCATTER_GLI     = "figure_scatter_measured_vs_GLI.png"
SCATTER_MUR     = "figure_scatter_measured_vs_Murray.png"
BA_GLI          = "figure_bland_altman_measured_vs_GLI.png"
BA_MUR          = "figure_bland_altman_measured_vs_Murray.png"

# Rounding rules for ID derivation (tune if needed)
AGE_DECIMALS    = 1   # e.g., 64.3 years
HEIGHT_DECIMALS = 0   # e.g., 170 cm

# ---------------- HELPERS ----------------
def require_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")

def first_present(df, candidates):
    """Return the first column name that exists in df from the candidate list, else None."""
    for c in candidates:
        if c in df.columns:
            return c
    return None

def std_sex_series(s):
    """Normalize sex values to 'M'/'F' first letter uppercase."""
    return s.astype(str).str.strip().str.upper().str[0]

def to_num(series, dec=None):
    """Coerce to numeric; optionally round to 'dec' decimals."""
    x = pd.to_numeric(series, errors="coerce")
    if dec is not None:
        x = x.round(dec)
    return x

def safe_ratio(series):
    """Convert % to fraction if needed; leave [0..1] alone; coerce to float."""
    x = pd.to_numeric(series, errors="coerce")
    return np.where(x > 1.5, x / 100.0, x)

def pair_clean(a, b):
    """Return aligned float numpy arrays with non-NaN pairs (accepts Series/ndarray/list)."""
    def to_num_array(z):
        if isinstance(z, pd.Series):
            return pd.to_numeric(z, errors="coerce").to_numpy()
        return pd.to_numeric(pd.Series(z), errors="coerce").to_numpy()
    x = to_num_array(a)
    y = to_num_array(b)
    m = (~np.isnan(x)) & (~np.isnan(y))
    return x[m], y[m]

def pearson_and_paired_t(a, b):
    x, y = pair_clean(a, b)
    n = len(x)
    if n < 2:
        return np.nan, np.nan, n
    r, _ = stats.pearsonr(x, y)
    _, p = stats.ttest_rel(x, y)
    return r, p, n

def lin_ccc(a, b):
    """Lin’s Concordance Correlation Coefficient."""
    x, y = pair_clean(a, b)
    n = len(x)
    if n < 2:
        return np.nan
    mx, my = x.mean(), y.mean()
    vx, vy = x.var(ddof=1), y.var(ddof=1)
    cov = np.cov(x, y, ddof=1)[0, 1]
    denom = vx + vy + (mx - my) ** 2
    if denom == 0:
        return np.nan
    return (2 * cov) / denom

def bland_altman_axes(ax, measured, predicted, title):
    """Draw Bland–Altman and return dict with bias & LoA."""
    x, y = pair_clean(measured, predicted)  # x = measured, y = predicted
    if len(x) < 3:
        ax.set_visible(False); return None
    diff = y - x
    mean = (y + x) / 2
    bias = float(np.mean(diff))
    sd   = float(np.std(diff, ddof=1))
    loa_low, loa_high = bias - 1.96*sd, bias + 1.96*sd

    ax.scatter(mean, diff, s=16)
    ax.axhline(bias,     linestyle='-')
    ax.axhline(loa_low,  linestyle='--')
    ax.axhline(loa_high, linestyle='--')
    ax.set_title(f"{title}\nBias={bias:.3g}, LoA [{loa_low:.3g}, {loa_high:.3g}]")
    ax.set_xlabel("Mean of (Measured, Predicted)")
    ax.set_ylabel("Pred − Measured")
    return {"bias": bias, "loa_low": loa_low, "loa_high": loa_high}

def round_cols(df, cols, k=3):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").round(k)
    return df

# ---------------- LOAD ----------------
require_file(VALIDATION_FILE)
require_file(MEASURED_FILE)

val = pd.read_csv(VALIDATION_FILE)
meas = pd.read_excel(MEASURED_FILE)

# ---------------- PREP MEASURED (REALITY) ----------------
# Locate columns
m_sex_col    = first_present(meas, ["Sex","sex","Gender","gender"])
m_age_col    = first_present(meas, ["Age","age"])
m_height_col = first_present(meas, ["Height","height","Ht","Ht(cm)","Height_cm"])

if not all([m_sex_col, m_age_col, m_height_col]):
    raise RuntimeError("Measured file must contain Sex, Age, and Height to derive Patient_ID.")

meas_use = meas.copy()
meas_use["__Sex__"]    = std_sex_series(meas_use[m_sex_col])
meas_use["__Age__"]    = to_num(meas_use[m_age_col], dec=AGE_DECIMALS)
meas_use["__Height__"] = to_num(meas_use[m_height_col], dec=HEIGHT_DECIMALS)

# Measured spirometry (FEV1, FVC, Ratio)
col_fev1 = first_present(meas_use, ["FEV1_PRE", "FEV1", "fev1", "FEV1 (L)"])
col_fvc  = first_present(meas_use, ["FVC_PRE", "FVC", "fvc", "FVC (L)"])
col_ratio_percent = first_present(meas_use, ["FEV 1 % FVC_PRE", "FEV1%FVC_PRE", "FEV1/FVC%", "FEV1%FVC"])
col_ratio_frac    = first_present(meas_use, ["measured_ratio", "FEV1_FVC", "ratio", "FEV1/FVC"])

meas_use["__measured_fev1__"] = to_num(meas_use[col_fev1]) if col_fev1 else np.nan
meas_use["__measured_fvc__"]  = to_num(meas_use[col_fvc])  if col_fvc  else np.nan

if col_ratio_frac:
    meas_use["__measured_ratio__"] = safe_ratio(meas_use[col_ratio_frac])
elif col_ratio_percent:
    meas_use["__measured_ratio__"] = safe_ratio(meas_use[col_ratio_percent])
else:
    if col_fev1 and col_fvc:
        meas_use["__measured_ratio__"] = pd.to_numeric(meas_use[col_fev1], errors="coerce") / pd.to_numeric(meas_use[col_fvc], errors="coerce")
    else:
        meas_use["__measured_ratio__"] = np.nan

# ---------------- DERIVE Patient_ID FROM MEASURED ----------------
meas_use["__basekey__"] = (
    meas_use["__Sex__"].astype(str) + "_" +
    meas_use["__Age__"].astype(str) + "_" +
    meas_use["__Height__"].astype(str)
)
meas_use["_k"] = meas_use.groupby("__basekey__").cumcount() + 1
meas_use["Patient_ID"] = meas_use["__basekey__"] + "_" + meas_use["_k"].astype(str)

# ---------------- MIRROR THE SAME KEY IN VALIDATION ----------------
v_sex_col    = first_present(val, ["Sex","sex","Gender","gender"])
v_age_col    = first_present(val, ["Age","age"])
v_height_col = first_present(val, ["Height","height"])

if not all([v_sex_col, v_age_col, v_height_col]):
    raise RuntimeError("Validation CSV must contain Sex, Age, and Height to mirror Patient_ID.")

val["__Sex__"]    = std_sex_series(val[v_sex_col])
val["__Age__"]    = to_num(val[v_age_col], dec=AGE_DECIMALS)
val["__Height__"] = to_num(val[v_height_col], dec=HEIGHT_DECIMALS)

val["__basekey__"] = (
    val["__Sex__"].astype(str) + "_" +
    val["__Age__"].astype(str) + "_" +
    val["__Height__"].astype(str)
)
val["_k"] = val.groupby("__basekey__").cumcount() + 1
val["Patient_ID"] = val["__basekey__"] + "_" + val["_k"].astype(str)

# ---------------- STRICT JOIN ON DERIVED Patient_ID ----------------
cols_needed = ["Patient_ID", "__measured_fev1__", "__measured_fvc__", "__measured_ratio__"]
vm = pd.merge(val, meas_use[cols_needed], on="Patient_ID", how="inner")

if vm.empty:
    raise RuntimeError("Join on derived Patient_ID produced 0 rows. Check Sex/Age/Height availability/rounding.")

print(f"[info] Joined by derived Patient_ID: {len(vm)} rows (pred={len(val)}, meas={len(meas_use)})")

# ---------------- BUILD TABLE: METHOD vs MEASURED ----------------
def add_stats_row(df_rows, method_name, pred_col, meas_col, metric_label):
    x, y = pair_clean(vm[meas_col], vm[pred_col])  # x=measured, y=pred
    n = len(x)
    if n < 2:
        df_rows.append({"Method": method_name, "Metric": metric_label, "n": n})
        return

    r, p, _ = pearson_and_paired_t(x, y)
    ccc = lin_ccc(x, y)
    diff = y - x
    bias = float(np.mean(diff))
    sd   = float(np.std(diff, ddof=1))
    loa_low, loa_high = bias - 1.96*sd, bias + 1.96*sd

    df_rows.append({
        "Method": method_name,
        "Metric": metric_label,
        "n": n,
        "Measured mean": float(np.mean(x)),
        "Measured sd":   float(np.std(x, ddof=1)),
        "Predicted mean":float(np.mean(y)),
        "Predicted sd":  float(np.std(y, ddof=1)),
        "Pearson r": r,
        "Paired t p": p,
        "CCC": ccc,
        "Mean diff (Pred−Meas)": bias,
        "SD diff": sd,
        "LoA low": loa_low,
        "LoA high": loa_high
    })

rows = []
# GLI vs Measured
add_stats_row(rows, "GLI",    "gli_fev1",  "__measured_fev1__",  "FEV1 (L)")
add_stats_row(rows, "GLI",    "gli_fvc",   "__measured_fvc__",   "FVC (L)")
add_stats_row(rows, "GLI",    "gli_ratio", "__measured_ratio__", "FEV1/FVC (ratio)")
# Murray vs Measured
add_stats_row(rows, "Murray", "murray_fev1",  "__measured_fev1__",  "FEV1 (L)")
add_stats_row(rows, "Murray", "murray_fvc",   "__measured_fvc__",   "FVC (L)")
add_stats_row(rows, "Murray", "murray_ratio", "__measured_ratio__", "FEV1/FVC (ratio)")

table = pd.DataFrame(rows)
table = round_cols(
    table,
    ["Measured mean","Measured sd","Predicted mean","Predicted sd",
     "Pearson r","Paired t p","CCC","Mean diff (Pred−Meas)","SD diff","LoA low","LoA high"],
    3
)
table.to_csv(TABLE_OUT, index=False)

# ---------------- FIGURES: SCATTER Measured vs GLI ----------------
figA, axesA = plt.subplots(1, 3, figsize=(15, 4))
pairsA = [
    ("__measured_fev1__", "gli_fev1",  "FEV1 (L)"),
    ("__measured_fvc__",  "gli_fvc",   "FVC (L)"),
    ("__measured_ratio__","gli_ratio", "FEV1/FVC (ratio)")
]
for ax, (mcol, pcol, label) in zip(axesA, pairsA):
    x, y = pair_clean(vm[mcol], vm[pcol])
    if len(x) == 0: ax.set_visible(False); continue
    ax.scatter(x, y, s=16)
    lo, hi = min(np.min(x), np.min(y)), max(np.max(x), np.max(y))
    ax.plot([lo, hi], [lo, hi], linestyle="--")
    r, p, n = pearson_and_paired_t(x, y)
    ccc = lin_ccc(x, y)
    ax.text(0.02, 0.98, f"r={r:.3f}\np={p:.3g}\nCCC={ccc:.3f}\nn={n}",
            transform=ax.transAxes, ha="left", va="top",
            bbox=dict(boxstyle="round", alpha=0.15))
    ax.set_xlabel(f"Measured {label}"); ax.set_ylabel(f"GLI {label}")
figA.suptitle("Measured vs GLI — Scatter with equality line", y=1.02, fontsize=11)
figA.tight_layout(); figA.savefig(SCATTER_GLI, dpi=300); plt.close(figA)

# ---------------- FIGURES: SCATTER Measured vs Murray ----------------
figB, axesB = plt.subplots(1, 3, figsize=(15, 4))
pairsB = [
    ("__measured_fev1__", "murray_fev1",  "FEV1 (L)"),
    ("__measured_fvc__",  "murray_fvc",   "FVC (L)"),
    ("__measured_ratio__","murray_ratio", "FEV1/FVC (ratio)")
]
for ax, (mcol, pcol, label) in zip(axesB, pairsB):
    x, y = pair_clean(vm[mcol], vm[pcol])
    if len(x) == 0: ax.set_visible(False); continue
    ax.scatter(x, y, s=16)
    lo, hi = min(np.min(x), np.min(y)), max(np.max(x), np.max(y))
    ax.plot([lo, hi], [lo, hi], linestyle="--")
    r, p, n = pearson_and_paired_t(x, y)
    ccc = lin_ccc(x, y)
    ax.text(0.02, 0.98, f"r={r:.3f}\np={p:.3g}\nCCC={ccc:.3f}\nn={n}",
            transform=ax.transAxes, ha="left", va="top",
            bbox=dict(boxstyle="round", alpha=0.15))
    ax.set_xlabel(f"Measured {label}"); ax.set_ylabel(f"Murray {label}")
figB.suptitle("Measured vs Murray — Scatter with equality line", y=1.02, fontsize=11)
figB.tight_layout(); figB.savefig(SCATTER_MUR, dpi=300); plt.close(figB)

# ---------------- FIGURES: Bland–Altman (Measured vs GLI) ----------------
figC, axesC = plt.subplots(1, 3, figsize=(15, 4))
ba_pairsC = [
    ("__measured_fev1__", "gli_fev1",  "FEV1 (GLI − Measured)"),
    ("__measured_fvc__",  "gli_fvc",   "FVC (GLI − Measured)"),
    ("__measured_ratio__","gli_ratio", "FEV1/FVC (GLI − Measured)")
]
for ax, (mcol, pcol, title) in zip(axesC, ba_pairsC):
    bland_altman_axes(ax, vm[mcol], vm[pcol], title)
figC.suptitle("Bland–Altman — Measured vs GLI", y=1.02, fontsize=11)
figC.tight_layout(); figC.savefig(BA_GLI, dpi=300); plt.close(figC)

# ---------------- FIGURES: Bland–Altman (Measured vs Murray) ----------------
figD, axesD = plt.subplots(1, 3, figsize=(15, 4))
ba_pairsD = [
    ("__measured_fev1__", "murray_fev1",  "FEV1 (Murray − Measured)"),
    ("__measured_fvc__",  "murray_fvc",   "FVC (Murray − Measured)"),
    ("__measured_ratio__","murray_ratio", "FEV1/FVC (Murray − Measured)")
]
for ax, (mcol, pcol, title) in zip(axesD, ba_pairsD):
    bland_altman_axes(ax, vm[mcol], vm[pcol], title)
figD.suptitle("Bland–Altman — Measured vs Murray", y=1.02, fontsize=11)
figD.tight_layout(); figD.savefig(BA_MUR, dpi=300); plt.close(figD)

print("✅ Done. Generated:")
print(f"- {TABLE_OUT}")
print(f"- {SCATTER_GLI}")
print(f"- {SCATTER_MUR}")
print(f"- {BA_GLI}")
print(f"- {BA_MUR}")
