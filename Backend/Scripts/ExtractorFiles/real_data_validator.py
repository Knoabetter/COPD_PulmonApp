"""
DATA VALIDATOR - DIRECT APPROACH

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from working_calculator import WorkingGLI2012Calculator, MurrayCalculator

def get_real_data_location():
    """Get the exact location of your real extracted data"""
    
    print("🎯 DIRECT DATA ACCESS")
    print("=" * 40)
    
    print("Where is your real extracted spirometry data stored?")
    print("\nOptions:")
    print("1. Database (specify connection details)")
    print("2. Excel file (specify exact file path)")
    print("3. React frontend state/localStorage")
    print("4. Flask backend API endpoints")
    
    choice = input("\nEnter option (1-4): ").strip()
    
    if choice == "1":
        return get_database_connection()
    elif choice == "2":
        return get_excel_file()
    elif choice == "3":
        return get_frontend_data()
    elif choice == "4":
        return get_api_data()
    else:
        print("Invalid choice. Using Excel entry mode.")
        return get_excel_file()

def get_database_connection():
    """Get database connection details"""
    print("\n📊 DATABASE ACCESS")
    db_path = input("Enter database file path (e.g., ./patients.db): ").strip()
    table_name = input("Enter table name (e.g., patients): ").strip()
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Available columns: {columns}")
        
        # Get sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        sample_data = cursor.fetchall()
        
        print(f"Sample data: {sample_data}")
        
        conn.close()
        return {'type': 'database', 'path': db_path, 'table': table_name}
        
    except Exception as e:
        print(f"Database error: {e}")
        return None

def get_excel_file():
    """Get .XLSX file path"""
    print("\n📄 Excel FILE ACCESS")
    file_path = input("Enter exact file path: ").strip()
    
    try:
        df = pd.read_excel(file_path)
        print(f"Columns: {list(df.columns)}")
        print(f"Shape: {df.shape}")
        print(f"Sample data:\n{df.head()}")
        
        return {'type': 'excel', 'path': file_path, 'sheet': 0} 
        
    except Exception as e:
        print(f"XLSX error: {e}")
        return None

    """Get JSON file path"""
    print("\n📋 JSON FILE ACCESS")
    file_path = input("Enter exact JSON file path: ").strip()
    
    try:
        import json
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        print(f"Data type: {type(data)}")
        if isinstance(data, list) and len(data) > 0:
            print(f"Sample record: {data[0]}")
        elif isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
        
        return {'type': 'json', 'path': file_path}
        
    except Exception as e:
        print(f"JSON error: {e}")
        return None

def get_frontend_data():
    """Get React frontend data"""
    print("\n⚛️ REACT FRONTEND DATA")
    print("Options:")
    print("1. Browser localStorage dump")
    print("2. Component state export")
    print("3. Public data folder")
    
    sub_choice = input("Enter choice (1-3): ").strip()
    
    if sub_choice == "1":
        print("Export localStorage data from browser console:")
        print("JSON.stringify(localStorage)")
        data_str = input("Paste the exported data: ").strip()
        try:
            import json
            data = json.loads(data_str)
            return {'type': 'localstorage', 'data': data}
        except:
            print("Invalid JSON data")
            return None
    
    elif sub_choice == "3":
        folder_path = input("Enter public data folder path: ").strip()
        return {'type': 'frontend_folder', 'path': folder_path}
    
    return None

def get_api_data():
    """Get Flask backend API data"""
    print("\n🔌 FLASK API ACCESS")
    base_url = input("Enter API base URL (e.g., http://localhost:5000): ").strip()
    endpoint = input("Enter patients endpoint (e.g., /api/patients): ").strip()
    
    try:
        import requests
        response = requests.get(f"{base_url}{endpoint}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API response: {data}")
            return {'type': 'api', 'url': f"{base_url}{endpoint}"}
        else:
            print(f"API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"API error: {e}")
        return None

def load_real_data(data_source):
    """Load real data based on source type"""
    
    if not data_source:
        return None
    
    if data_source['type'] == 'excel':
        df = pd.read_excel(data_source['path'], sheet_name=data_source['sheet'])
        return df.to_dict('records')
    
    elif data_source['type'] == 'json':
        import json
        with open(data_source['path'], 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        else:
            return [data]  # Single record
    
    elif data_source['type'] == 'database':
        import sqlite3
        conn = sqlite3.connect(data_source['path'])
        df = pd.read_sql_query(f"SELECT * FROM {data_source['table']}", conn)
        conn.close()
        return df.to_dict('records')
    
    elif data_source['type'] == 'manual':
        return data_source['data']
    
    elif data_source['type'] == 'api':
        import requests
        response = requests.get(data_source['url'])
        if response.status_code == 200:
            return response.json()
    
    return None

def validate_with_real_data():
    """Main validation function using real data"""
    
    print("🚨 REAL DATA VALIDATION")
    print("=" * 50)
    
    # Get data source
    data_source = get_real_data_location()
    
    if not data_source:
        print("❌ No valid data source provided.")
        return None
    
    # Load real data
    real_patients = load_real_data(data_source)
    
    if not real_patients:
        print("❌ Failed to load data.")
        return None
    
    print(f"✅ Loaded {len(real_patients)} real patient records")
    
    # Initialize calculators
    murray_calc = MurrayCalculator()
    gli_calc = WorkingGLI2012Calculator()
    gli_calc.load_gli_tables()
    
    validation_results = []
    diagnostic_results = []
    
    # Process each real patient
    for i, patient in enumerate(real_patients[:]):  
        print(f"\nProcessing Patient {i+1}: {patient.get('patient_id', f'Patient_{i+1}')}")
        
        try:
            # Ensure required fields exist
            age = float(patient['Age'])
            sex = str(patient['Sex']).upper()
            height = float(patient['Height'])
            print(f"  {age}y {sex} {height}cm")
            
           # Ensure measured_ratio is a fraction (0–1) even if extracted as %
            if patient.get('measured_ratio') is not None:
                mr = float(patient['measured_ratio'])
                measured_ratio = mr / 100.0 if mr > 1.5 else mr
            else:
                measured_ratio = None

            # Diagnose using fractions
            gli_lln = gli_result.get('FEV1_FVC_GLI_LLN', 0.70)
            murray_copd = (measured_ratio is not None) and (measured_ratio < 0.70)
            gli_copd    = (measured_ratio is not None) and (measured_ratio < gli_lln)

            diagnostic_result = {
                'Case': i + 1,
                'Patient_ID': patient.get('patient_id', f'Patient_{i+1}'),
                'Source_ID': patient.get('ID', patient.get('Patient_ID', f'Patient_{i+1}')),  # optional stable key
                'Age': age,
                'Sex': sex,
                'measured_ratio': measured_ratio,
                'measured_ratio_pct': round(measured_ratio*100, 1) if measured_ratio is not None else None,
                'gli_lln': round(gli_lln, 4),
                'gli_lln_pct': round(gli_lln*100, 1),
                'murray_diagnosis': 'COPD' if murray_copd else 'Normal',
                'GLI_diagnosis': 'COPD' if gli_copd else 'Normal',
                'Agreement': 'Yes' if murray_copd == gli_copd else 'No'


            }
            
            # Calculate differences
            validation_result['fev1_diff'] = abs(validation_result['murray_fev1'] - validation_result['gli_fev1'])
            validation_result['ratio_diff'] = abs(validation_result['murray_ratio'] - validation_result['gli_ratio'])
            
            validation_results.append(validation_result)
            
            # Diagnostic agreement (if measured values available)
            if patient.get('measured_ratio') is not None:
                measured_ratio = float(patient['measured_ratio'])
                gli_lln = gli_result.get('FEV1_FVC_GLI_LLN', 0.70)
                
                murray_copd = measured_ratio < 70.0
                gli_copd = (measured_ratio / 100) < gli_lln
                
                diagnostic_result = {
                    'Case': i + 1,
                    'Patient_ID': patient.get('patient_id', f'Patient_{i+1}'),
                    'Age': age,
                    'Sex': sex,
                    'measured_ratio': measured_ratio,
                    'gli_lln': round(gli_lln * 100, 1),
                    'murray_diagnosis': 'COPD' if murray_copd else 'Normal',
                    'GLI_diagnosis': 'COPD' if gli_copd else 'Normal',
                    'Agreement': 'Yes' if murray_copd == gli_copd else 'No'
                }
                
                diagnostic_results.append(diagnostic_result)
                
                print(f"  Measured ratio: {measured_ratio:.1f}%")
                print(f"  Murray: {'COPD' if murray_copd else 'Normal'}, GLI: {'COPD' if gli_copd else 'Normal'}")
                print(f"  Agreement: {'✅' if murray_copd == gli_copd else '❌'}")
            
            print(f"  Murray FEV1: {validation_result['murray_fev1']:.3f}L, GLI: {validation_result['gli_fev1']:.3f}L")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue
    
    # Save results
    if validation_results:
        val_df = pd.DataFrame(validation_results)
        val_df.to_csv('real_extracted_validation_results.csv', index=False)
        print(f"\n✅ Saved validation results: real_extracted_validation_results.csv")
    
    if diagnostic_results:
        diag_df = pd.DataFrame(diagnostic_results)
        diag_df.to_csv('real_extracted_diagnostic_agreement.csv', index=False)
        print(f"✅ Saved diagnostic results: real_extracted_diagnostic_agreement.csv")
    
    return validation_results, diagnostic_results

if __name__ == "__main__":
    print("🎯 REAL EXTRACTED DATA VALIDATOR")
    print("This will use your actual PDF extraction results")
    print("=" * 60)
    
    results = validate_with_real_data()
    
    if results:
        print("\n🎉 SUCCESS! Generated Results 4.2 data from real extractions")
        print("📁 Files ready for your Tables 4.1 and 4.2")
    else:
        print("\n❌ Failed to generate data. Check your data sources.")