import pandas as pd
import numpy as np
import os
from scipy.interpolate import interp1d

# ---------- WORKING DUAL CALCULATOR ----------
BASE_DIR = os.environ.get('DATA_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Data'))
INPUT_FILE = os.path.join(BASE_DIR, "copd_extracted_data_final.xlsx")
FILE_SPIRO_GLI = os.path.join(BASE_DIR, "lookuptables.xlsx")

# ── Pattern classification helpers ───────────────────────────────────────────
# Every obstructive label either interpreter can return contains one of these words:
#   ERS 2022: "Airflow obstruction", "Possible mixed disorder"
#   Murray:   "Obstructive ventilatory defect", "Obstruction with concomitant restriction
#             or air trapping", "Mild obstruction or normal variant"
# If a label is renamed, update these helpers (see also Bug 6: explicit booleans).
OBSTRUCTIVE_KEYWORDS = ('obstruction', 'obstructive', 'mixed')


def is_obstructive_pattern(pattern):
    """True if a spirometry primary_pattern means FEV1/FVC is below the threshold."""
    p = (pattern or '').lower()
    return any(k in p for k in OBSTRUCTIVE_KEYWORDS)


def is_normal_pattern(pattern):
    """True only for a fully normal result ("Normal spirometry"), not "...normal variant"."""
    return (pattern or '').strip().lower().startswith('normal')


def spirometry_obstructed(interp):
    """Obstruction from an interpreter result: explicit flag first, label only as fallback
    (e.g. results saved before flags existed)."""
    flags = (interp or {}).get('flags')
    if flags is not None:
        return bool(flags.get('obstructed'))
    return is_obstructive_pattern((interp or {}).get('primary_pattern'))


def spirometry_normal(interp):
    flags = (interp or {}).get('flags')
    if flags is not None:
        return bool(flags.get('normal'))
    return is_normal_pattern((interp or {}).get('primary_pattern'))


def compare_methods(ers, trad):
    """Single source of truth for ERS 2022 vs Murray agreement (backend and UI)."""
    ers_obs, trad_obs = spirometry_obstructed(ers), spirometry_obstructed(trad)
    ers_norm, trad_norm = spirometry_normal(ers), spirometry_normal(trad)
    both_obstructed = ers_obs and trad_obs
    both_normal = ers_norm and trad_norm
    # Neither normal nor obstructive in both (e.g. restriction / non-specific in both)
    both_other = not (ers_obs or trad_obs or ers_norm or trad_norm)
    return {
        'ers_obstructed': ers_obs, 'traditional_obstructed': trad_obs,
        'ers_normal': ers_norm, 'traditional_normal': trad_norm,
        'both_obstructed': both_obstructed, 'both_normal': both_normal,
        'methods_agree': both_obstructed or both_normal or both_other,
    }


def gli_z_score(measured, M, S, L):
    """Exact GLI 2012 z-score from LMS (Box-Cox) parameters.
    z = ((measured/M)^L - 1) / (L*S);  z = ln(measured/M) / S when L ~ 0.
    Returns None if any input is missing or invalid."""
    try:
        measured, M, S, L = float(measured), float(M), float(S), float(L)
    except (TypeError, ValueError):
        return None
    if any(np.isnan(v) for v in (measured, M, S, L)) or measured <= 0 or M <= 0 or S <= 0:
        return None
    if abs(L) < 1e-4:
        return float(np.log(measured / M) / S)
    return float(((measured / M) ** L - 1) / (L * S))


class WorkingGLI2012Calculator:
    """GLI 2012 Calculator - FIXED RATIO VERSION"""
    
    def __init__(self):
        self.name = "GLI 2012"
        self.spline_data = {}
        
    def load_gli_tables(self):
        """Load GLI 2012 spirometry tables"""
        print(f"📊 Loading {self.name} spirometry tables...")
        
        try:
            xls = pd.ExcelFile(FILE_SPIRO_GLI)
            sheet_map = {
                'FEV1': {'M': 'FEV1 males', 'F': 'FEV1 females'},
                'FVC': {'M': 'FVC males', 'F': 'FVC females'},
                'FEV1_FVC': {'M': 'FEV1FVC males', 'F': 'FEV1FVC females'}
            }
            
            for param, sheets in sheet_map.items():
                self.spline_data[param] = {}
                for sex, sheet in sheets.items():
                    try:
                        df = xls.parse(sheet)
                        
                        # Extract correct columns (1,2,3,4)
                        age_col = df.iloc[1:, 1]      # age
                        lspline_col = df.iloc[1:, 2]  # Lspline  
                        mspline_col = df.iloc[1:, 3]  # Mspline
                        sspline_col = df.iloc[1:, 4]  # Sspline
                        
                        clean_data = pd.DataFrame({
                            'age': age_col,
                            'lspline': lspline_col,
                            'mspline': mspline_col,
                            'sspline': sspline_col
                        })
                        
                        clean_data = clean_data.apply(pd.to_numeric, errors='coerce').dropna()
                        clean_data = clean_data[(clean_data['age'] >= 3) & (clean_data['age'] <= 95)]
                        
                        if len(clean_data) > 0:
                            self.spline_data[param][sex] = clean_data.reset_index(drop=True)
                            print(f"    ✅ {param} {sex}: {len(clean_data)} points")
                            
                    except Exception as e:
                        print(f"    ❌ {param} {sex}: {e}")
            
            return len(self.spline_data) > 0
            
        except Exception as e:
            print(f"    ❌ Error loading GLI file: {e}")
            return False
    
    def get_splines(self, param, sex, age):
        """Get spline values for parameter"""
        try:
            df = self.spline_data[param][sex]
            Mspline = interp1d(df['age'], df['mspline'], fill_value="extrapolate")(age)
            Sspline = interp1d(df['age'], df['sspline'], fill_value="extrapolate")(age)
            Lspline = interp1d(df['age'], df['lspline'], fill_value="extrapolate")(age)
            return float(Mspline), float(Sspline), float(Lspline)
        except:
            return np.nan, np.nan, np.nan
    
    def calculate_fev1(self, age, sex, height):
        """Calculate GLI FEV1"""
        try:
            Mspline, Sspline, Lspline = self.get_splines('FEV1', sex, age)
            if np.isnan(Mspline):
                return np.nan, np.nan, np.nan, np.nan, np.nan
            
            # GLI 2012 FEV1 coefficients
            if sex == 'M':
                a0, a1, a2 = -10.3420, 2.2196, 0.0574
                p0, p1 = -2.3268, 0.0798
                q0, q1 = 0.8866, 0.0850
            else:
                a0, a1, a2 = -9.6987, 2.1211, -0.0270
                p0, p1 = -2.3765, 0.0972
                q0, q1 = 1.1540, 0.0
            
            ln_height = np.log(height)
            ln_age = np.log(age)
            
            # Calculate predicted
            ln_M = a0 + a1 * ln_height + a2 * ln_age + Mspline
            predicted = np.exp(ln_M)
            
            # Calculate LLN
            ln_S = p0 + p1 * ln_age + Sspline
            S = np.exp(ln_S)
            L = q0 + q1 * ln_age + Lspline
            
            if abs(L) > 0.01:
                term = 1 - 1.645 * L * S
                LLN = predicted * (term ** (1/L)) if term > 0 else predicted * np.exp(-1.645 * S)
            else:
                LLN = predicted * np.exp(-1.645 * S)
            
            return predicted, LLN, predicted, S, L   # M = predicted (median)
            
        except Exception as e:
            print(f"    ❌ GLI FEV1 error: {e}")
            return np.nan, np.nan, np.nan, np.nan, np.nan
    
    def calculate_fvc(self, age, sex, height):
        """Calculate GLI FVC"""
        try:
            Mspline, Sspline, Lspline = self.get_splines('FVC', sex, age)
            if np.isnan(Mspline):
                return np.nan, np.nan, np.nan, np.nan, np.nan
            
            # GLI 2012 FVC coefficients
            if sex == 'M':
                a0, a1, a2 = -11.2281, 2.3670, 0.0800
                p0, p1 = -2.2963, 0.0633
                q0, q1 = 0.9481, 0.0
            else:
                a0, a1, a2 = -10.4030, 2.2831, 0.0378
                p0, p1 = -2.3549, 0.0956
                q0, q1 = 0.8236, 0.0
            
            ln_height = np.log(height)
            ln_age = np.log(age)
            
            # Calculate predicted
            ln_M = a0 + a1 * ln_height + a2 * ln_age + Mspline
            predicted = np.exp(ln_M)
            
            # Calculate LLN
            ln_S = p0 + p1 * ln_age + Sspline
            S = np.exp(ln_S)
            L = q0 + q1 * ln_age + Lspline
            
            if abs(L) > 0.01:
                term = 1 - 1.645 * L * S
                LLN = predicted * (term ** (1/L)) if term > 0 else predicted * np.exp(-1.645 * S)
            else:
                LLN = predicted * np.exp(-1.645 * S)
            
            return predicted, LLN, predicted, S, L   # M = predicted (median)
            
        except Exception as e:
            print(f"    ❌ GLI FVC error: {e}")
            return np.nan, np.nan, np.nan, np.nan, np.nan
    
    def calculate_ratio(self, age, sex, height):
        """Calculate GLI 2012 FEV1/FVC ratio using correct log-normal LMS framework"""
        try:
            Mspline, Sspline, Lspline = self.get_splines('FEV1_FVC', sex, age)
            if np.isnan(Mspline):
                return np.nan, np.nan, np.nan, np.nan, np.nan

            # GLI 2012 FEV1/FVC coefficients (from lookuptables.xlsx FEV1FVC sheets)
            if sex == 'M':
                a0, a1, a2 = 0.7403, -0.1595, -0.0366
                p0, p1 = -2.9595, 0.1156
                q0, q1 = 4.7101, -0.6774
            else:
                a0, a1, a2 = 0.550559, -0.107805, -0.054419
                p0, p1 = -3.23948, 0.18503
                q0, q1 = 7.032, -1.197

            ln_age = np.log(age)
            ln_height = np.log(height)

            # Predicted (median)
            ln_M = a0 + a1 * ln_height + a2 * ln_age + Mspline
            M = np.exp(ln_M)                          # unclamped median, used for z-scores
            predicted = max(0.30, min(0.95, M))       # NOTE: clamp reviewed in Bug 7

            # LLN using Box-Cox framework
            ln_S = p0 + p1 * ln_age + Sspline
            S = np.exp(ln_S)
            L = q0 + q1 * ln_age + Lspline

            if abs(L) > 0.01:
                term = 1 - 1.645 * L * S
                LLN = predicted * (term ** (1/L)) if term > 0 else predicted * np.exp(-1.645 * S)
            else:
                LLN = predicted * np.exp(-1.645 * S)

            LLN = max(0.20, LLN)

            print(f"    GLI ratio {sex}: ln_M={ln_M:.4f} -> predicted={predicted:.4f}, LLN={LLN:.4f}")

            return predicted, LLN, M, S, L

        except Exception as e:
            print(f"    ❌ GLI ratio error: {e}")
            return np.nan, np.nan, np.nan, np.nan, np.nan
    
    def calculate_patient(self, age, sex, height):
        """Calculate all GLI parameters for patient"""
        results = {}
        
        for prefix, fn in (('FEV1', self.calculate_fev1),
                           ('FVC', self.calculate_fvc),
                           ('FEV1_FVC', self.calculate_ratio)):
            pred, lln, M, S, L = fn(age, sex, height)
            results[f'{prefix}_GLI_pred'] = pred
            results[f'{prefix}_GLI_LLN'] = lln
            results[f'{prefix}_GLI_M'] = M      # LMS parameters, needed for exact z-scores
            results[f'{prefix}_GLI_S'] = S
            results[f'{prefix}_GLI_L'] = L
        
        return results

