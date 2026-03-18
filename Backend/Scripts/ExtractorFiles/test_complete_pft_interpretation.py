#!/usr/bin/env python3
"""
Test script for complete PFT interpretation including lung volumes and gas transfer
"""

import sys
sys.path.append('/mnt/project')

from working_calculator import (
    WorkingGLI2012Calculator, 
    MurrayCalculator,
    perform_complete_clinical_interpretation
)

def test_complete_pft_interpretation():
    """Test complete PFT interpretation with all parameters"""
    
    print("="*70)
    print("COMPLETE PFT INTERPRETATION TEST")
    print("="*70)
    
    # Patient demographics
    age = 65.0
    sex = 'M'
    height = 175.0
    
    # Simulated extracted data from PDF (format: "pred pre pred_pre_percent post pred_post_percent dchange")
    # This is what pdf_extractor.py would provide
    extracted_data = {
        # Basic spirometry (already working)
        'FEV1_PRE': 2.1,  # Measured value in L
        'FVC_PRE': 3.8,   # Measured value in L
        'FEV 1 % FVC_PRE': 55.3,  # Ratio as percentage
        
        # Full extracted strings with percent predicted values
        'FEV1': '3.91 2.1 53.7 2.3 58.8 9.5',  # pred, pre, pre%, post, post%, change
        'FVC': '4.82 3.8 78.8 4.0 83.0 5.3',
        
        # New parameters - Lung Volumes
        'RV': '2.45 3.42 139.6',  # pred, pre, pre% (hyperinflation)
        'TLC': '6.73 7.22 107.3',  # pred, pre, pre% (normal)
        'RV % TLC': '36.4 47.4 130.2',  # pred, pre, pre% (air trapping)
        
        # New parameters - Gas Transfer
        'DLCOc SB': '8.23 5.12 62.2',  # pred, pre, pre% (reduced)
        'DLCOc/V': '1.42 0.98 69.0',   # pred, pre, pre% (reduced KCO)
        
        # Hemoglobin (if available)
        'Hb': '14.2'  # g/dL
    }
    
    # Initialize calculators
    murray_calc = MurrayCalculator()
    gli_calc = WorkingGLI2012Calculator()
    
    # Calculate reference values
    murray_results = murray_calc.calculate_patient(age, sex, height)
    gli_results = {}
    if gli_calc.load_gli_tables():
        gli_results = gli_calc.calculate_patient(age, sex, height)
    
    # Perform complete interpretation
    interpretation = perform_complete_clinical_interpretation(
        murray_results, 
        gli_results, 
        extracted_data, 
        age, 
        sex
    )
    
    print("\n" + "="*70)
    print("EXPECTED INTERPRETATION:")
    print("- Obstructive pattern (FEV1/FVC < 70%)")
    print("- Hyperinflation (RV 139.6% predicted)")
    print("- Air trapping (RV/TLC 130.2% predicted)")
    print("- Reduced gas transfer suggesting emphysema")
    print("- Overall: COPD with emphysematous changes")
    print("="*70)
    
    return interpretation

def test_restrictive_pattern():
    """Test restrictive pattern interpretation"""
    
    print("\n\n" + "="*70)
    print("RESTRICTIVE PATTERN TEST")
    print("="*70)
    
    # Patient demographics
    age = 55.0
    sex = 'F'
    height = 165.0
    
    # Restrictive pattern data
    extracted_data = {
        'FEV1_PRE': 1.8,
        'FVC_PRE': 2.0,
        'FEV 1 % FVC_PRE': 90.0,  # Normal ratio
        
        'FEV1': '2.85 1.8 63.2',
        'FVC': '3.42 2.0 58.5',
        
        # Restrictive volumes
        'RV': '1.82 1.45 79.7',     # Normal RV
        'TLC': '5.24 3.65 69.7',    # Reduced TLC (restrictive)
        'RV % TLC': '34.7 39.7 114.4',
        
        # Reduced gas transfer
        'DLCOc SB': '7.12 4.27 60.0',  # Reduced
        'DLCOc/V': '1.38 1.17 84.8',   # Normal KCO
        
        'Hb': '13.5'
    }
    
    # Initialize calculators
    murray_calc = MurrayCalculator()
    gli_calc = WorkingGLI2012Calculator()
    
    # Calculate reference values
    murray_results = murray_calc.calculate_patient(age, sex, height)
    gli_results = {}
    if gli_calc.load_gli_tables():
        gli_results = gli_calc.calculate_patient(age, sex, height)
    
    # Perform complete interpretation
    interpretation = perform_complete_clinical_interpretation(
        murray_results, 
        gli_results, 
        extracted_data, 
        age, 
        sex
    )
    
    print("\n" + "="*70)
    print("EXPECTED INTERPRETATION:")
    print("- Restrictive pattern (TLC < 80%)")
    print("- Reduced DLCO with preserved KCO")
    print("- Suggests possible interstitial lung disease")
    print("="*70)
    
    return interpretation

def test_isolated_gas_transfer_defect():
    """Test isolated gas transfer defect"""
    
    print("\n\n" + "="*70)
    print("ISOLATED GAS TRANSFER DEFECT TEST")
    print("="*70)
    
    # Patient demographics
    age = 45.0
    sex = 'F'
    height = 168.0
    
    # Normal spirometry with isolated DLCO reduction
    extracted_data = {
        'FEV1_PRE': 3.2,
        'FVC_PRE': 3.9,
        'FEV 1 % FVC_PRE': 82.1,  # Normal ratio
        
        'FEV1': '3.15 3.2 101.6',  # Normal
        'FVC': '3.78 3.9 103.2',   # Normal
        
        # Normal volumes
        'RV': '1.95 2.02 103.6',   # Normal
        'TLC': '5.73 5.92 103.3',  # Normal
        'RV % TLC': '34.0 34.1 100.3',
        
        # Isolated gas transfer reduction
        'DLCOc SB': '7.89 4.73 59.9',  # Significantly reduced
        'DLCOc/V': '1.41 0.80 56.7',   # Also reduced
        
        'Hb': '12.8'
    }
    
    # Initialize calculators
    murray_calc = MurrayCalculator()
    gli_calc = WorkingGLI2012Calculator()
    
    # Calculate reference values
    murray_results = murray_calc.calculate_patient(age, sex, height)
    gli_results = {}
    if gli_calc.load_gli_tables():
        gli_results = gli_calc.calculate_patient(age, sex, height)
    
    # Perform complete interpretation
    interpretation = perform_complete_clinical_interpretation(
        murray_results, 
        gli_results, 
        extracted_data, 
        age, 
        sex
    )
    
    print("\n" + "="*70)
    print("EXPECTED INTERPRETATION:")
    print("- Normal spirometry and lung volumes")
    print("- Isolated severe reduction in gas transfer")
    print("- Consider pulmonary vascular disease or early ILD")
    print("="*70)
    
    return interpretation

if __name__ == "__main__":
    # Run all test scenarios
    test_complete_pft_interpretation()
    test_restrictive_pattern()
    test_isolated_gas_transfer_defect()
    
    print("\n\n✅ Complete PFT interpretation tests completed!")
