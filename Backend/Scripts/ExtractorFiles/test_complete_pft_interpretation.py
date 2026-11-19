#!/usr/bin/env python3
"""
Tests for complete PFT interpretation (spirometry + lung volumes + gas transfer + BD).

Data format used here = what the app actually receives:
pdf_extractor.process_file() -> save_data.append_data() expands every raw string
in place, so perform_clinical_interpretation() gets keys like
  RV_PRED, RV_LLN, RV_PRE, RV_PRE_PERCENT   (lung volumes / DLCO: "pred [LLN] pre %pred")
  FEV1_PRED, FEV1_PRE, FEV1_POST, ...       (spirometry with post-BD)
Raw-string parsing is tested separately (parse_pred_pre_percent / BD fallback).

Every check prints one line:  ✓/✗  what was checked  |  expected  |  got
so the results can be validated by hand.

Run:  python test_complete_pft_interpretation.py           (readable report)
      python test_complete_pft_interpretation.py --noisy   (also show the interpreter's own prints)
      pytest test_complete_pft_interpretation.py           (also works)
"""

import contextlib
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Windows consoles/pipes may not be UTF-8; never let a print (✓, emoji) break a test
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

from working_calculator import (
    WorkingGLI2012Calculator,
    MurrayCalculator,
    ClinicalInterpreter,
    parse_pred_pre_percent,
    perform_clinical_interpretation,
)

_OUT = sys.stdout          # report goes here even while the interpreter is silenced
_GLI = None


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def info(text):
    print(f"      · {text}", file=_OUT)


def check(what, got, expected=True, op='=='):
    """Print one validation line, then assert it.
    op: '==' equal, '!=' not equal, 'in' expected is a substring of got,
        'any_in' expected is a substring of at least one item of the list got."""
    if op == '==':
        ok = got == expected
    elif op == '!=':
        ok = got != expected
    elif op == 'in':
        ok = expected in (got or '')
    elif op == 'any_in':
        ok = any(expected in item for item in (got or []))
    else:
        raise ValueError(op)
    shown_expected = {'==': repr(expected), '!=': f"not {expected!r}",
                      'in': f"contains {expected!r}", 'any_in': f"an item containing {expected!r}"}[op]
    print(f"    {'✓' if ok else '✗'} {what}\n        expected: {shown_expected}\n        got:      {got!r}", file=_OUT)
    assert ok, f"{what}: expected {shown_expected}, got {got!r}"


def _gli():
    global _GLI
    if _GLI is None:
        _GLI = WorkingGLI2012Calculator()
        with _quiet():
            loaded = _GLI.load_gli_tables()
        assert loaded, "GLI lookup tables failed to load"
    return _GLI


def _run(age, sex, height, extracted_data):
    murray = MurrayCalculator().calculate_patient(age, sex, height)
    with _quiet():
        gli = _gli().calculate_patient(age, sex, height)
    measured = {k: float(extracted_data[k]) for k in ('FEV1_PRE', 'FVC_PRE', 'FEV 1 % FVC_PRE')}
    info(f"patient {age:.0f}{sex} {height:.0f} cm | FEV1 {measured['FEV1_PRE']} L, "
         f"FVC {measured['FVC_PRE']} L, FEV1/FVC {measured['FEV 1 % FVC_PRE']}%")
    info(f"GLI: FEV1 pred {gli['FEV1_GLI_pred']:.2f} / LLN {gli['FEV1_GLI_LLN']:.2f} | "
         f"FVC pred {gli['FVC_GLI_pred']:.2f} / LLN {gli['FVC_GLI_LLN']:.2f} | "
         f"ratio pred {gli['FEV1_FVC_GLI_pred']:.3f} / LLN {gli['FEV1_FVC_GLI_LLN']:.3f}")
    info(f"Murray: FEV1 pred {murray['FEV1_Murray_pred']:.2f} / LLN {murray['FEV1_Murray_LLN']:.2f} | "
         f"FVC pred {murray['FVC_Murray_pred']:.2f} / LLN {murray['FVC_Murray_LLN']:.2f} | ratio threshold 0.70")
    with _quiet():
        return perform_clinical_interpretation(murray, gli, measured, age, sex, extracted_data)