class MurrayCalculator:
    """Murray Traditional Calculator"""
    
    def __init__(self):
        self.name = "Murray (Traditional)"
        
    def calculate_patient(self, age, sex, height):
        """Calculate Murray parameters"""
        results = {}
        
        try:
            age = float(age)
            height = float(height)
            
            if sex == 'M':
                fev1_pred = 0.0414 * height - 0.0244 * age - 2.190
                fvc_pred = 0.0600 * height - 0.0214 * age - 4.650
            else:
                fev1_pred = 0.0342 * height - 0.0255 * age - 1.578
                fvc_pred = 0.0491 * height - 0.0216 * age - 3.590
            
            fev1_pred = max(0.5, fev1_pred)
            fvc_pred = max(0.5, fvc_pred)
            
            results['FEV1_Murray_pred'] = fev1_pred
            results['FVC_Murray_pred'] = fvc_pred

            # Traditional LLN = 80% of predicted (project report §3.4.1; Murray Table 32.3
            # defines "abnormal" as < LLN without a numeric rule).
            results['FEV1_Murray_LLN'] = 0.80 * fev1_pred
            results['FVC_Murray_LLN'] = 0.80 * fvc_pred
            
            if fev1_pred > 0 and fvc_pred > 0:
                ratio = fev1_pred / fvc_pred
                results['FEV1_FVC_Murray_pred'] = ratio
                results['FEV1_FVC_Murray_LLN'] = 0.70
            
        except Exception as e:
            print(f"    ❌ Murray error: {e}")
            
        return results

def parse_pred_pre_percent(raw):
    """Parse a raw extractor string the same way save_data.expand_pred_pre_percent does.
    3 values: "pred pre %pred"      4 values: "pred LLN pre %pred"
    Returns dict with keys pred, lln, pre, pct (None when absent)."""
    out = {'pred': None, 'lln': None, 'pre': None, 'pct': None}
    if raw in (None, "", "None"):
        return out
    vals = str(raw).split()
    if len(vals) == 3:
        out['pred'], out['pre'], out['pct'] = vals
    elif len(vals) == 4:
        out['pred'], out['lln'], out['pre'], out['pct'] = vals
    return out


