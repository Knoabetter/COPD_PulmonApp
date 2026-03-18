# results_4_2_generator.py
"""
COPD Results 4.2 — Tables & Figures (robust, unit-safe, join-safe)

Outputs (in current folder):
  - table_4_1_validation_summary.csv       # Murray vs GLI (FEV1, FVC, Ratio): r, p (paired t), CCC, descriptives
  - table_4_1b_method_vs_measured.csv      # Each method vs Measured: r, p (paired t), CCC, descriptives
  - table_4_2_diagnostic_agreement.csv     # Agreement %, 2x2, McNemar p, Cohen's kappa (recomputed robustly)
  - figure_4_1_real_data_comparison.png    # Scatter panels Murray vs GLI with y=x, r, p, CCC, n
  - figure_4_2_real_diagnostic_agreement.png  # 2x2 matrix (counts)

Inputs (same folder):
  - real_extracted_validation_results.csv   # has murray_* and gli_* predictions
  - real_extracted_diagnostic_agreement.csv # may have buggy labels; we recompute robustly
  different folder
  - ExtractorFiles/copd_extracted_data_trial.xlsx          # measured spirometry values

Notes:
- Ratio values are handled as FRACTIONS (0–1). Any % is converted once.
- Join preference for Table 4.1b: Source_ID → Patient_ID → Case → ID. No unsafe row-order fallbacks.
- Figures use matplotlib only, no seaborn.
"""

import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# ------------------ CONFIG ------------------
VALIDATION_FILE = "real_extracted_validation_results.csv"
DIAGNOSTIC_FILE = "real_extracted_diagnostic_agreement.csv"
MEASURED_FILE   = "ExtractorFiles/copd_extracted_data_trial.xlsx"

TABLE_4_1_OUT  = "table_4_1_validation_summary.csv"
TABLE_4_1B_OUT = "table_4_1b_method_vs_measured.csv"
TABLE_4_2_OUT  = "table_4_2_diagnostic_agreement.csv"

FIGURE_4_1_OUT = "figure_4_1_real_data_comparison.png"
FIGURE_4_2_OUT = "figure_4_2_real_diagnostic_agreement.png"

# ------------------ UTILITIES ------------------
def require_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")

def safe_ratio(series):
    """Convert % to fraction if needed; leave [0..1] alone; coerce to float."""
    x = pd.to_numeric(series, errors="coerce")
    return np.where(x > 1.5, x / 100.0, x)

def pair_clean(a, b):
    """Return aligned float numpy arrays with non-NaN pairs (accepts Series/ndarray/list)."""
    def to_num_array(z):
        if isinstance(z, pd.Series):
            return pd.to_numeric(z, errors="coerce").to_numpy()
        # ndarray/list/iterable → Series → numeric → ndarray
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

def round_cols(df, cols, k=3):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").round(k)
    return df