# ---------------------------------------------------------------- parsers
def test_parse_three_values():
    """Raw 3-value string 'pred pre %pred' (Bug 2)."""
    info("input: '2.45 3.42 139.6'")
    check("parsed fields", parse_pred_pre_percent("2.45 3.42 139.6"),
          {'pred': '2.45', 'lln': None, 'pre': '3.42', 'pct': '139.6'})


def test_parse_four_values():
    """Raw 4-value string 'pred LLN pre %pred' (Bug 2)."""
    info("input: '6.73 5.48 7.22 107.3'")
    check("parsed fields", parse_pred_pre_percent("6.73 5.48 7.22 107.3"),
          {'pred': '6.73', 'lln': '5.48', 'pre': '7.22', 'pct': '107.3'})


def test_parse_missing_or_odd_length():
    """Missing or unknown layouts give no %pred instead of a wrong one (Bug 2)."""
    check("None -> %pred", parse_pred_pre_percent(None)['pct'], None)
    check("'1.0 2.0' (2 values) -> %pred", parse_pred_pre_percent("1.0 2.0")['pct'], None)


def test_lung_volumes_raw_string_fallback():
    """Raw 3-value strings must give the same pattern as expanded keys (Bug 2)."""
    interp = ClinicalInterpreter()
    raw = {'RV': '2.45 3.42 139.6', 'TLC': '6.73 7.22 107.3', 'RV % TLC': '36.4 47.4 130.2'}
    info(f"input: {raw}")
    with _quiet():
        lv = interp.interpret_lung_volumes(raw, is_obstructed=True)
    check("TLC %pred", lv['values']['TLC_%pred'], 107.3)
    check("TLC measured (not the predicted 6.73)", lv['values']['TLC_meas'], 7.22)
    check("pattern (RV/TLC 130% pred = air trapping, TLC normal)", lv['pattern'], 'Hyperinflation')


def test_bd_raw_string_fallback_all_layouts():
    """FEV1 pre/post read from 5-, 6- and 7-value raw strings (Bug 2)."""
    interp = ClinicalInterpreter()
    for layout, fev1_raw in (("5 values", "3.91 2.10 53.7 2.40 61.4"),
                             ("6 values", "3.91 2.10 53.7 2.40 61.4 14.3"),
                             ("7 values (with LLN)", "3.91 2.95 2.10 53.7 2.40 61.4 14.3")):
        info(f"{layout}: '{fev1_raw}'")
        with _quiet():
            bd = interp.interpret_bd_response({'FEV1': fev1_raw}, fev1_pred=3.91)
        check(f"{layout}: FEV1 pre", bd['fev1']['pre'], 2.10)
        check(f"{layout}: FEV1 post", bd['fev1']['post'], 2.40)


def test_save_data_two_value_ratio_is_pred_pre():
    """NEW formats print FEV1/FVC as 'Ref Pre' without post-BD (Bug B)."""
    from save_data import expand_data_keys
    r = expand_data_keys({'FEV 1 % FVC': '77 81'})
    check("'77 81' -> (PRED, PRE, POST)",
          (r['FEV 1 % FVC_PRED'], r['FEV 1 % FVC_PRE'], r['FEV 1 % FVC_POST']), ('77', '81', None))
    r = expand_data_keys({'FEV 1 % FVC': '78 66 70 -4'})
    check("'78 66 70 -4' with post (unchanged) -> (PRED, PRE, POST)",
          (r['FEV 1 % FVC_PRED'], r['FEV 1 % FVC_PRE'], r['FEV 1 % FVC_POST']), ('78', '66', '70'))
    r = expand_data_keys({'FEV6': '3.1 3.2'})
    check("other field FEV6 '3.1 3.2' (unchanged) -> (PRE, POST)", (r['FEV6_PRE'], r['FEV6_POST']), ('3.1', '3.2'))