class ClinicalInterpreter:
    """Clinical interpretation following ERS 2022 and Traditional methods"""
    
    def __init__(self):
        self.name = "Clinical Interpreter"
    
    def interpret_ers2022_algorithm(self, measured_values, gli_results):
        """
        ERS 2022 Figure 8 & 10 Algorithm Implementation
        Uses GLI predictions with 5th percentile LLN
        """
        interpretation = {
            'method': 'ERS 2022 Standards',
            'primary_pattern': 'Unknown',
            'secondary_findings': [],
            'severity': 'Unknown',
            'clinical_notes': [],
            'flags': None,   # set once the pattern is decided; None = not interpretable
        }
        
        try:
            # Extract measured values
            fev1_measured = measured_values.get('FEV1_PRE', 0)
            fvc_measured = measured_values.get('FVC_PRE', 0) 
            ratio_measured = measured_values.get('FEV 1 % FVC_PRE', 0)
            
            # Extract GLI predictions and LLNs
            fev1_pred = gli_results.get('FEV1_GLI_pred', 0)
            fev1_lln = gli_results.get('FEV1_GLI_LLN', 0)
            fvc_pred = gli_results.get('FVC_GLI_pred', 0)
            fvc_lln = gli_results.get('FVC_GLI_LLN', 0)
            ratio_pred = gli_results.get('FEV1_FVC_GLI_pred', 0)
            ratio_lln = gli_results.get('FEV1_FVC_GLI_LLN', 0)

            def _z(prefix, measured):
                return gli_z_score(measured, gli_results.get(f'{prefix}_GLI_M'),
                                   gli_results.get(f'{prefix}_GLI_S'), gli_results.get(f'{prefix}_GLI_L'))
            
            # Convert ratio if given as percentage
            if ratio_measured > 1:
                ratio_measured = ratio_measured / 100

            # Fallback: compute ratio from components when OCR misses the [%] unit bracket
            if ratio_measured == 0 and fev1_measured > 0 and fvc_measured > 0:
                ratio_measured = fev1_measured / fvc_measured
                print(f"🔧 Computed FEV1/FVC ratio from components: {ratio_measured:.3f}")

            if not all([fev1_measured, fvc_measured, ratio_measured]):
                interpretation['clinical_notes'].append("Insufficient measured values for interpretation")
                return interpretation

            # Exact GLI LMS z-scores (None if LMS parameters are unavailable)
            fev1_z = _z('FEV1', fev1_measured)
            fvc_z = _z('FVC', fvc_measured)
            ratio_z = _z('FEV1_FVC', ratio_measured)
            if ratio_z is not None:
                interpretation['fev1_fvc_z_score'] = round(ratio_z, 2)

            # ERS 2022 Figure 8 Algorithm - Spirometry Interpretation
            print(f"🔍 ERS 2022 Algorithm:")
            print(f"   Ratio: {ratio_measured:.3f} vs LLN: {ratio_lln:.3f}")
            print(f"   FVC: {fvc_measured:.3f} vs LLN: {fvc_lln:.3f}")
            
            # Step 1: Check FEV1/FVC ratio
            if ratio_measured >= ratio_lln:  # >5th percentile
                print(f"   ✅ Normal FEV1/FVC ratio")
                
                # Step 2: Check FVC
                if fvc_measured >= fvc_lln:  # >5th percentile
                    interpretation['primary_pattern'] = 'Normal spirometry'
                    interpretation['severity'] = 'Normal'
                    interpretation['clinical_notes'].append("All spirometric values within normal limits")
                else:
                    interpretation['primary_pattern'] = 'Possible restriction or non-specific pattern'
                    interpretation['clinical_notes'].append("Low FVC with normal FEV1/FVC - consider lung volumes")
                    interpretation['secondary_findings'].append("TLC measurement recommended")
                    if fvc_z is not None:
                        fvc_z_score = fvc_z
                        interpretation['fvc_z_score'] = round(fvc_z_score, 2)
                        if fvc_z_score >= -1.645:
                            fvc_severity = 'Borderline'
                        elif fvc_z_score >= -2.5:
                            fvc_severity = 'Mild'
                        elif fvc_z_score >= -4.0:
                            fvc_severity = 'Moderate'
                        else:
                            fvc_severity = 'Severe'
                        interpretation['severity'] = fvc_severity
                        interpretation['clinical_notes'].append(f"FVC z-score: {fvc_z_score:.2f} ({fvc_severity} restriction)")
                    else:
                        interpretation['severity'] = 'Mild'
                    
            else:  # FEV1/FVC < LLN = Obstruction present
                print(f"   ⚠️ Obstruction detected")
                
                # Step 3: Check FVC to determine if mixed disorder
                if fvc_measured >= fvc_lln:
                    interpretation['primary_pattern'] = 'Airflow obstruction'
                    interpretation['clinical_notes'].append("Pure obstructive pattern")
                else:
                    interpretation['primary_pattern'] = 'Possible mixed disorder'
                    interpretation['clinical_notes'].append("Obstruction with possible restriction")
                    interpretation['secondary_findings'].append("Lung volumes needed to confirm mixed pattern")
                    if fvc_z is not None:
                        interpretation['fvc_z_score'] = round(fvc_z, 2)
                        interpretation['clinical_notes'].append(f"FVC z-score: {fvc_z:.2f}")
                
                # Determine obstruction severity using FEV1 z-score
                if fev1_z is None:
                    interpretation['clinical_notes'].append("FEV1 z-score unavailable (GLI LMS parameters missing)")
                else:
                    fev1_z_score = fev1_z
                    interpretation['fev1_z_score'] = round(fev1_z_score, 2)
                    
                    if fev1_z_score >= -2.5:
                        interpretation['severity'] = 'Mild'
                    elif fev1_z_score >= -4.0:
                        interpretation['severity'] = 'Moderate' 
                    else:
                        interpretation['severity'] = 'Severe'
                    
                    interpretation['clinical_notes'].append(f"FEV1 z-score: {fev1_z_score:.2f}")

            # Explicit flags — the same comparisons that chose the pattern above.
            # ERS 2022 Fig. 8 does not use FEV1 for the pattern, so "normal" = ratio and FVC normal.
            ers_obstructed = ratio_measured < ratio_lln
            ers_low_fvc = fvc_measured < fvc_lln
            interpretation['flags'] = {
                'obstructed': bool(ers_obstructed),
                'low_fvc': bool(ers_low_fvc),
                'low_fev1': bool(fev1_lln > 0 and fev1_measured < fev1_lln),
                'normal': bool(not ers_obstructed and not ers_low_fvc),
            }
            
            # Add percentage predicted for reference
            if fev1_pred > 0 and fvc_pred > 0:
                fev1_percent = (fev1_measured / fev1_pred) * 100
                fvc_percent = (fvc_measured / fvc_pred) * 100
                interpretation['fev1_percent_predicted'] = fev1_percent
                interpretation['fvc_percent_predicted'] = fvc_percent
                interpretation['clinical_notes'].append(f"FEV1: {fev1_percent:.0f}% predicted, FVC: {fvc_percent:.0f}% predicted")
            
        except Exception as e:
            interpretation['clinical_notes'].append(f"Error in ERS 2022 interpretation: {str(e)}")
        
        return interpretation
    
    def interpret_traditional_murray(self, measured_values, murray_results):
        """
        Murray Algorithm — full flowchart (Murray_2 / Table 32.3)
        Uses fixed FEV1/FVC < 0.70 and Murray LLN (80% predicted) thresholds.
        Severity grading follows Murray Table 32.3 (not GOLD 1-4).
        """
        interpretation = {
            'method': 'Traditional (Murray)',
            'primary_pattern': 'Unknown',
            'secondary_findings': [],
            'severity': 'Unknown',
            'clinical_notes': [],
            'flags': None,   # set once the pattern is decided; None = not interpretable
        }

        try:
            # Extract measured values
            fev1_measured = measured_values.get('FEV1_PRE', 0)
            fvc_measured = measured_values.get('FVC_PRE', 0)
            ratio_measured = measured_values.get('FEV 1 % FVC_PRE', 0)

            # Extract Murray predictions and LLNs
            fev1_pred = murray_results.get('FEV1_Murray_pred', 0)
            fvc_pred  = murray_results.get('FVC_Murray_pred', 0)
            fev1_lln  = murray_results.get('FEV1_Murray_LLN', 0)  # 80% of pred
            fvc_lln   = murray_results.get('FVC_Murray_LLN', 0)   # 80% of pred

            # Convert ratio if given as percentage
            if ratio_measured > 1:
                ratio_measured = ratio_measured / 100

            # Fallback: compute ratio from components when OCR misses the [%] unit bracket
            if ratio_measured == 0 and fev1_measured > 0 and fvc_measured > 0:
                ratio_measured = fev1_measured / fvc_measured
                print(f"🔧 Computed FEV1/FVC ratio from components: {ratio_measured:.3f}")

            if not all([fev1_measured, fvc_measured, ratio_measured]):
                interpretation['clinical_notes'].append("Insufficient measured values for interpretation")
                return interpretation

            # Derived flags
            fev1_low = fev1_lln > 0 and fev1_measured < fev1_lln
            fvc_low  = fvc_lln  > 0 and fvc_measured  < fvc_lln

            fev1_percent = (fev1_measured / fev1_pred * 100) if fev1_pred > 0 else None
            fvc_percent  = (fvc_measured  / fvc_pred  * 100) if fvc_pred  > 0 else None

            if fev1_percent is not None:
                interpretation['fev1_percent_predicted'] = fev1_percent
            if fvc_percent is not None:
                interpretation['fvc_percent_predicted'] = fvc_percent

            print(f"🔍 Murray Algorithm:")
            print(f"   Ratio: {ratio_measured:.3f} vs 0.70 | FEV1 low: {fev1_low} | FVC low: {fvc_low}")

            # ── Murray_2 flowchart ─────────────────────────────────────────────
            if ratio_measured < 0.70:
                # Obstruction branch
                if fev1_low:
                    if not fvc_low:
                        # Low ratio + low FEV1 + normal FVC → Obstructive VD
                        interpretation['primary_pattern'] = 'Obstructive ventilatory defect'
                        interpretation['clinical_notes'].append("FEV1/FVC < 0.70 with low FEV1 and normal FVC")
                        interpretation['secondary_findings'].append(
                            "DLCO recommended — Low: suggests emphysema; Normal: suggests airway disease")
                    else:
                        # Low ratio + low FEV1 + low FVC → obstruction with restriction/air trapping
                        interpretation['primary_pattern'] = 'Obstruction with concomitant restriction or air trapping'
                        interpretation['clinical_notes'].append("Low FEV1/FVC, low FEV1, and low FVC")
                        interpretation['secondary_findings'].append(
                            "TLC recommended — Normal TLC: obstructive VD; Low TLC: mixed obstructive and restrictive defect")
                else:
                    # Low ratio + normal FEV1
                    if not fvc_low:
                        interpretation['primary_pattern'] = 'Mild obstruction or normal variant'
                        interpretation['clinical_notes'].append("Low FEV1/FVC with normal FEV1 and FVC — may be a normal variant")
                    else:
                        # Murray_2: normal FEV1 + low FVC joins the same box as low FEV1 + low FVC
                        interpretation['primary_pattern'] = 'Obstruction with concomitant restriction or air trapping'
                        interpretation['clinical_notes'].append("Low FEV1/FVC with low FVC despite normal FEV1")
                        interpretation['secondary_findings'].append(
                            "TLC recommended — Normal TLC: obstructive VD; Low TLC: mixed obstructive and restrictive defect")

                # Murray Table 32.3 severity (applied when obstruction is confirmed)
                if fev1_percent is not None and interpretation['primary_pattern'] != 'Mild obstruction or normal variant':
                    if fev1_percent >= 70:
                        interpretation['severity'] = 'Mild'
                    elif fev1_percent >= 60:
                        interpretation['severity'] = 'Moderate'
                    elif fev1_percent >= 50:
                        interpretation['severity'] = 'Moderately severe'
                    elif fev1_percent >= 35:
                        interpretation['severity'] = 'Severe'
                    else:
                        interpretation['severity'] = 'Very severe'

                    interpretation['clinical_notes'].append(
                        f"FEV1: {fev1_percent:.0f}% predicted (Murray severity grading)")

            else:
                # No obstruction branch (ratio ≥ 0.70)
                if fvc_low:
                    # Low FVC → suggestive of restriction
                    interpretation['primary_pattern'] = 'Suggestive of restrictive ventilatory defect'
                    interpretation['clinical_notes'].append("Normal FEV1/FVC with low FVC suggests restriction")
                    interpretation['secondary_findings'].append(
                        "TLC recommended — Low TLC: restrictive VD (DLCO: Low → ILD; Normal → chest wall/neuromuscular); "
                        "Normal TLC: non-specific VD")
                elif fev1_low:
                    # Normal FVC, low FEV1, no obstruction → non-specific VD
                    interpretation['primary_pattern'] = 'Non-specific ventilatory defect'
                    interpretation['clinical_notes'].append("Normal FEV1/FVC, normal FVC, but low FEV1")
                    interpretation['secondary_findings'].append(
                        "DLCO recommended — Low: pulmonary vascular disease or mild parenchymal disease; Normal: may be normal variant")
                else:
                    interpretation['primary_pattern'] = 'Normal spirometry'
                    interpretation['severity'] = 'Normal'
                    interpretation['clinical_notes'].append("FEV1/FVC ≥ 0.70, FEV1 and FVC within normal limits")

                if fev1_percent is not None and fvc_percent is not None:
                    interpretation['clinical_notes'].append(
                        f"FEV1: {fev1_percent:.0f}% predicted, FVC: {fvc_percent:.0f}% predicted")

            # Explicit flags — the same comparisons that chose the pattern above
            murray_obstructed = ratio_measured < 0.70
            interpretation['flags'] = {
                'obstructed': bool(murray_obstructed),
                'low_fvc': bool(fvc_low),
                'low_fev1': bool(fev1_low),
                'normal': bool(not murray_obstructed and not fvc_low and not fev1_low),
            }

        except Exception as e:
            interpretation['clinical_notes'].append(f"Error in Murray interpretation: {str(e)}")

        return interpretation

    def interpret_complete_pft(self, extracted_data, murray_results=None, gli_results=None):
        """
        Complete PFT interpretation including lung volumes and gas transfer
        Uses ALL extracted values from PDF
        """
        interpretation = {
            'spirometry': None,
            'lung_volumes': None,
            'gas_transfer': None,
            'summary': None
        }
        
        try:
            measured_spirometry = {}
            for k in ['FEV1_PRE', 'FVC_PRE', 'FEV 1 % FVC_PRE']:
                v = extracted_data.get(k)
                try:
                    measured_spirometry[k] = float(v) if v not in (None, "", "None") else 0.0
                except (ValueError, TypeError):
                    measured_spirometry[k] = 0.0

            # Use existing spirometry interpretation
            if gli_results:
                interpretation['spirometry'] = self.interpret_ers2022_algorithm(measured_spirometry, gli_results)
            elif murray_results:
                interpretation['spirometry'] = self.interpret_traditional_murray(measured_spirometry, murray_results)

            # Derive obstruction flag from spirometry result for lung volumes flowchart
            is_obstructed = spirometry_obstructed(interpretation.get('spirometry'))

            # Interpret lung volumes (RV, TLC) — pass obstruction status for Mixed disorder detection
            interpretation['lung_volumes'] = self.interpret_lung_volumes(extracted_data, is_obstructed)
            
            # Interpret gas transfer (DLCO/TLCO, KCO)
            interpretation['gas_transfer'] = self.interpret_gas_transfer(extracted_data)
            
            # Generate summary interpretation
            interpretation['summary'] = self.generate_summary_interpretation(interpretation)
            
        except Exception as e:
            interpretation['error'] = f"Error in complete interpretation: {str(e)}"
        
        return interpretation
    
    def interpret_lung_volumes(self, extracted_data, is_obstructed=False):
        """
        Interpret lung volume patterns following the ERS 2022 lung volumes flowchart.
        Thresholds: TLC <80% ≈ <5th percentile (restriction); >120% ≈ >95th (hyperinflation).
        RV/TLC >120% ≈ >95th percentile (air trapping).
        is_obstructed: True if FEV1/FVC is below LLN (used to detect Mixed disorder).
        """
        volume_interpretation = {
            'pattern': 'Unknown',
            'findings': [],
            'values': {}
        }
        try:
            # Prefer expanded keys created by save_data.py (*_PRE_PERCENT and *_PRE)
            rv_percent     = extracted_data.get("RV_PRE_PERCENT")
            tlc_percent    = extracted_data.get("TLC_PRE_PERCENT")
            rv_tlc_percent = extracted_data.get("RV % TLC_PRE_PERCENT")

            rv_meas     = extracted_data.get("RV_PRE")
            tlc_meas    = extracted_data.get("TLC_PRE")
            rv_tlc_meas = extracted_data.get("RV % TLC_PRE")

            # Fallback to raw strings (only if expanded keys are missing).
            # Real extractor layout: "pred pre %pred" or "pred LLN pre %pred".
            raw = {k: parse_pred_pre_percent(extracted_data.get(k)) for k in ("RV", "TLC", "RV % TLC")}
            if rv_percent is None:     rv_percent = raw["RV"]['pct']
            if rv_meas is None:        rv_meas = raw["RV"]['pre']
            if tlc_percent is None:    tlc_percent = raw["TLC"]['pct']
            if tlc_meas is None:       tlc_meas = raw["TLC"]['pre']
            if rv_tlc_percent is None: rv_tlc_percent = raw["RV % TLC"]['pct']
            if rv_tlc_meas is None:    rv_tlc_meas = raw["RV % TLC"]['pre']

            # Convert to float and store
            if rv_percent is not None:
                rv_percent = float(rv_percent)
                volume_interpretation["values"]["RV_%pred"] = rv_percent
            if rv_meas is not None:
                volume_interpretation["values"]["RV_meas"] = float(rv_meas)

            if tlc_percent is not None:
                tlc_percent = float(tlc_percent)
                volume_interpretation["values"]["TLC_%pred"] = tlc_percent
            if tlc_meas is not None:
                volume_interpretation["values"]["TLC_meas"] = float(tlc_meas)

            if rv_tlc_percent is not None:
                rv_tlc_percent = float(rv_tlc_percent)
                volume_interpretation["values"]["RV/TLC_%pred"] = rv_tlc_percent
            if rv_tlc_meas is not None:
                volume_interpretation["values"]["RV/TLC_meas"] = float(rv_tlc_meas)

            # ── Lung volumes flowchart (ERS 2022) ────────────────────────────
            # Prefer machine LLN values when available; fall back to 80%/120% approximation
            tlc_lln_val    = extracted_data.get('TLC_LLN') or raw["TLC"]['lln']
            rv_tlc_lln_val = extracted_data.get('RV % TLC_LLN') or raw["RV % TLC"]['lln']

            if tlc_meas is not None and tlc_lln_val is not None:
                try:
                    tlc_low = float(tlc_meas) < float(tlc_lln_val)
                except (ValueError, TypeError):
                    tlc_low = tlc_percent is not None and tlc_percent < 80
            else:
                tlc_low = tlc_percent is not None and tlc_percent < 80

            # High TLC (hyperinflation) = TLC above the ULN — same rule as RV/TLC below.
            # ULN ≈ pred + (pred - LLN)  (APPROXIMATION: assumes a symmetric distribution;
            # reports print no ULN). Without pred/LLN (e.g. NEW formats), fall back to %pred > 120.
            tlc_pred_val = extracted_data.get('TLC_PRED') or raw["TLC"]['pred']
            tlc_high = None
            if tlc_meas is not None and tlc_lln_val is not None and tlc_pred_val is not None:
                try:
                    tpred_, tlln_ = float(tlc_pred_val), float(tlc_lln_val)
                    if tlln_ < tpred_:
                        tlc_high = float(tlc_meas) > tpred_ + (tpred_ - tlln_)
                except (ValueError, TypeError):
                    pass
            if tlc_high is None:
                tlc_high = tlc_percent is not None and tlc_percent > 120

            # Air trapping = RV/TLC above the upper limit of normal (ULN).
            # Reports print no ULN, so it is ESTIMATED by mirroring the printed LLN around
            # the predicted value:  ULN ≈ pred + (pred - LLN)   (APPROXIMATION: assumes a
            # symmetric distribution). Without pred/LLN, fall back to %pred > 120.
            # (Previously LLN * 1.3, which is ~= the predicted value and flagged almost everyone.)
            rv_tlc_pred_val = extracted_data.get('RV % TLC_PRED') or raw["RV % TLC"]['pred']
            air_trap = None
            if rv_tlc_meas is not None and rv_tlc_lln_val is not None and rv_tlc_pred_val is not None:
                try:
                    pred_, lln_ = float(rv_tlc_pred_val), float(rv_tlc_lln_val)
                    if lln_ < pred_:
                        air_trap = float(rv_tlc_meas) > pred_ + (pred_ - lln_)
                except (ValueError, TypeError):
                    pass
            if air_trap is None:
                air_trap = rv_tlc_percent is not None and rv_tlc_percent > 120

            if tlc_low:
                # Restriction present
                if air_trap:
                    if is_obstructed:
                        volume_interpretation["pattern"] = "Mixed disorder"
                        volume_interpretation["findings"].append(
                            "Restriction (low TLC) + air trapping + obstruction = Mixed obstructive-restrictive disorder")
                    else:
                        volume_interpretation["pattern"] = "Complex restriction"
                        volume_interpretation["findings"].append(
                            "Restriction with air trapping (RV/TLC elevated) — complex restriction")
                else:
                    volume_interpretation["pattern"] = "Simple restriction"
                    volume_interpretation["findings"].append(
                        "Reduced TLC without air trapping — simple restriction")

            elif tlc_high:
                # Possible hyperinflation
                if air_trap:
                    volume_interpretation["pattern"] = "Hyperinflation"
                    volume_interpretation["findings"].append(
                        "Elevated TLC and RV/TLC — hyperinflation")
                else:
                    volume_interpretation["pattern"] = "Large lungs"
                    volume_interpretation["findings"].append(
                        "Elevated TLC without proportional air trapping — large lungs (constitutional)")

            elif air_trap:
                # Normal TLC but elevated RV/TLC
                volume_interpretation["pattern"] = "Hyperinflation"
                volume_interpretation["findings"].append(
                    "Air trapping (elevated RV/TLC) with normal TLC — hyperinflation")

            else:
                volume_interpretation["pattern"] = "Normal lung volumes"

            volume_interpretation["flags"] = {
                'tlc_low': bool(tlc_low),
                'tlc_high': bool(tlc_high),
                'air_trapping': bool(air_trap),
                'tlc_known': tlc_meas is not None or tlc_percent is not None,
            }

            # Add quantitative notes
            if tlc_percent is not None:
                volume_interpretation["findings"].append(f"TLC: {tlc_percent:.0f}% predicted")
            if rv_percent is not None:
                volume_interpretation["findings"].append(f"RV: {rv_percent:.0f}% predicted")
            if rv_tlc_percent is not None:
                volume_interpretation["findings"].append(f"RV/TLC: {rv_tlc_percent:.0f}% predicted")

        except Exception as e:
            volume_interpretation["error"] = f"Error interpreting lung volumes: {str(e)}"

        return volume_interpretation
    
    def interpret_bd_response(self, extracted_data, fev1_pred=None, fvc_pred=None):
        """
        ERS 2022 bronchodilator reversibility criteria:
        Significant = FEV1 or FVC increase ≥150 mL AND ≥10% of predicted value.
        """
        bd = {
            'has_post_bd': False,
            'fev1': {'pre': None, 'post': None, 'delta_l': None, 'delta_pct_pred': None, 'significant': False},
            'fvc':  {'pre': None, 'post': None, 'delta_l': None, 'delta_pct_pred': None, 'significant': False},
            'overall_significant': False,
            'interpretation': 'Post-BD data not available'
        }
        try:
            # Try expanded keys first (*_PRE / *_POST created by save_data.py)
            fev1_pre  = extracted_data.get('FEV1_PRE')
            fev1_post = extracted_data.get('FEV1_POST')
            fvc_pre   = extracted_data.get('FVC_PRE')
            fvc_post  = extracted_data.get('FVC_POST')

            # Fallback to raw string (layouts from save_data.expand_full_numeric_row):
            #   5 vals: pred pre pct_pre post pct_post              → pre [1], post [3]
            #   6 vals: pred pre pct_pre post pct_post dchange      → pre [1], post [3]
            #   7 vals: pred LLN pre pct_pre post pct_post dchange  → pre [2], post [4]
            def _extract_pre_post(raw_str):
                vals = str(raw_str).split()
                try:
                    if len(vals) == 7:
                        return float(vals[2]), float(vals[4])
                    if len(vals) in (5, 6):
                        return float(vals[1]), float(vals[3])
                except (ValueError, IndexError):
                    pass
                return None, None

            if (fev1_pre is None or fev1_post is None) and extracted_data.get('FEV1'):
                p, po = _extract_pre_post(extracted_data['FEV1'])
                fev1_pre  = fev1_pre  if fev1_pre  is not None else p
                fev1_post = fev1_post if fev1_post is not None else po

            if (fvc_pre is None or fvc_post is None) and extracted_data.get('FVC'):
                p, po = _extract_pre_post(extracted_data['FVC'])
                fvc_pre  = fvc_pre  if fvc_pre  is not None else p
                fvc_post = fvc_post if fvc_post is not None else po

            # Convert to float
            def _f(v): return float(v) if v is not None else None
            fev1_pre, fev1_post = _f(fev1_pre), _f(fev1_post)
            fvc_pre,  fvc_post  = _f(fvc_pre),  _f(fvc_post)

            if fev1_post is None and fvc_post is None:
                return bd  # No post-BD data available

            bd['has_post_bd'] = True

            # FEV1 response
            if fev1_pre is not None and fev1_post is not None:
                delta = fev1_post - fev1_pre
                bd['fev1']['pre']     = round(fev1_pre, 2)
                bd['fev1']['post']    = round(fev1_post, 2)
                bd['fev1']['delta_l'] = round(delta, 3)
                if fev1_pred and fev1_pred > 0:
                    pct = (delta / fev1_pred) * 100
                    bd['fev1']['delta_pct_pred'] = round(pct, 1)
                    bd['fev1']['significant'] = (delta >= 0.150 and pct >= 10.0)

            # FVC response
            if fvc_pre is not None and fvc_post is not None:
                delta = fvc_post - fvc_pre
                bd['fvc']['pre']     = round(fvc_pre, 2)
                bd['fvc']['post']    = round(fvc_post, 2)
                bd['fvc']['delta_l'] = round(delta, 3)
                if fvc_pred and fvc_pred > 0:
                    pct = (delta / fvc_pred) * 100
                    bd['fvc']['delta_pct_pred'] = round(pct, 1)
                    bd['fvc']['significant'] = (delta >= 0.150 and pct >= 10.0)

            bd['overall_significant'] = bd['fev1']['significant'] or bd['fvc']['significant']

            if bd['overall_significant']:
                parts = []
                if bd['fev1']['significant']:
                    parts.append(f"FEV1 +{bd['fev1']['delta_l']*1000:.0f} mL ({bd['fev1']['delta_pct_pred']:.1f}% pred)")
                if bd['fvc']['significant']:
                    parts.append(f"FVC +{bd['fvc']['delta_l']*1000:.0f} mL ({bd['fvc']['delta_pct_pred']:.1f}% pred)")
                bd['interpretation'] = (
                    f"Significant BD response: {', '.join(parts)} — "
                    "suggests reversible airflow obstruction (consider asthma or asthma-COPD overlap)"
                )
            else:
                bd['interpretation'] = (
                    "No significant BD response (ERS 2022 threshold: ≥150 mL AND ≥10% predicted) — "
                    "consistent with fixed, irreversible obstruction"
                )

        except Exception as e:
            bd['error'] = f"Error interpreting BD response: {str(e)}"

        return bd

    def interpret_gas_transfer(self, extracted_data):
        """Interpret gas transfer/diffusion capacity from extracted PDF data"""
        gas_interpretation = {
            'pattern': 'Unknown',
            'findings': [],
            'values': {}
        }
        
        try:             # Prefer expanded percent-predicted keys
            # OLD format: "DLCOc SB" / "DLCOc/V"; NEW format: "DLCOc" / "DLCOc/VA"
            def _first(*keys):
                for k in keys:
                    v = extracted_data.get(k)
                    if v not in (None, "", "None"):
                        return v
                return None

            dlco_percent = _first("DLCOc SB_PRE_PERCENT", "DLCOc_PRE_PERCENT", "DLCO SB_PRE_PERCENT")
            kco_percent  = _first("DLCOc/V_PRE_PERCENT", "DLCOc/VA_PRE_PERCENT", "DLCO/VA_PRE_PERCENT")
            dlco_meas    = _first("DLCOc SB_PRE", "DLCOc_PRE", "DLCO SB_PRE")
            kco_meas     = _first("DLCOc/V_PRE", "DLCOc/VA_PRE", "DLCO/VA_PRE")

            # Fallback to raw strings: "pred pre %pred" or "pred LLN pre %pred"
            if dlco_percent is None or dlco_meas is None:
                raw = parse_pred_pre_percent(_first("DLCOc SB", "DLCOc"))
                dlco_percent = dlco_percent if dlco_percent is not None else raw['pct']
                dlco_meas    = dlco_meas    if dlco_meas    is not None else raw['pre']
            if kco_percent is None or kco_meas is None:
                raw = parse_pred_pre_percent(_first("DLCOc/V", "DLCOc/VA"))
                kco_percent = kco_percent if kco_percent is not None else raw['pct']
                kco_meas    = kco_meas    if kco_meas    is not None else raw['pre']

            # Store absolute measured values
            if dlco_meas is not None:
                try:
                    gas_interpretation["values"]["TLCO_meas"] = float(dlco_meas)
                except (ValueError, TypeError):
                    pass
            if kco_meas is not None:
                try:
                    gas_interpretation["values"]["KCO_meas"] = float(kco_meas)
                except (ValueError, TypeError):
                    pass

            # Interpret TLCO (DLCO) percent predicted
            if dlco_percent is not None:
                dlco_percent = float(dlco_percent)
                gas_interpretation["values"]["TLCO_%pred"] = dlco_percent

                if dlco_percent < 80:
                    if dlco_percent < 40:
                        gas_interpretation["findings"].append("Severely reduced TLCO (<40% predicted)")
                    elif dlco_percent < 60:
                        gas_interpretation["findings"].append("Moderately reduced TLCO (<60% predicted)")
                    else:
                        gas_interpretation["findings"].append("Mildly reduced TLCO (<80% predicted)")
                    gas_interpretation["hb_correction_notice"] = (
                        "Ensure DLCO is Hb-corrected (DLCOc). Uncorrected DLCO underestimates severity "
                        "in anaemia and overestimates in polycythaemia "
                        "(ERS standard: correct to Hb 14.6 g/dL for males, 13.4 g/dL for females)."
                    )

            # Interpret KCO percent predicted
            if kco_percent is not None:
                kco_percent = float(kco_percent)
                gas_interpretation["values"]["KCO_%pred"] = kco_percent
                if kco_percent < 80:
                    gas_interpretation["findings"].append("Reduced KCO (<80% predicted)")

            # Pattern logic — from the numbers, not from the findings text
            tlco_reduced = dlco_percent is not None and dlco_percent < 80
            kco_reduced = kco_percent is not None and kco_percent < 80
            gas_interpretation["flags"] = {'tlco_low': bool(tlco_reduced), 'kco_low': bool(kco_reduced)}

            if tlco_reduced and kco_reduced:
                gas_interpretation["pattern"] = "Parenchymal disease pattern"
            elif tlco_reduced and not kco_reduced:
                gas_interpretation["pattern"] = "Vascular limitation or emphysema pattern"
            else:
                gas_interpretation["pattern"] = "Normal gas transfer"

        except Exception as e:
            gas_interpretation["error"] = f"Error interpreting gas transfer: {str(e)}"

        
        return gas_interpretation
    
    def generate_summary_interpretation(self, full_interpretation):
        """Generate a summary interpretation combining all PFT components"""
        summary = {
            'overall_pattern': '',
            'key_findings': [],
            'recommendations': []
        }
        
        try:
            spirometry = full_interpretation.get('spirometry', {})
            volumes = full_interpretation.get('lung_volumes', {})
            gas_transfer = full_interpretation.get('gas_transfer', {})
            
            # Determine overall pattern
            spiro_pattern  = spirometry.get('primary_pattern', '')
            volume_pattern = volumes.get('pattern', '')
            gas_pattern    = gas_transfer.get('pattern', '')
            gas_findings   = str(gas_transfer.get('findings', []))

            # Decide from explicit flags (labels are for display only)
            obstructed = spirometry_obstructed(spirometry)
            spiro_normal = spirometry_normal(spirometry)
            sflags = spirometry.get('flags') or {}
            low_fvc = bool(sflags.get('low_fvc'))
            vflags = volumes.get('flags') or {}
            tlc_known = bool(vflags.get('tlc_known'))
            tlc_low = bool(vflags.get('tlc_low'))
            tlc_high = bool(vflags.get('tlc_high'))
            air_trapping = bool(vflags.get('air_trapping'))
            tlco_low = bool((gas_transfer.get('flags') or {}).get('tlco_low'))

            if obstructed and tlc_low:
                # Lung-volume "Mixed disorder" (low TLC + air trapping + obstruction) and
                # obstruction with simple restriction both end up here, as before
                summary['overall_pattern'] = 'Mixed obstructive-restrictive disorder'
                if tlco_low:
                    summary['key_findings'].append('Mixed disorder with reduced gas transfer — consider ILD with airflow obstruction')

            elif obstructed and low_fvc and not tlc_known:
                # ERS "Possible mixed disorder": low FVC may be restriction or air trapping
                summary['overall_pattern'] = 'Possible mixed disorder — lung volumes needed'
                if tlco_low:
                    summary['key_findings'].append('Obstruction with reduced gas transfer — consider emphysema')

            elif obstructed:
                if air_trapping:
                    summary['overall_pattern'] = 'Obstructive disorder with hyperinflation'
                else:
                    summary['overall_pattern'] = 'Obstructive disorder'
                if tlco_low:
                    summary['key_findings'].append('Obstruction with reduced gas transfer — consider emphysema')

            elif tlc_low:
                summary['overall_pattern'] = 'Complex restrictive disorder' if air_trapping else 'Restrictive disorder'
                if tlco_low:
                    summary['key_findings'].append('Restriction with reduced gas transfer — consider interstitial lung disease')

            elif low_fvc and not tlc_known:
                # Low FVC with normal ratio but no TLC measured: restriction cannot be confirmed
                summary['overall_pattern'] = 'Possible restriction — lung volumes needed'

            elif not spiro_normal and spirometry.get('flags') is not None:
                # Low FVC with normal TLC, or (Murray) low FEV1 with normal ratio and FVC
                summary['overall_pattern'] = 'Non-specific ventilatory defect'
                if tlco_low:
                    summary['key_findings'].append('Non-specific pattern with reduced gas transfer — consider pulmonary vascular disease')

            elif spiro_normal and tlc_high and not air_trapping:
                summary['overall_pattern'] = 'Large lungs (constitutional or air trapping)'

            elif spiro_normal and not (tlc_low or tlc_high or air_trapping):
                if tlco_low:
                    summary['overall_pattern'] = 'Isolated reduction in gas transfer'
                    summary['recommendations'].append('Consider pulmonary vascular disease or early ILD')
                else:
                    summary['overall_pattern'] = 'Normal pulmonary function'

            else:
                summary['overall_pattern'] = spiro_pattern if spiro_pattern else 'Inconclusive — further testing required'
            
            # Add severity if available
            if spirometry.get('severity'):
                summary['severity'] = spirometry['severity']
            
            # Compile key findings
            summary['key_findings'].extend(spirometry.get('clinical_notes', [])[:2])  # Top 2 spirometry findings
            summary['key_findings'].extend(volumes.get('findings', [])[:1])  # Top volume finding
            summary['key_findings'].extend(gas_transfer.get('findings', [])[:1])  # Top gas transfer finding
            
        except Exception as e:
            summary['error'] = f"Error generating summary: {str(e)}"
        
        return summary
    