def first_present(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

# ------------------ LOAD DATA ------------------
require_file(VALIDATION_FILE)
require_file(DIAGNOSTIC_FILE)
require_file(MEASURED_FILE)

val = pd.read_csv(VALIDATION_FILE)
diag = pd.read_csv(DIAGNOSTIC_FILE)
meas = pd.read_excel(MEASURED_FILE)

# ------------------ PREP MEASURED COLUMNS ------------------
col_fev1 = first_present(meas, ["FEV1_PRE", "FEV1", "fev1", "FEV1 (L)"])
col_fvc  = first_present(meas, ["FVC_PRE", "FVC", "fvc", "FVC (L)"])
col_ratio_percent = first_present(meas, ["FEV 1 % FVC_PRE", "FEV1%FVC_PRE", "FEV1/FVC%", "FEV1%FVC"])
col_ratio_frac    = first_present(meas, ["measured_ratio", "FEV1_FVC", "ratio", "FEV1/FVC"])

meas_use = meas.copy()
meas_use["__measured_fev1__"] = pd.to_numeric(meas_use[col_fev1], errors="coerce") if col_fev1 else np.nan
meas_use["__measured_fvc__"]  = pd.to_numeric(meas_use[col_fvc],  errors="coerce") if col_fvc  else np.nan

if col_ratio_frac:
    meas_use["__measured_ratio__"] = safe_ratio(meas_use[col_ratio_frac])
elif col_ratio_percent:
    meas_use["__measured_ratio__"] = safe_ratio(meas_use[col_ratio_percent])
else:
    if col_fev1 and col_fvc:
        meas_use["__measured_ratio__"] = pd.to_numeric(meas_use[col_fev1], errors="coerce") / pd.to_numeric(meas_use[col_fvc], errors="coerce")
    else:
        meas_use["__measured_ratio__"] = np.nan

# ------------------ TABLE 4.1: Murray vs GLI ------------------
def summarize_method_comparison(x, y, label_x, label_y, metric):
    r, p, n = pearson_and_paired_t(x, y)
    ccc = lin_ccc(x, y)
    x_arr, y_arr = pair_clean(x, y)
    stats_row = {
        "Metric": metric,
        "Comparison": f"{label_y} vs {label_x}",
        f"{label_x} mean": float(np.nanmean(x_arr)) if n else np.nan,
        f"{label_x} sd":   float(np.nanstd(x_arr, ddof=1)) if n > 1 else np.nan,
        f"{label_y} mean": float(np.nanmean(y_arr)) if n else np.nan,
        f"{label_y} sd":   float(np.nanstd(y_arr, ddof=1)) if n > 1 else np.nan,
        "n": n,
        "Pearson r": r,
        "Paired t p": p,
        "CCC": ccc,
        "Mean diff (y-x)": float(np.nanmean(y_arr - x_arr)) if n else np.nan,
        "SD diff": float(np.nanstd(y_arr - x_arr, ddof=1)) if n > 1 else np.nan
    }
    return stats_row

rows_41 = []
pairs_41 = [
    ("murray_fev1", "gli_fev1", "Murray FEV1", "GLI FEV1", "FEV1 (L)"),
    ("murray_fvc",  "gli_fvc",  "Murray FVC",  "GLI FVC",  "FVC (L)"),
    ("murray_ratio","gli_ratio","Murray Ratio","GLI Ratio","FEV1/FVC (ratio)")
]
for xcol, ycol, lx, ly, metric in pairs_41:
    if xcol in val.columns and ycol in val.columns:
        rows_41.append(summarize_method_comparison(val[xcol], val[ycol], lx, ly, metric))

table_41 = pd.DataFrame(rows_41)
table_41 = round_cols(table_41, ["Pearson r", "Paired t p", "CCC", "Mean diff (y-x)", "SD diff"], 3)
table_41.to_csv(TABLE_4_1_OUT, index=False)

# ------------------ TABLE 4.1b: Method vs Measured ------------------
# Choose best join key: Source_ID → Patient_ID → Case → ID
join_keys = [k for k in ["Source_ID", "Patient_ID", "Case", "ID"] if (k in val.columns and k in meas_use.columns)]
vm = None
key_used = None
if join_keys:
    key_used = join_keys[0]
    vm = pd.merge(
        val,
        meas_use[[key_used, "__measured_fev1__", "__measured_fvc__", "__measured_ratio__"]],
        on=key_used,
        how="inner"
    )

rows_41b = []
def add_m_vs_measured(col_method, col_meas, label_method, label_meas, metric):
    if vm is None or (col_method not in vm.columns):
        return
    r, p, n = pearson_and_paired_t(vm[col_method], vm[col_meas])
    ccc = lin_ccc(vm[col_method], vm[col_meas])
    x, y = pair_clean(vm[col_method], vm[col_meas])
    rows_41b.append({
        "Metric": metric,
        "Comparison": f"{label_meas} vs {label_method}",
        "n": n,
        "Pearson r": r,
        "Paired t p": p,
        "CCC": ccc,
        "Mean diff (y-x)": float(np.nanmean(y - x)) if n else np.nan,
        "SD diff": float(np.nanstd(y - x, ddof=1)) if n > 1 else np.nan
    })

# FEV1
add_m_vs_measured("murray_fev1", "__measured_fev1__", "Murray FEV1", "Measured FEV1", "FEV1 (L)")
add_m_vs_measured("gli_fev1",    "__measured_fev1__", "GLI FEV1",    "Measured FEV1", "FEV1 (L)")
# FVC
add_m_vs_measured("murray_fvc",  "__measured_fvc__",  "Murray FVC",  "Measured FVC",  "FVC (L)")
add_m_vs_measured("gli_fvc",     "__measured_fvc__",  "GLI FVC",     "Measured FVC",  "FVC (L)")
# Ratio (fractions)
add_m_vs_measured("murray_ratio","__measured_ratio__","Murray Ratio","Measured Ratio","FEV1/FVC (ratio)")
add_m_vs_measured("gli_ratio",   "__measured_ratio__","GLI Ratio",   "Measured Ratio","FEV1/FVC (ratio)")

table_41b = pd.DataFrame(rows_41b)
table_41b = round_cols(table_41b, ["Pearson r","Paired t p","CCC","Mean diff (y-x)","SD diff"], 3)
# If merge failed, leave a clear note
if vm is None:
    table_41b = pd.DataFrame([{
        "Metric": "NA",
        "Comparison": "Join failed (no common key among Source_ID / Patient_ID / Case / ID)",
        "n": 0
    }])
table_41b.to_csv(TABLE_4_1B_OUT, index=False)

# ------------------ TABLE 4.2: Diagnostic Agreement (robust recompute) ------------------
# Expect diag to have measured_ratio and gli_lln (either fraction or %). We recompute cleanly.
diag_use = diag.copy()

# Build fraction versions
mr_frac = safe_ratio(diag_use.get("measured_ratio"))
gli_lln_frac = safe_ratio(diag_use.get("gli_lln"))

# Recompute diagnoses with FRACTIONS
murray_copd = (mr_frac < 0.70)
gli_copd    = (mr_frac < gli_lln_frac)

diag_use["murray_diagnosis_fixed"] = np.where(murray_copd, "COPD", "NORMAL")
diag_use["GLI_diagnosis_fixed"]    = np.where(gli_copd,    "COPD", "NORMAL")
diag_use["Agreement_fixed"]        = np.where(diag_use["murray_diagnosis_fixed"] == diag_use["GLI_diagnosis_fixed"], "YES", "NO")

# 2×2 cells:
a = ((diag_use["murray_diagnosis_fixed"] == "COPD")   & (diag_use["GLI_diagnosis_fixed"] == "COPD")).sum()
b = ((diag_use["murray_diagnosis_fixed"] == "COPD")   & (diag_use["GLI_diagnosis_fixed"] == "NORMAL")).sum()
c = ((diag_use["murray_diagnosis_fixed"] == "NORMAL") & (diag_use["GLI_diagnosis_fixed"] == "COPD")).sum()
d = ((diag_use["murray_diagnosis_fixed"] == "NORMAL") & (diag_use["GLI_diagnosis_fixed"] == "NORMAL")).sum()

N = len(diag_use)
agree_pct = (diag_use["Agreement_fixed"] == "YES").mean() * 100.0 if N > 0 else np.nan
mcnemar_p = stats.binomtest(k=min(b, c), n=b + c, p=0.5, alternative="two-sided").pvalue if (b + c) > 0 else np.nan

# Cohen’s kappa (safe)
try:
    from sklearn.metrics import cohen_kappa_score
    kappa = cohen_kappa_score(
        diag_use["murray_diagnosis_fixed"],
        diag_use["GLI_diagnosis_fixed"],
        labels=["COPD", "NORMAL"]
    ) if (len(set(diag_use["murray_diagnosis_fixed"])) > 1 or len(set(diag_use["GLI_diagnosis_fixed"])) > 1) else np.nan
except Exception:
    kappa = np.nan

table_42 = pd.DataFrame([{
    "Total N": N,
    "Agreement %": round(agree_pct, 1) if pd.notna(agree_pct) else np.nan,
    "Cohen's kappa": kappa,
    "McNemar p": mcnemar_p,
    "a (MUR+ & GLI+)": a,
    "b (MUR+ & GLI-)": b,
    "c (MUR- & GLI+)": c,
    "d (MUR- & GLI-)": d
}])
table_42 = round_cols(table_42, ["Cohen's kappa", "McNemar p"], 4)
table_42.to_csv(TABLE_4_2_OUT, index=False)

# ------------------ FIGURE 4.1: Scatter Murray vs GLI with annotation ------------------
def scatter_panel(ax, x, y, xlabel, ylabel):
    x_arr, y_arr = pair_clean(x, y)
    if len(x_arr) == 0:
        ax.set_visible(False)
        return
    ax.scatter(x_arr, y_arr, s=16)
    lo = min(np.nanmin(x_arr), np.nanmin(y_arr))
    hi = max(np.nanmax(x_arr), np.nanmax(y_arr))
    ax.plot([lo, hi], [lo, hi], linestyle="--")  # equality line
    r, p, n = pearson_and_paired_t(x_arr, y_arr)
    ccc = lin_ccc(x_arr, y_arr)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    # Annotate inside the axes for readability
    ax.text(0.02, 0.98, f"r={r:.3f}\np={p:.3g}\nCCC={ccc:.3f}\nn={n}", transform=ax.transAxes,
            ha="left", va="top", bbox=dict(boxstyle="round", alpha=0.15))

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
scatter_panel(axes[0], val.get("murray_fev1"),  val.get("gli_fev1"),  "Murray FEV1 (L)", "GLI FEV1 (L)")
scatter_panel(axes[1], val.get("murray_fvc"),   val.get("gli_fvc"),   "Murray FVC (L)",  "GLI FVC (L)")
scatter_panel(axes[2], val.get("murray_ratio"), val.get("gli_ratio"), "Murray FEV1/FVC", "GLI FEV1/FVC")
fig.suptitle("Figure 4.1 — Murray vs GLI (with r, paired t p, and CCC)", y=1.02, fontsize=11)
fig.tight_layout()
fig.savefig(FIGURE_4_1_OUT, dpi=300)
plt.close(fig)

# ------------------ FIGURE 4.2: 2x2 matrix (counts) ------------------
fig2, ax2 = plt.subplots(figsize=(4.8, 4.8))
ax2.axis("off")

# draw a simple grid with text
ax2.text(0.5, 0.95, "Figure 4.2 — Diagnostic Agreement (recomputed)\n"
                    f"κ={kappa if not np.isnan(kappa) else 'NaN'} | McNemar p={mcnemar_p if not np.isnan(mcnemar_p) else 'NaN'}",
         ha="center", va="top")
table_text = [
    ["",           "GLI: COPD",         "GLI: Normal"],
    ["Murray: COPD",   f"{a}",             f"{b}"],
    ["Murray: Normal", f"{c}",             f"{d}"]
]
# render as a small table
the_table = ax2.table(cellText=table_text, loc="center", cellLoc="center")
the_table.scale(1.2, 1.8)
fig2.tight_layout()
fig2.savefig(FIGURE_4_2_OUT, dpi=300)
plt.close(fig2)

print("✅ Done. Generated:")
print(f"- {TABLE_4_1_OUT}")
print(f"- {TABLE_4_1B_OUT}")
print(f"- {TABLE_4_2_OUT}")
print(f"- {FIGURE_4_1_OUT}")
print(f"- {FIGURE_4_2_OUT}")