def test_murray_lln_is_80_percent_of_predicted():
    """Murray LLN = 80% of predicted (Bug 4a)."""
    m = MurrayCalculator().calculate_patient(65, 'M', 175)
    info(f"65M 175 cm: FEV1 pred {m['FEV1_Murray_pred']:.3f}, FVC pred {m['FVC_Murray_pred']:.3f}")
    check("FEV1 LLN", round(m['FEV1_Murray_LLN'], 4), round(0.8 * m['FEV1_Murray_pred'], 4))
    check("FVC LLN", round(m['FVC_Murray_LLN'], 4), round(0.8 * m['FVC_Murray_pred'], 4))


def test_murray_low_ratio_normal_fev1_low_fvc():
    """Murray_2 flowchart: low ratio + normal FEV1 + low FVC (Bug 4a)."""
    murray = {'FEV1_Murray_pred': 3.0, 'FEV1_Murray_LLN': 2.4, 'FVC_Murray_pred': 4.5, 'FVC_Murray_LLN': 3.6}
    measured = {'FEV1_PRE': 2.5, 'FVC_PRE': 3.5, 'FEV 1 % FVC_PRE': 68.0}
    info("ratio 0.68 < 0.70 | FEV1 2.5 >= LLN 2.4 (normal) | FVC 3.5 < LLN 3.6 (low)")
    with _quiet():
        r = ClinicalInterpreter().interpret_traditional_murray(measured, murray)
    check("pattern", r['primary_pattern'], 'Obstruction with concomitant restriction or air trapping')
    check("recommends TLC", r['secondary_findings'], 'TLC recommended', op='any_in')


def test_air_trapping_uses_estimated_uln():
    """RV/TLC above estimated ULN = pred + (pred - LLN) = 36 + 8 = 44 (Bug 4b)."""
    interp = ClinicalInterpreter()
    base = {'TLC_PRED': 6.0, 'TLC_LLN': 4.9, 'TLC_PRE': 6.1, 'TLC_PRE_PERCENT': 101.7,
            'RV % TLC_PRED': 36.0, 'RV % TLC_LLN': 28.0, 'RV % TLC_PRE_PERCENT': 105.6}
    info("RV/TLC pred 36, LLN 28 -> ULN 44 (old rule LLN x 1.3 = 36.4)")
    with _quiet():
        a = interp.interpret_lung_volumes({**base, 'RV % TLC_PRE': 38.0}, False)
        b = interp.interpret_lung_volumes({**base, 'RV % TLC_PRE': 46.0, 'RV % TLC_PRE_PERCENT': 127.8}, False)
        nolln = {k: v for k, v in base.items() if k != 'RV % TLC_LLN'}
        c = interp.interpret_lung_volumes({**nolln, 'RV % TLC_PRE': 46.0, 'RV % TLC_PRE_PERCENT': 127.8}, False)
    check("RV/TLC 38 (below ULN 44; old rule called this air trapping)", a['pattern'], 'Normal lung volumes')
    check("RV/TLC 46 (above ULN 44)", b['pattern'], 'Normal lung volumes', op='!=')
    check("no LLN, RV/TLC 127.8% pred (fallback > 120%)", c['pattern'], 'Normal lung volumes', op='!=')


def test_high_tlc_uses_estimated_uln():
    """TLC above estimated ULN = 6.0 + (6.0 - 4.9) = 7.1 L (Bug 4b)."""
    interp = ClinicalInterpreter()
    base = {'TLC_PRED': 6.0, 'TLC_LLN': 4.9,
            'RV % TLC_PRED': 36.0, 'RV % TLC_LLN': 28.0, 'RV % TLC_PRE': 37.0, 'RV % TLC_PRE_PERCENT': 102.8}
    info("TLC pred 6.0, LLN 4.9 -> ULN 7.1 | RV/TLC kept normal")
    with _quiet():
        high = interp.interpret_lung_volumes({**base, 'TLC_PRE': 7.3, 'TLC_PRE_PERCENT': 121.7}, False)
        normal = interp.interpret_lung_volumes({**base, 'TLC_PRE': 7.0, 'TLC_PRE_PERCENT': 116.7}, False)
        nolln = {k: v for k, v in base.items() if k != 'TLC_LLN'}
        fb = interp.interpret_lung_volumes({**nolln, 'TLC_PRE': 7.3, 'TLC_PRE_PERCENT': 121.7}, False)
    check("TLC 7.3 L (above ULN 7.1)", high['pattern'], 'Large lungs')
    check("TLC 7.0 L (below ULN 7.1)", normal['pattern'], 'Normal lung volumes')
    check("no LLN, TLC 121.7% pred (fallback > 120%)", fb['pattern'], 'Large lungs')