def perform_clinical_interpretation(murray_results, gli_results, measured_values, age, sex, extracted_data=None):
    """
    Clinical interpretation - handles both basic spirometry and complete PFT
    
    Parameters:
    - murray_results: Murray calculator results
    - gli_results: GLI calculator results  
    - measured_values: Basic spirometry values (FEV1, FVC, ratio)
    - age, sex: Patient demographics
    - extracted_data: Full extracted data including lung volumes and gas transfer (optional)
    """
    interpreter = ClinicalInterpreter()
    
    print(f"\n🏥 CLINICAL INTERPRETATION")
    print(f"Patient: {age}y {sex}")
    print("=" * 50)
    ers2022_interpretation = interpreter.interpret_ers2022_algorithm(measured_values, gli_results)
    traditional_interpretation = interpreter.interpret_traditional_murray(measured_values, murray_results)
    
    # Print spirometry results
    print(f"\n--- ERS 2022 INTERPRETATION ---")
    print(f"Pattern: {ers2022_interpretation['primary_pattern']}")
    print(f"Severity: {ers2022_interpretation['severity']}")
    for note in ers2022_interpretation['clinical_notes']:
        print(f"  • {note}")
    
    print(f"\n--- TRADITIONAL MURRAY INTERPRETATION ---")
    print(f"Pattern: {traditional_interpretation['primary_pattern']}")
    print(f"Severity: {traditional_interpretation['severity']}")
    for note in traditional_interpretation['clinical_notes']:
        print(f"  • {note}")
    
    # Compare methods
    print(f"\n--- METHOD COMPARISON ---")
    ers_pattern = ers2022_interpretation['primary_pattern']
    trad_pattern = traditional_interpretation['primary_pattern']
    
    method_comparison = compare_methods(ers2022_interpretation, traditional_interpretation)
    ers_obstructive  = method_comparison['ers_obstructed']
    trad_obstructive = method_comparison['traditional_obstructed']

    if method_comparison['both_obstructed']:
        print("✅ Both methods detect obstructive pattern")
    elif method_comparison['both_normal']:
        print("✅ Both methods agree: Normal")
    elif method_comparison['methods_agree']:
        print("✅ Both methods agree: neither normal nor obstructive")
    else:
        print("⚠️ Methods disagree - ERS 2022 more accurate for age/height")
    
    # Age-bias warning when methods disagree
    age_bias_warning = None
    if ers_obstructive != trad_obstructive:
        if trad_obstructive and not ers_obstructive and age >= 60:
            age_bias_warning = (
                f"Age-related discordance (age {age:.0f}): The fixed FEV1/FVC < 0.70 cutoff "
                f"commonly over-diagnoses obstruction in patients ≥60y — at this age, "
                f"a ratio just below 0.70 may be physiologically normal. "
                f"GLI LLN-based (ERS 2022) assessment is preferred."
            )
        elif ers_obstructive and not trad_obstructive and age < 45:
            age_bias_warning = (
                f"Age-related discordance (age {age:.0f}): In younger adults, normal FEV1/FVC "
                f"is typically higher (>0.80). The fixed 0.70 cutoff may miss mild obstruction. "
                f"GLI LLN-based (ERS 2022) assessment is preferred."
            )
        else:
            age_bias_warning = (
                "Method discordance: ERS 2022 uses an age/sex/height-specific LLN rather than "
                "a fixed 0.70 threshold, providing more accurate classification across all age groups."
            )

    # Build base response
    interpretation = {
        'ers2022': ers2022_interpretation,
        'traditional': traditional_interpretation,
        'patient_info': {'age': age, 'sex': sex},
        'age_bias_warning': age_bias_warning,
        'method_comparison': method_comparison,   # UI uses this instead of its own label matching
    }

    # BD reversibility response (needs predicted values from calculators)
    if extracted_data:
        fev1_pred_bd = gli_results.get('FEV1_GLI_pred') or murray_results.get('FEV1_Murray_pred')
        fvc_pred_bd  = gli_results.get('FVC_GLI_pred')  or murray_results.get('FVC_Murray_pred')
        interpretation['bd_response'] = interpreter.interpret_bd_response(
            extracted_data, fev1_pred_bd, fvc_pred_bd
        )

    # Check if we have extended PFT data
    if extracted_data:
        has_extended_data = any(extracted_data.get(k) not in (None, "", "None")
            for k in ["RV_PRE", "TLC_PRE", "RV % TLC_PRE",
                     "DLCOc SB_PRE", "DLCOc/V_PRE",
                     "DLCOc_PRE", "DLCOc/VA_PRE",
                     "DLCO SB_PRE", "DLCO/VA_PRE"
    ]
)
        if has_extended_data:
            print(f"\n📊 EXTENDED PFT DATA DETECTED - Performing complete analysis...")
            
            # Get complete PFT interpretation
            complete_pft = interpreter.interpret_complete_pft(extracted_data, murray_results, gli_results)
            interpretation['has_extended_data'] = True
            interpretation['lung_volumes'] = complete_pft.get('lung_volumes')
            interpretation['gas_transfer'] = complete_pft.get('gas_transfer')
            interpretation['complete_summary'] = complete_pft.get('summary')
            
            # Print lung volume results
            if complete_pft.get('lung_volumes'):
                volumes = complete_pft['lung_volumes']
                print(f"\n📏 LUNG VOLUMES:")
                print(f"Pattern: {volumes.get('pattern', 'Unknown')}")
                for finding in volumes.get('findings', []):
                    print(f"  • {finding}")
                if volumes.get('values'):
                    for param, value in volumes['values'].items():
                        print(f"  - {param}: {value:.1f}")
            
            # Print gas transfer results
            if complete_pft.get('gas_transfer'):
                gas = complete_pft['gas_transfer']
                print(f"\n💨 GAS TRANSFER:")
                print(f"Pattern: {gas.get('pattern', 'Unknown')}")
                for finding in gas.get('findings', []):
                    print(f"  • {finding}")
                if gas.get('values'):
                    for param, value in gas['values'].items():
                        print(f"  - {param}: {value:.1f}")
            
            # Print overall summary
            if complete_pft.get('summary'):
                summary = complete_pft['summary']
                print(f"\n🎯 OVERALL INTERPRETATION:")
                print(f"Pattern: {summary.get('overall_pattern', 'Unknown')}")
                if summary.get('severity'):
                    print(f"Severity: {summary['severity']}")
                print("\nKey Findings:")
                for finding in summary.get('key_findings', []):
                    print(f"  • {finding}")
                if summary.get('recommendations'):
                    print("\nRecommendations:")
                    for rec in summary['recommendations']:
                        print(f"  → {rec}")
        else:
            interpretation['has_extended_data'] = False
            print(f"\n📊 Basic spirometry only - no extended PFT data available")
    else:
        interpretation['has_extended_data'] = False
    
    return interpretation

