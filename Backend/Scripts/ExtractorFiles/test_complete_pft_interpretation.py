#!/usr/bin/env python3
"""
Tests for complete PFT interpretation (spirometry + lung volumes + gas transfer + BD).

Data format used here = what the app actually receives:
pdf_extractor.process_file() -> save_data.append_data() expands every raw string
in place, so perform_clinical_interpretation() gets keys like
  RV_PRED, RV_LLN, RV_PRE, RV_PRE_PERCENT   (lung volumes / DLCO: "pred [LLN] pre %pred")
  FEV1_PRED, FEV1_PRE, FEV1_POST, ...       (spirometry with post-BD)
Raw-string parsing is tested separately (parse_pred_pre_percent / BD fallback).

Run:  python test_complete_pft_interpretation.py      (or: pytest)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from working_calculator import (
    WorkingGLI2012Calculator,
    MurrayCalculator,
    ClinicalInterpreter,
    parse_pred_pre_percent,
    perform_clinical_interpretation,
)

_GLI = None


def _gli():
    global _GLI
    if _GLI is None:
        _GLI = WorkingGLI2012Calculator()
        assert _GLI.load_gli_tables(), "GLI lookup tables failed to load"
    return _GLI


def _run(age, sex, height, extracted_data):
    murray = MurrayCalculator().calculate_patient(age, sex, height)
    gli = _gli().calculate_patient(age, sex, height)
    measured = {k: float(extracted_data[k]) for k in ('FEV1_PRE', 'FVC_PRE', 'FEV 1 % FVC_PRE')}
    return perform_clinical_interpretation(murray, gli, measured, age, sex, extracted_data)


# ---------------------------------------------------------------- parsers
def test_parse_three_values():
    assert parse_pred_pre_percent("2.45 3.42 139.6") == {
        'pred': '2.45', 'lln': None, 'pre': '3.42', 'pct': '139.6'}


def test_parse_four_values():
    assert parse_pred_pre_percent("6.73 5.48 7.22 107.3") == {
        'pred': '6.73', 'lln': '5.48', 'pre': '7.22', 'pct': '107.3'}


def test_parse_missing_or_odd_length():
    assert parse_pred_pre_percent(None)['pct'] is None
    assert parse_pred_pre_percent("1.0 2.0")['pct'] is None


def test_lung_volumes_raw_string_fallback():
    """Raw 3-value strings must give the same pattern as expanded keys."""
    interp = ClinicalInterpreter()
    raw = {'RV': '2.45 3.42 139.6', 'TLC': '6.73 7.22 107.3', 'RV % TLC': '36.4 47.4 130.2'}
    lv = interp.interpret_lung_volumes(raw, is_obstructed=True)
    assert lv['values']['TLC_%pred'] == 107.3
    assert lv['values']['TLC_meas'] == 7.22          # measured, not predicted
    assert lv['pattern'] == 'Hyperinflation'


def test_bd_raw_string_fallback_all_layouts():
    interp = ClinicalInterpreter()
    for fev1_raw in ("3.91 2.10 53.7 2.40 61.4",                # 5 values
                     "3.91 2.10 53.7 2.40 61.4 14.3",           # 6 values
                     "3.91 2.95 2.10 53.7 2.40 61.4 14.3"):     # 7 values (with LLN)
        bd = interp.interpret_bd_response({'FEV1': fev1_raw}, fev1_pred=3.91)
        assert bd['fev1']['pre'] == 2.10, fev1_raw
        assert bd['fev1']['post'] == 2.40, fev1_raw


def test_save_data_two_value_ratio_is_pred_pre():
    """NEW formats print FEV1/FVC as "Ref Pre" without post-BD (Bug B)."""
    from save_data import expand_data_keys
    r = expand_data_keys({'FEV 1 % FVC': '77 81'})
    assert (r['FEV 1 % FVC_PRED'], r['FEV 1 % FVC_PRE'], r['FEV 1 % FVC_POST']) == ('77', '81', None)
    r = expand_data_keys({'FEV 1 % FVC': '78 66 70 -4'})          # with post: unchanged
    assert (r['FEV 1 % FVC_PRED'], r['FEV 1 % FVC_PRE'], r['FEV 1 % FVC_POST']) == ('78', '66', '70')
    r = expand_data_keys({'FEV6': '3.1 3.2'})                      # other fields: unchanged
    assert (r['FEV6_PRE'], r['FEV6_POST']) == ('3.1', '3.2')


def test_murray_lln_is_80_percent_of_predicted():
    m = MurrayCalculator().calculate_patient(65, 'M', 175)
    assert abs(m['FEV1_Murray_LLN'] - 0.8 * m['FEV1_Murray_pred']) < 1e-9
    assert abs(m['FVC_Murray_LLN'] - 0.8 * m['FVC_Murray_pred']) < 1e-9


def test_murray_low_ratio_normal_fev1_low_fvc():
    """Murray_2 flowchart: low ratio + normal FEV1 + low FVC -> obstruction with restriction/air trapping."""
    murray = {'FEV1_Murray_pred': 3.0, 'FEV1_Murray_LLN': 2.4, 'FVC_Murray_pred': 4.5, 'FVC_Murray_LLN': 3.6}
    measured = {'FEV1_PRE': 2.5, 'FVC_PRE': 3.5, 'FEV 1 % FVC_PRE': 68.0}
    r = ClinicalInterpreter().interpret_traditional_murray(measured, murray)
    assert r['primary_pattern'] == 'Obstruction with concomitant restriction or air trapping'
    assert any('TLC recommended' in f for f in r['secondary_findings'])


def test_air_trapping_uses_estimated_uln():
    """RV/TLC 38 with pred 36, LLN 28: above pred (and above LLN*1.3=36.4) but below ULN 44."""
    interp = ClinicalInterpreter()
    base = {'TLC_PRED': 6.0, 'TLC_LLN': 4.9, 'TLC_PRE': 6.1, 'TLC_PRE_PERCENT': 101.7,
            'RV % TLC_PRED': 36.0, 'RV % TLC_LLN': 28.0, 'RV % TLC_PRE_PERCENT': 105.6}
    assert interp.interpret_lung_volumes({**base, 'RV % TLC_PRE': 38.0})['pattern'] == 'Normal lung volumes'
    assert interp.interpret_lung_volumes({**base, 'RV % TLC_PRE': 46.0,
                                          'RV % TLC_PRE_PERCENT': 127.8})['pattern'] != 'Normal lung volumes'
    # no LLN -> fallback %pred > 120
    nolln = {k: v for k, v in base.items() if k != 'RV % TLC_LLN'}
    assert interp.interpret_lung_volumes({**nolln, 'RV % TLC_PRE': 46.0,
                                          'RV % TLC_PRE_PERCENT': 127.8})['pattern'] != 'Normal lung volumes'


def test_high_tlc_uses_estimated_uln():
    """TLC pred 6.0, LLN 4.9 -> ULN 7.1. 7.3 L (121.7%) is high; 7.0 L is not.
    RV/TLC kept below its ULN so only the TLC rule is tested."""
    interp = ClinicalInterpreter()
    base = {'TLC_PRED': 6.0, 'TLC_LLN': 4.9,
            'RV % TLC_PRED': 36.0, 'RV % TLC_LLN': 28.0, 'RV % TLC_PRE': 37.0, 'RV % TLC_PRE_PERCENT': 102.8}
    high = interp.interpret_lung_volumes({**base, 'TLC_PRE': 7.3, 'TLC_PRE_PERCENT': 121.7})
    assert high['pattern'] != 'Normal lung volumes'
    normal = interp.interpret_lung_volumes({**base, 'TLC_PRE': 7.0, 'TLC_PRE_PERCENT': 116.7})
    assert normal['pattern'] == 'Normal lung volumes'
    # no LLN -> fallback %pred > 120
    nolln = {k: v for k, v in base.items() if k != 'TLC_LLN'}
    fb = interp.interpret_lung_volumes({**nolln, 'TLC_PRE': 7.3, 'TLC_PRE_PERCENT': 121.7})
    assert fb['pattern'] != 'Normal lung volumes'


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
    assert r['ers2022']['primary_pattern'] == 'Airflow obstruction'
    assert 'obstructive' in r['traditional']['primary_pattern'].lower()
    assert r['has_extended_data']
    assert r['lung_volumes']['pattern'] == 'Hyperinflation'
    assert r['gas_transfer']['values']['TLCO_%pred'] == 62.2
    assert r['complete_summary']['overall_pattern'] == 'Obstructive disorder with hyperinflation'
    assert any('emphysema' in f for f in r['complete_summary']['key_findings'])
    assert not r['bd_response']['overall_significant']   # +200 mL but only ~6% pred


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
    assert r['ers2022']['primary_pattern'] == 'Possible restriction or non-specific pattern'
    assert r['lung_volumes']['pattern'] == 'Simple restriction'
    assert r['complete_summary']['overall_pattern'] == 'Restrictive disorder'
    assert any('interstitial' in f for f in r['complete_summary']['key_findings'])


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
    assert r['ers2022']['primary_pattern'] == 'Normal spirometry'
    assert r['lung_volumes']['pattern'] == 'Normal lung volumes'
    assert r['complete_summary']['overall_pattern'] == 'Isolated reduction in gas transfer'


def test_new_format_gas_transfer_keys():
    """NEW-format PDFs store DLCOc / DLCOc/VA (not 'DLCOc SB' / 'DLCOc/V')."""
    data = {
        'FEV1_PRE': 3.2, 'FVC_PRE': 3.9, 'FEV 1 % FVC_PRE': 82.1,
        'DLCOc_PRED': 7.89, 'DLCOc_PRE': 4.73, 'DLCOc_PRE_PERCENT': 59.9,
        'DLCOc/VA_PRED': 1.41, 'DLCOc/VA_PRE': 0.80, 'DLCOc/VA_PRE_PERCENT': 56.7,
    }
    r = _run(45.0, 'F', 168.0, data)
    assert r['has_extended_data']
    assert r['gas_transfer']['values']['TLCO_%pred'] == 59.9
    assert r['gas_transfer']['values']['KCO_%pred'] == 56.7


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith('test_') and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except Exception as e:
            failed += 1
            print(f"FAIL  {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