def test_pattern_helpers_cover_every_label():
    """Every primary_pattern both interpreters can return is classified correctly (Bug 5)."""
    from working_calculator import is_obstructive_pattern, is_normal_pattern
    obstructive = ['Airflow obstruction', 'Possible mixed disorder',
                   'Obstructive ventilatory defect', 'Mild obstruction or normal variant',
                   'Obstruction with concomitant restriction or air trapping']
    other = ['Normal spirometry', 'Possible restriction or non-specific pattern',
             'Suggestive of restrictive ventilatory defect', 'Non-specific ventilatory defect']
    for p in obstructive:
        check(f"obstructive: '{p}'", is_obstructive_pattern(p), True)
    for p in other:
        check(f"not obstructive: '{p}'", is_obstructive_pattern(p), False)
    check("normal: 'Normal spirometry'", is_normal_pattern('Normal spirometry'), True)
    check("not normal: 'Mild obstruction or normal variant'", is_normal_pattern('Mild obstruction or normal variant'), False)


def test_method_agreement_murray_obstructive_label():
    """The UI agreement counts Murray 'Obstructive ventilatory defect' as obstruction (Bug 5)."""
    from web_backend import analyze_method_agreement
    ers = {'primary_pattern': 'Airflow obstruction', 'severity': 'Mild'}
    trad = {'primary_pattern': 'Obstructive ventilatory defect', 'severity': 'Moderate'}
    with _quiet():
        a = analyze_method_agreement(ers, trad, {})
        b = analyze_method_agreement({'primary_pattern': 'Normal spirometry', 'severity': 'Normal'},
                                     {'primary_pattern': 'Mild obstruction or normal variant', 'severity': 'Mild'}, {})
    check("ERS 'Airflow obstruction' vs Murray 'Obstructive ventilatory defect' (old code: disagree)",
          a['classification_match'], 'agree')
    check("ERS 'Normal spirometry' vs Murray 'Mild obstruction or normal variant' (old code: agree)",
          b['classification_match'], 'agree', op='!=')


def test_flags_match_patterns():
    """Every interpreter returns explicit flags that agree with its label (Bug 6)."""
    from working_calculator import is_obstructive_pattern, is_normal_pattern
    interp = ClinicalInterpreter()
    with _quiet():
        g = _gli().calculate_patient(60.0, 'M', 175.0)
    m = MurrayCalculator().calculate_patient(60.0, 'M', 175.0)
    info(f"60M 175 cm | GLI ratio LLN {g['FEV1_FVC_GLI_LLN']:.3f}, FVC LLN {g['FVC_GLI_LLN']:.2f} | "
         f"Murray FEV1 LLN {m['FEV1_Murray_LLN']:.2f}, FVC LLN {m['FVC_Murray_LLN']:.2f}")
    for fev1, fvc, ratio in [(3.2, 4.2, 76.0), (2.0, 4.0, 50.0), (1.6, 2.6, 61.5), (2.4, 2.8, 85.7), (2.0, 3.0, 66.7)]:
        meas = {'FEV1_PRE': fev1, 'FVC_PRE': fvc, 'FEV 1 % FVC_PRE': ratio}
        with _quiet():
            results = (('ERS', interp.interpret_ers2022_algorithm(meas, g)),
                       ('Murray', interp.interpret_traditional_murray(meas, m)))
        for method, r in results:
            label, f = r['primary_pattern'], r['flags']
            check(f"FEV1 {fev1} FVC {fvc} ratio {ratio}% | {method} '{label}' -> flags (obstructed, normal)",
                  (f['obstructed'], f['normal']), (is_obstructive_pattern(label), is_normal_pattern(label)))