def test_working_calculator():
    """Test the working calculator with clinical interpretation"""
    print("🫁 ENHANCED DUAL CALCULATOR TEST")
    print("=" * 50)
    
    # Test patient data
    age = 74.0
    sex = 'F'
    height = 156.0
    
    # Sample measured values (you can modify these)
    measured_values = {
        'FEV1_PRE': 1.2,     # L
        'FVC_PRE': 2.1,      # L  
        'FEV 1 % FVC_PRE': 57.1  # % (will be converted to ratio)
    }
    
    print(f"Patient: {age} year old {sex}, {height} cm")
    print(f"Measured: FEV1={measured_values['FEV1_PRE']}L, FVC={measured_values['FVC_PRE']}L, Ratio={measured_values['FEV 1 % FVC_PRE']}%")
    
    # Murray calculator
    print(f"\n--- MURRAY RESULTS ---")
    murray_calc = MurrayCalculator()
    murray_results = murray_calc.calculate_patient(age, sex, height)
    
    for param in ['FEV1', 'FVC', 'FEV1_FVC']:
        pred = murray_results.get(f'{param}_Murray_pred', np.nan)
        lln = murray_results.get(f'{param}_Murray_LLN', np.nan)
        if not np.isnan(pred):
            print(f"  {param}: {pred:.3f} (LLN: {lln:.3f})")
    
    # GLI calculator
    print(f"\n--- GLI RESULTS ---")
    gli_calc = WorkingGLI2012Calculator()
    gli_results = {}
    
    if gli_calc.load_gli_tables():
        gli_results = gli_calc.calculate_patient(age, sex, height)
        
        for param in ['FEV1', 'FVC', 'FEV1_FVC']:
            pred = gli_results.get(f'{param}_GLI_pred', np.nan)
            lln = gli_results.get(f'{param}_GLI_LLN', np.nan)
            if not np.isnan(pred):
                print(f"  {param}: {pred:.3f} (LLN: {lln:.3f})")
    
    # ENHANCED: Clinical Interpretation
    if gli_results and murray_results:
        clinical_interpretation = perform_clinical_interpretation(
            murray_results, gli_results, measured_values, age, sex
        )
        
        # Show interpretation summary
        print(f"\n🎯 INTERPRETATION SUMMARY:")
        ers_interp = clinical_interpretation['ers2022']
        trad_interp = clinical_interpretation['traditional'] 
        
        print(f"ERS 2022:     {ers_interp['primary_pattern']} ({ers_interp['severity']})")
        print(f"Traditional:  {trad_interp['primary_pattern']} ({trad_interp['severity']})")
    
    else:
        print("⚠️ Clinical interpretation requires both GLI and Murray results")