def test_compare_methods_uses_flags_not_labels():
    """Agreement is decided from flags; a renamed label cannot change it (Bug 6)."""
    from working_calculator import compare_methods
    ers = {'primary_pattern': 'Possible mixed disorder',
           'flags': {'obstructed': True, 'low_fvc': True, 'low_fev1': True, 'normal': False}}
    trad = {'primary_pattern': 'Obstructive ventilatory defect',
            'flags': {'obstructed': True, 'low_fvc': False, 'low_fev1': True, 'normal': False}}
    r = compare_methods(ers, trad)
    check("ERS mixed vs Murray obstructive -> (both_obstructed, methods_agree)",
          (r['both_obstructed'], r['methods_agree']), (True, True))
    check("same, ERS label renamed to 'Some new wording' -> methods_agree",
          compare_methods({**ers, 'primary_pattern': 'Some new wording'}, trad)['methods_agree'], True)
    check("results saved before flags existed (label fallback) -> both_obstructed",
          compare_methods({'primary_pattern': 'Airflow obstruction'},
                          {'primary_pattern': 'Obstructive ventilatory defect'})['both_obstructed'], True)


def test_summary_low_fvc_normal_tlc_is_non_specific():
    """ERS 2022: low FVC with normal TLC is non-specific, not restriction (Bug 6)."""
    interp = ClinicalInterpreter()
    lv = {'TLC_PRED': 6.0, 'TLC_LLN': 4.9, 'TLC_PRE': 6.0, 'TLC_PRE_PERCENT': 100.0,
          'RV % TLC_PRED': 36.0, 'RV % TLC_LLN': 28.0, 'RV % TLC_PRE': 36.0, 'RV % TLC_PRE_PERCENT': 100.0}
    spiro = {'primary_pattern': 'Possible restriction or non-specific pattern', 'clinical_notes': [],
             'flags': {'obstructed': False, 'low_fvc': True, 'low_fev1': True, 'normal': False}}
    info("spirometry: normal ratio, low FVC")
    with _quiet():
        with_tlc = interp.generate_summary_interpretation(
            {'spirometry': spiro, 'lung_volumes': interp.interpret_lung_volumes(lv, False), 'gas_transfer': {}})
        no_tlc = interp.generate_summary_interpretation(
            {'spirometry': spiro, 'lung_volumes': {'pattern': '', 'findings': []}, 'gas_transfer': {}})
    check("with normal TLC (old: 'Restrictive disorder')", with_tlc['overall_pattern'], 'Non-specific ventilatory defect')
    check("without TLC (old: 'Restrictive disorder')", no_tlc['overall_pattern'], 'Possible restriction — lung volumes needed')


def test_summary_ers_mixed_with_low_tlc_keeps_obstruction():
    """ERS 'Possible mixed disorder' + low TLC keeps the obstruction (Bug 6)."""
    interp = ClinicalInterpreter()
    lv = {'TLC_PRED': 6.0, 'TLC_LLN': 4.9, 'TLC_PRE': 4.2, 'TLC_PRE_PERCENT': 70.0,
          'RV % TLC_PRED': 36.0, 'RV % TLC_LLN': 28.0, 'RV % TLC_PRE': 36.0, 'RV % TLC_PRE_PERCENT': 100.0}
    spiro = {'primary_pattern': 'Possible mixed disorder', 'clinical_notes': [],
             'flags': {'obstructed': True, 'low_fvc': True, 'low_fev1': True, 'normal': False}}
    info("spirometry: low ratio + low FVC | TLC 4.2 L < LLN 4.9")
    with _quiet():
        s = interp.generate_summary_interpretation(
            {'spirometry': spiro, 'lung_volumes': interp.interpret_lung_volumes(lv, True), 'gas_transfer': {}})
    check("overall pattern (old: 'Restrictive disorder')", s['overall_pattern'], 'Mixed obstructive-restrictive disorder')


def test_perform_interpretation_returns_method_comparison():
    """The response carries method_comparison for the UI (Bug 6)."""
    r = _run(65.0, 'M', 175.0, {'FEV1_PRE': 2.1, 'FVC_PRE': 3.8, 'FEV 1 % FVC_PRE': 55.3})
    info(f"ERS: '{r['ers2022']['primary_pattern']}' | Murray: '{r['traditional']['primary_pattern']}'")
    mc = r['method_comparison']
    check("method_comparison (both_obstructed, methods_agree)", (mc['both_obstructed'], mc['methods_agree']), (True, True))


# ---------------------------------------------------------------- scenarios
def test_obstruction_with_hyperinflation():
    """65M: FEV1/FVC 55%, RV/TLC 130% pred, normal TLC, low TLCO and KCO."""
    data = {
        'FEV1_PRE': 2.1, 'FVC_PRE': 3.8, 'FEV 1 % FVC_PRE': 55.3,
        'FEV1_PRED': 3.91, 'FEV1_POST': 2.3, 'FVC_PRED': 4.82, 'FVC_POST': 4.0,
        'RV_PRED': 2.45, 'RV_PRE': 3.42, 'RV_PRE_PERCENT': 139.6,
        'TLC_PRED': 6.73, 'TLC_PRE': 7.22, 'TLC_PRE_PERCENT': 107.3,
        'RV % TLC_PRED': 36.4, 'RV % TLC_PRE': 47.4, 'RV % TLC_PRE_PERCENT': 130.2,
        'DLCOc SB_PRED': 8.23, 'DLCOc SB_PRE': 5.12, 'DLCOc SB_PRE_PERCENT': 62.2,
        'DLCOc/V_PRED': 1.42, 'DLCOc/V_PRE': 0.98, 'DLCOc/V_PRE_PERCENT': 69.0,
    }
    r = _run(65.0, 'M', 175.0, data)
    info(f"ERS FEV1 z {r['ers2022'].get('fev1_z_score')} | Murray severity {r['traditional']['severity']} | "
         f"BD: FEV1 {data['FEV1_PRE']} -> {data['FEV1_POST']} L")
    check("ERS pattern (ratio below GLI LLN)", r['ers2022']['primary_pattern'], 'Airflow obstruction')
    check("Murray pattern (ratio < 0.70)", r['traditional']['primary_pattern'].lower(), 'obstructive', op='in')
    check("extended data detected", bool(r['has_extended_data']), True)
    check("lung volumes (RV/TLC 130% pred, TLC 107% pred)", r['lung_volumes']['pattern'], 'Hyperinflation')
    check("TLCO %pred read", r['gas_transfer']['values']['TLCO_%pred'], 62.2)
    check("overall summary", r['complete_summary']['overall_pattern'], 'Obstructive disorder with hyperinflation')
    check("key finding mentions emphysema", r['complete_summary']['key_findings'], 'emphysema', op='any_in')
    check("BD response significant (+200 mL but only ~5% pred)", bool(r['bd_response']['overall_significant']), False)


def test_restrictive_pattern():
    """55F: normal ratio, low FVC, TLC 70% pred, TLCO 60%, KCO preserved."""
    data = {
        'FEV1_PRE': 1.8, 'FVC_PRE': 2.0, 'FEV 1 % FVC_PRE': 90.0,
        'RV_PRED': 1.82, 'RV_PRE': 1.45, 'RV_PRE_PERCENT': 79.7,
        'TLC_PRED': 5.24, 'TLC_PRE': 3.65, 'TLC_PRE_PERCENT': 69.7,
        'RV % TLC_PRED': 34.7, 'RV % TLC_PRE': 39.7, 'RV % TLC_PRE_PERCENT': 114.4,
        'DLCOc SB_PRED': 7.12, 'DLCOc SB_PRE': 4.27, 'DLCOc SB_PRE_PERCENT': 60.0,
        'DLCOc/V_PRED': 1.38, 'DLCOc/V_PRE': 1.17, 'DLCOc/V_PRE_PERCENT': 84.8,
    }
    r = _run(55.0, 'F', 165.0, data)
    info(f"ERS FVC z {r['ers2022'].get('fvc_z_score')} | severity {r['ers2022']['severity']}")
    check("ERS pattern (normal ratio, FVC below LLN)", r['ers2022']['primary_pattern'], 'Possible restriction or non-specific pattern')
    check("lung volumes (TLC 70% pred, no air trapping)", r['lung_volumes']['pattern'], 'Simple restriction')
    check("overall summary", r['complete_summary']['overall_pattern'], 'Restrictive disorder')
    check("key finding mentions interstitial lung disease", r['complete_summary']['key_findings'], 'interstitial', op='any_in')