def test_clinical_scenarios():
    """Test different clinical scenarios"""
    scenarios = [
        {
            'name': 'Normal Patient',
            'age': 45, 'sex': 'M', 'height': 175,
            'measured': {'FEV1_PRE': 3.8, 'FVC_PRE': 4.5, 'FEV 1 % FVC_PRE': 84.4}
        },
        {
            'name': 'COPD Patient', 
            'age': 65, 'sex': 'M', 'height': 175,
            'measured': {'FEV1_PRE': 2.1, 'FVC_PRE': 3.8, 'FEV 1 % FVC_PRE': 55.3}
        },
        {
            'name': 'Restrictive Pattern',
            'age': 55, 'sex': 'F', 'height': 165,
            'measured': {'FEV1_PRE': 1.8, 'FVC_PRE': 2.0, 'FEV 1 % FVC_PRE': 90.0}
        }
    ]
    
    print("\n" + "="*60)
    print("🧪 CLINICAL SCENARIO TESTING")
    print("="*60)
    
    murray_calc = MurrayCalculator()
    gli_calc = WorkingGLI2012Calculator()
    gli_calc.load_gli_tables()
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name'].upper()} ---")
        
        murray_results = murray_calc.calculate_patient(scenario['age'], scenario['sex'], scenario['height'])
        gli_results = gli_calc.calculate_patient(scenario['age'], scenario['sex'], scenario['height'])
        
        clinical_interpretation = perform_clinical_interpretation(
            murray_results, gli_results, scenario['measured'], scenario['age'], scenario['sex']
        )

if __name__ == "__main__":
    test_working_calculator()
    test_clinical_scenarios()