def test_isolated_gas_transfer_defect():
    """45F: normal spirometry and volumes, TLCO 60% and KCO 57% pred."""
    data = {
        'FEV1_PRE': 3.2, 'FVC_PRE': 3.9, 'FEV 1 % FVC_PRE': 82.1,
        'RV_PRED': 1.95, 'RV_PRE': 2.02, 'RV_PRE_PERCENT': 103.6,
        'TLC_PRED': 5.73, 'TLC_PRE': 5.92, 'TLC_PRE_PERCENT': 103.3,
        'RV % TLC_PRED': 34.0, 'RV % TLC_PRE': 34.1, 'RV % TLC_PRE_PERCENT': 100.3,
        'DLCOc SB_PRED': 7.89, 'DLCOc SB_PRE': 4.73, 'DLCOc SB_PRE_PERCENT': 59.9,
        'DLCOc/V_PRED': 1.41, 'DLCOc/V_PRE': 0.80, 'DLCOc/V_PRE_PERCENT': 56.7,
    }
    r = _run(45.0, 'F', 168.0, data)
    check("ERS pattern", r['ers2022']['primary_pattern'], 'Normal spirometry')
    check("lung volumes", r['lung_volumes']['pattern'], 'Normal lung volumes')
    check("gas-transfer flags (tlco_low, kco_low)",
          (r['gas_transfer']['flags']['tlco_low'], r['gas_transfer']['flags']['kco_low']), (True, True))
    check("overall summary", r['complete_summary']['overall_pattern'], 'Isolated reduction in gas transfer')


def test_new_format_gas_transfer_keys():
    """NEW-format PDFs store DLCOc / DLCOc/VA (not 'DLCOc SB' / 'DLCOc/V') (Bug 2)."""
    data = {
        'FEV1_PRE': 3.2, 'FVC_PRE': 3.9, 'FEV 1 % FVC_PRE': 82.1,
        'DLCOc_PRED': 7.89, 'DLCOc_PRE': 4.73, 'DLCOc_PRE_PERCENT': 59.9,
        'DLCOc/VA_PRED': 1.41, 'DLCOc/VA_PRE': 0.80, 'DLCOc/VA_PRE_PERCENT': 56.7,
    }
    r = _run(45.0, 'F', 168.0, data)
    check("extended data detected", bool(r['has_extended_data']), True)
    check("TLCO %pred read from DLCOc_PRE_PERCENT", r['gas_transfer']['values']['TLCO_%pred'], 59.9)
    check("KCO %pred read from DLCOc/VA_PRE_PERCENT", r['gas_transfer']['values']['KCO_%pred'], 56.7)


if __name__ == "__main__":
    noisy = '--noisy' in sys.argv
    tests = [(n, f) for n, f in list(globals().items()) if n.startswith('test_') and callable(f)]
    failed = []
    for i, (name, fn) in enumerate(tests, 1):
        doc = (fn.__doc__ or '').strip().splitlines()[0] if fn.__doc__ else ''
        print(f"\n[{i}/{len(tests)}] {name}\n      {doc}", file=_OUT)
        try:
            if noisy:
                fn()
            else:
                with _quiet():
                    fn()
            print(f"  PASS  {name}", file=_OUT)
        except Exception as e:
            failed.append(name)
            print(f"  FAIL  {name}: {type(e).__name__}: {e}", file=_OUT)
    print(f"\n{len(tests) - len(failed)}/{len(tests)} passed", file=_OUT)
    if failed:
        print("Failed: " + ", ".join(failed), file=_OUT)
    sys.exit(1 if failed else 0)
