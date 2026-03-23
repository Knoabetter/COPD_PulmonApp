import sys
import os
# Ensure this file's directory is on sys.path so local modules
# (pdf_extractor, working_calculator, consts, etc.) are importable
# when gunicorn runs with --chdir (which doesn't add cwd to sys.path)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tempfile
import pandas as pd
import numpy as np
import jwt
import bcrypt
from functools import wraps
from flask import Flask, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
from enum import Enum
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
try:
    from working_calculator import (
        WorkingGLI2012Calculator, 
        MurrayCalculator, 
        ClinicalInterpreter,
        perform_clinical_interpretation)
    CLINICAL_INTERPRETER_AVAILABLE = True
    print("✅ Clinical interpretation module loaded successfully")
except ImportError as e:
    print(f"⚠️ Clinical interpretation not available: {e}")
    CLINICAL_INTERPRETER_AVAILABLE = False


def compute_age(dob_str: str, ref_date_str: str | None = None) -> float | None:
    """
    Compute age from Date of Birth and reference date
    dob_str examples: '02/08/1980'
    ref_date_str examples: '08/12/2024' or '08 12 2024'
    """
    if not dob_str:
        return None

    try:       # Parse DOB - try day/month/year format first
        dob = datetime.strptime(dob_str.strip(), "%d/%m/%Y").date()
    except ValueError:  # Try alternative format month/day/year
        try:
            dob = datetime.strptime(dob_str.strip(), "%m/%d/%Y").date()
        except ValueError:
            print(f"⚠️ Could not parse DOB: {dob_str}")
            return None

    ref = None   # Parse reference date if possible, else use today
    if ref_date_str:
        s = ref_date_str.strip().replace(" ", "/")
        # '08 12 2024' -> '08/12/2024'
        # try common formats
        for fmt in ("%d/%m/%Y", "%d/%m/%y", "%m/%d/%Y", "%m/%d/%y"):
            try:
                ref = datetime.strptime(s, fmt).date()
                break
            except ValueError:
                continue

    if ref is None:
        ref = datetime.today().date()

    years = ref.year - dob.year - ((ref.month, ref.day) < (dob.month, dob.day))
    return float(years)

class FORMATS(Enum):
    class OLD(Enum):
        FULL = "OLD_FULL"
        ONLY_SPIROMETRY_WITH_POST = "OLD_ONLY_SPIROMETRY_WITH_POST"
        ONLY_SPIROMETRY_WITHOUT_POST = "OLD_ONLY_SPIROMETRY_WITHOUT_POST"

    class NEW(Enum):
        FULL_WITH_POST = "NEW_FULL_WITH_POST"
        FULL_WITHOUT_POST = "NEW_FULL_WITHOUT_POST"
        ONLY_SPIROMETRY_WITH_POST = "NEW_ONLY_SPIROMETRY_WITH_POST"
        ONLY_SPIROMETRY_WITHOUT_POST = "NEW_ONLY_SPIROMETRY_WITHOUT_POST"
    
    class THIRD(Enum):
        FORMAT = "THIRD_FORMAT"

""" 
Enhanced Database Configuration
"""
DATABASE_FILE_NAME = "copd_extracted_data_trial.xlsx" 
## TODO ##
PDF_EXTRACTOR_AVAILABLE = False
get_data_from_file = None
print("🔍 Attempting to import PDF extractor...")
try:
    from pdf_extractor import get_data_from_file
    PDF_EXTRACTOR_AVAILABLE = True
    print("✅ PDF extractor imported successfully")
    
except Exception as e:
    print(f"❌ PDF extractor import failed: {e}")
    PDF_EXTRACTOR_AVAILABLE = False
    get_data_from_file = None
print(f"📊 PDF Extractor Status: {'Available' if PDF_EXTRACTOR_AVAILABLE else 'Not Available'}")

# ==================== FLASK SERVER INITIALIZATION ====================

print("🚀 Initializing Flask server...")
# Create Flask app
app = Flask(__name__)
CORS(app)

# Custom JSON encoder — converts numpy scalars/nans so jsonify never throws
from flask.json.provider import DefaultJSONProvider

class _NumpyJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return None if np.isnan(obj) else float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

app.json_provider_class = _NumpyJSONProvider
app.json = _NumpyJSONProvider(app)

# ==================== AUTH CONFIG ====================
JWT_SECRET      = os.environ.get('JWT_SECRET', 'dev-secret-change-in-production')
AUTH_USERNAME   = os.environ.get('AUTH_USERNAME', 'admin')
AUTH_PASSWORD_HASH = os.environ.get('AUTH_PASSWORD_HASH', '')

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401
        try:
            jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid or expired token'}), 401
        return f(*args, **kwargs)
    return decorated

# Configuration
# React frontend build directory (relative to this file → project_root/Frontend/dist)
REACT_BUILD = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..', '..', 'Frontend', 'dist'
)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== METHOD AGREEMENT ANALYSIS ====================

def analyze_method_agreement(ers2022_result, traditional_result, measured_values):
    """
    Analyze agreement between ERS 2022 and Traditional methods
    Returns comprehensive comparison metrics
    """
    agreement = {
        'interpretation_agreement': False,
        'severity_agreement': False,
        'classification_match': 'disagree',
        'confidence_level': 'low',
        'clinical_recommendation': '',
        'detailed_comparison': {},
        'method_strengths': {
            'ers2022': [],
            'traditional': []
        }
    }
    
    try:
        # Extract key interpretations
        ers_pattern = ers2022_result.get('primary_pattern', '').lower()
        trad_pattern = traditional_result.get('primary_pattern', '').lower()
        ers_severity = ers2022_result.get('severity', '')
        trad_severity = traditional_result.get('severity', '')
        
        # Pattern agreement analysis
        ers_obstructive = any(word in ers_pattern for word in ['obstruction', 'copd', 'airflow'])
        trad_obstructive = any(word in trad_pattern for word in ['obstruction', 'copd'])
        ers_normal = 'normal' in ers_pattern
        trad_normal = 'normal' in trad_pattern
        
        # Check interpretation agreement
        if (ers_obstructive and trad_obstructive) or (ers_normal and trad_normal):
            agreement['interpretation_agreement'] = True
            agreement['classification_match'] = 'agree'
            agreement['confidence_level'] = 'high'
        elif not ers_obstructive and not trad_obstructive:
            agreement['interpretation_agreement'] = True
            agreement['classification_match'] = 'partial_agree'
            agreement['confidence_level'] = 'medium'
        
        # Severity agreement (if both detect obstruction)
        if ers_obstructive and trad_obstructive:
            # Compare severity levels
            ers_severity_clean = ers_severity.lower()
            trad_severity_clean = trad_severity.lower()
            
            if 'mild' in ers_severity_clean and 'mild' in trad_severity_clean:
                agreement['severity_agreement'] = True
            elif 'moderate' in ers_severity_clean and 'moderate' in trad_severity_clean:
                agreement['severity_agreement'] = True
            elif 'severe' in ers_severity_clean and 'severe' in trad_severity_clean:
                agreement['severity_agreement'] = True
        
        # Generate detailed comparison
        agreement['detailed_comparison'] = {
            'ers2022_interpretation': {
                'pattern': ers2022_result.get('primary_pattern'),
                'severity': ers2022_result.get('severity'),
                'method': 'GLI 2012 reference with age-adjusted LLN'
            },
            'traditional_interpretation': {
                'pattern': traditional_result.get('primary_pattern'),
                'severity': traditional_result.get('severity'), 
                'method': 'Murray equations with fixed 0.70 threshold'
            }
        }
        
        # Method strengths
        agreement['method_strengths']['ers2022'] = [
            'Age, sex, and height adjusted reference values',
            'Uses 5th percentile LLN instead of fixed threshold',
            'More accurate for diverse populations',
            'Current international standard (ERS 2022)'
        ]
        
        agreement['method_strengths']['traditional'] = [
            'Simple fixed threshold (FEV1/FVC < 0.70)',
            'Widely used historical method',
            'Easy to interpret and remember',
            'Consistent with older GOLD guidelines'
        ]
        
        # Clinical recommendations
        if agreement['interpretation_agreement']:
            if ers_obstructive and trad_obstructive:
                agreement['clinical_recommendation'] = (
                    "Both methods detect airflow obstruction. ERS 2022 method provides more "
                    "accurate severity assessment. Consider post-bronchodilator testing if not performed."
                )
            elif ers_normal and trad_normal:
                agreement['clinical_recommendation'] = (
                    "Both methods indicate normal spirometry. No evidence of airflow obstruction."
                )
        else:
            agreement['clinical_recommendation'] = (
                "Methods disagree on interpretation. ERS 2022 method is recommended as it uses "
                "age-adjusted reference values. Consider patient's clinical context and symptoms."
            )
        
        # Calculate confidence score
        confidence_factors = 0
        if agreement['interpretation_agreement']:
            confidence_factors += 3
        if agreement['severity_agreement']:
            confidence_factors += 2
        if ers2022_result.get('clinical_notes') and traditional_result.get('clinical_notes'):
            confidence_factors += 1
            
        if confidence_factors >= 5:
            agreement['confidence_level'] = 'very_high'
        elif confidence_factors >= 3:
            agreement['confidence_level'] = 'high'
        elif confidence_factors >= 2:
            agreement['confidence_level'] = 'medium'
        else:
            agreement['confidence_level'] = 'low'
            
    except Exception as e:
        print(f"❌ Error in method agreement analysis: {e}")
        agreement['error'] = str(e)
    
    return agreement


def validate_measurements(fev1, fvc, ratio, age, height):
    """
    Physiological plausibility checks on extracted spirometry values.
    Returns a list of warning strings (empty = all clear).
    """
    warnings = []

    # FEV1 cannot exceed FVC (FEV1 is always a fraction of FVC)
    if fev1 > 0 and fvc > 0 and fev1 > fvc + 0.15:
        warnings.append(
            f"FEV1 ({fev1:.2f} L) exceeds FVC ({fvc:.2f} L) — "
            "physiologically impossible, likely an extraction error"
        )

    # FEV1/FVC ratio plausibility
    if ratio > 0:
        r = ratio / 100.0 if ratio > 1.5 else ratio
        if r < 0.25 or r > 0.99:
            warnings.append(
                f"FEV1/FVC ratio {r:.2f} is outside the physiological range (0.25–0.99) — "
                "verify extraction"
            )

    # FEV1 absolute range
    if fev1 > 0 and (fev1 < 0.3 or fev1 > 8.0):
        warnings.append(
            f"FEV1 {fev1:.2f} L is outside the plausible range (0.3–8.0 L) — verify extraction"
        )

    # FVC absolute range
    if fvc > 0 and (fvc < 0.3 or fvc > 10.0):
        warnings.append(
            f"FVC {fvc:.2f} L is outside the plausible range (0.3–10.0 L) — verify extraction"
        )

    # Height range for adults
    if age >= 18 and height > 0 and (height < 140 or height > 215):
        warnings.append(
            f"Height {height:.0f} cm is unusual for an adult — verify extraction"
        )

    return warnings


# ==================== BASIC ENDPOINTS ====================

@app.route('/', methods=['GET'])
def home():
    """Serve the React frontend (or API info if build doesn't exist yet)"""
    if not os.path.isdir(REACT_BUILD):
        return jsonify({
            'status': 'API running',
            'note': 'React build not found — run: cd Frontend && npm run build',
            'pdf_extractor_available': PDF_EXTRACTOR_AVAILABLE,
            'clinical_interpreter_available': CLINICAL_INTERPRETER_AVAILABLE
        })
    return send_from_directory(REACT_BUILD, 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'pdf_extractor_available': PDF_EXTRACTOR_AVAILABLE,
        'clinical_interpreter_available': CLINICAL_INTERPRETER_AVAILABLE,
        'message': 'Flask server is running',
        'upload_folder': app.config['UPLOAD_FOLDER']
    })

@app.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    if not AUTH_PASSWORD_HASH:
        return jsonify({'error': 'Server auth not configured — set AUTH_PASSWORD_HASH env var'}), 503
    username_ok = username == AUTH_USERNAME
    try:
        password_ok = bcrypt.checkpw(password.encode(), AUTH_PASSWORD_HASH.encode())
    except Exception:
        password_ok = False
    if not username_ok or not password_ok:
        return jsonify({'error': 'Invalid credentials'}), 401
    token = jwt.encode(
        {'sub': username, 'exp': datetime.now(timezone.utc) + timedelta(hours=24)},
        JWT_SECRET, algorithm='HS256'
    )
    return jsonify({'success': True, 'token': token})

@app.route('/auth/logout', methods=['POST'])
def auth_logout():
    return jsonify({'success': True})

@app.route('/api/pdf/<filename>')
@require_auth
def serve_pdf(filename):
    """Serve uploaded PDF files"""
    try:
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(pdf_path):
            return send_file(pdf_path, mimetype='application/pdf')
        else:
            return jsonify({'error': 'PDF not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Upload ENDPOINT ==================== 

@app.route('/upload', methods=['POST'])
@require_auth
def upload_file():
    """
    Enhanced PDF upload endpoint with ERS 2022 dual-method clinical interpretation
    Returns both traditional and ERS 2022 spirometry interpretations
    """
    if not PDF_EXTRACTOR_AVAILABLE:
        return jsonify({
            'error': 'PDF extractor not available. Please check server configuration.',
            'success': False
        }), 503
    
    pdf_path = None  # Track PDF path for cleanup
    
    try:
        # File validation
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file uploaded',
                'success': False
            }), 400
        
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'success': False
            }), 400
        
        if not allowed_file(uploaded_file.filename):
            return jsonify({
                'error': 'Only PDF files are allowed.',
                'success': False
            }), 400
        
        # Save uploaded file temporarily with secure filename
        filename = secure_filename(uploaded_file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        try:
            uploaded_file.save(pdf_path)
            print(f"📁 File uploaded: {safe_filename}")
        except Exception as e:
            return jsonify({
                'error': f'Failed to save file: {str(e)}',
                'success': False
            }), 500
        
        # Extract data from PDF
        try:
            extracted_data = get_data_from_file(pdf_path)
            print("BACKEND: keys sample after get_data_from_file:", list(extracted_data.keys())[:30])
            extraction_message = "PDF processing completed successfully"
        except Exception as e:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            return jsonify({
                'error': f'PDF extraction failed: {str(e)}',
                'success': False
            }), 500
        
        # Validate required patient data
        required_fields = ['Age', 'Sex', 'Height']
        missing_fields = [field for field in required_fields 
                         if field not in extracted_data or not extracted_data[field]]
        
        if missing_fields:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            return jsonify({
                'error': f'Missing required patient data: {missing_fields}',
                'success': False,
                'extracted_data': extracted_data
            }), 400
        
        # Extract and validate patient parameters
        try:
            age = float(extracted_data['Age'])
            sex = str(extracted_data['Sex']).upper()
            height = float(extracted_data['Height'])
            
            # Validation ranges
            if not (3 <= age <= 95):
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                return jsonify({
                    'error': 'Age must be between 3 and 95 years',
                    'success': False
                }), 400
            
            if sex not in ['M', 'F']:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                return jsonify({
                    'error': 'Sex must be M or F',
                    'success': False
                }), 400
            
            if not (100 <= height <= 250):
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                return jsonify({
                    'error': 'Height must be between 100 and 250 cm',
                    'success': False
                }), 400
                
        except (ValueError, TypeError) as e:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            return jsonify({
                'error': f'Invalid patient data format: {str(e)}',
                'success': False
            }), 400
        
        print(f"✅ Patient validated: {age}y {sex} {height}cm")

        # Extract measured values - INCLUDING extended PFT parameters
        measured_values = {}

        # Basic spirometry fields (for backward compatibility)
        spirometry_fields = ['FEV1_PRE', 'FVC_PRE', 'FEV 1 % FVC_PRE']
        for field in spirometry_fields:
            if field in extracted_data and extracted_data[field]:
                try:
                    measured_values[field] = float(extracted_data[field])
                except (ValueError, TypeError):
                    print(f"⚠️ Could not convert {field}: {extracted_data[field]}")
        
        # Extract measured values for extended PFT parameters
        # Note: These are already in the extracted_data with full strings
        extended_fields = ['FEV1', 'FVC', 'RV', 'TLC', 'RV % TLC', 'DLCOc SB', 'DLCOc/V', 'DLCOc', 'DLCOc/VA']
        for field in extended_fields:
            if field in extracted_data and extracted_data[field]:
                # These contain full strings like "pred pre pred_pre_percent..."
                # We'll pass the full extracted_data to the interpretation function
                print(f"✅ Found extended parameter: {field}")
        
        print(f"📊 Basic measured values: {measured_values}")

        # Plausibility validation
        validation_warnings = validate_measurements(
            fev1=measured_values.get('FEV1_PRE', 0),
            fvc=measured_values.get('FVC_PRE', 0),
            ratio=measured_values.get('FEV 1 % FVC_PRE', 0),
            age=age,
            height=height
        )
        if validation_warnings:
            print(f"⚠️ Validation warnings: {validation_warnings}")

        # Perform spirometry calculations
        murray_results = {}
        gli_results = {}
        clinical_interpretation = {}
        
        if CLINICAL_INTERPRETER_AVAILABLE:
            try:
                # Murray (Traditional) calculations
                murray_calc = MurrayCalculator()
                murray_results = murray_calc.calculate_patient(age, sex, height)
                print(f"✅ Murray calculations completed")
                
                # GLI 2012 calculations
                gli_calc = WorkingGLI2012Calculator()
                if gli_calc.load_gli_tables():
                    gli_results = gli_calc.calculate_patient(age, sex, height)
                    print(f"✅ GLI calculations completed")
                else:
                    print(f"⚠️ GLI tables not loaded - using Murray only")
                
                # Complete Clinical interpretation with extended data
                if measured_values and (murray_results or gli_results):
                    clinical_interpretation = perform_clinical_interpretation(
                        murray_results, 
                        gli_results, 
                        measured_values, 
                        age, 
                        sex, 
                        extracted_data  # Pass full extracted data for extended analysis
                    )
                    print(f"🏥 Clinical interpretation completed")
                    
                    # Add method agreement analysis if both methods available
                    if (clinical_interpretation and 
                        'ers2022' in clinical_interpretation and 
                        'traditional' in clinical_interpretation):
                        
                        method_agreement = analyze_method_agreement(
                            clinical_interpretation['ers2022'],
                            clinical_interpretation['traditional'],
                            measured_values
                        )
                        clinical_interpretation['method_agreement'] = method_agreement
                        print(f"🔄 Method agreement analysis completed")
                
            except Exception as e:
                print(f"❌ Clinical calculation error: {e}")
                clinical_interpretation = {
                    'error': f'Clinical interpretation failed: {str(e)}'
                }
        
        # Prepare comprehensive response with ACTUAL data
        response_data = {
            'success': True,
            'message': f'File processed successfully: {extraction_message}',
            'filename': filename,
            'patient_info': {
                'age': age,
                'sex': sex,
                'height': height
            },
            'extraction_info': {
                'age': age,
                'sex': sex,
                'height': height,
                'fev1_pre': measured_values.get('FEV1_PRE'),
                'fvc_pre': measured_values.get('FVC_PRE'),
                'ratio_pre': measured_values.get('FEV 1 % FVC_PRE'),
            },
            'validation_warnings': validation_warnings,
            'measured_values': measured_values,
            'extracted_data': extracted_data,
            'murray_predictions': murray_results,
            'gli_predictions': gli_results,
            'clinical_interpretation': clinical_interpretation,
            'processing_info': {
                'pdf_extraction': 'success',
                'murray_calculations': 'success' if murray_results else 'failed',
                'gli_calculations': 'success' if gli_results else 'failed',
                'clinical_interpretation': 'success' if clinical_interpretation and 'error' not in clinical_interpretation else 'failed',
                'has_extended_pft': clinical_interpretation.get('has_extended_data', False) if clinical_interpretation else False
            }
        }
        
        # Enhanced logging for results
        if clinical_interpretation and 'ers2022' in clinical_interpretation:
            ers_interp = clinical_interpretation['ers2022']
            trad_interp = clinical_interpretation['traditional']
            
            print(f"\n🎯 INTERPRETATION SUMMARY:")
            print(f"ERS 2022:     {ers_interp.get('primary_pattern')} ({ers_interp.get('severity')})")
            print(f"Traditional:  {trad_interp.get('primary_pattern')} ({trad_interp.get('severity')})")
            
            if clinical_interpretation.get('has_extended_data'):
                print(f"Extended PFT: Yes")
                if clinical_interpretation.get('complete_summary'):
                    summary = clinical_interpretation['complete_summary']
                    print(f"Overall:      {summary.get('overall_pattern')}")
        
        # Clean up the uploaded file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f"🗑️ Temporary file cleaned up: {safe_filename}")
        
        print(f"✅ Upload processing completed successfully")
        
        # ACTUALLY RETURN THE RESPONSE!
        return jsonify(response_data)
            
    except Exception as e:
        # Clean up on any error
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except:
                pass
        
        print(f"❌ Upload error: {e}")
        return jsonify({
            'error': f'Server error: {str(e)}',
            'success': False
        }), 500
    # ==================== TEST ENDPOINT ====================

@app.route('/test', methods=['GET'])
@require_auth
def test_extraction():
    """Test endpoint to verify PDF extraction without file upload"""
    if not PDF_EXTRACTOR_AVAILABLE:
        return jsonify({
            'error': 'PDF extractor not available. Please check server configuration.',
            'success': False,
            'service_status': 'PDF extraction service unavailable'
        }), 503
    
    try:
        extracted_data = get_data_from_file("test_file.pdf")
        message = "Test extraction completed successfully"        
        return jsonify({
            'success': True,
            'data': extracted_data,
            'message': f"Test extraction: {message}",
            'extractor_mode': 'real'
        })
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return jsonify({
            'error': f'Test failed: {str(e)}',
            'success': False
        }), 500

# ==================== Analyze ENDPOINT ====================

@app.route('/analyze', methods=['POST'])
@require_auth
def clinical_analysis():
    """
    Clinical Analysis endpoint with ERS 2022 dual-method and Lung functions interpretation
    """
    if not PDF_EXTRACTOR_AVAILABLE:
        return jsonify({
            'error': 'PDF extractor not available — check server logs for the import error.',
            'success': False
        }), 503

    try:
        # Handle file upload from FormData
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided', 'success': False}), 400
        
        uploaded_file = request.files['file']
        criteria = request.form.get('criteria', 'comparison')  # 'comparison', 'ers2022', 'traditional'
        
        if uploaded_file.filename == '':
            return jsonify({'error': 'No file selected', 'success': False}), 400

        # Create secure filename and save to uploads folder
        filename = secure_filename(uploaded_file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        uploaded_file.save(pdf_path)
        print(f"📁 File saved: {pdf_path}")

        try:
            extracted_data = get_data_from_file(pdf_path) # Extract data from PDF
                        # Auto-fill Age if missing using Date of Birth
            if not extracted_data.get("Age") or extracted_data.get("Age") is None:
                dob = extracted_data.get("Date of Birth")
                ref_date = extracted_data.get("Date_PRE") or extracted_data.get("Date")
                computed_age = compute_age(dob, ref_date)
                
                if computed_age:
                    extracted_data["Age"] = computed_age
                    print(f"🔧 Computed age from DOB: {computed_age} years")
                else:
                    print(f"⚠️ Could not compute age - DOB: {dob}, Ref date: {ref_date}")
            
            message = "PDF processing completed successfully"
            # Validate required fields
            required_fields = ['Age', 'Sex', 'Height']
            missing_fields = [
                field for field in required_fields
                if field not in extracted_data or not extracted_data[field]
            ]

            if missing_fields:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                return jsonify({
                    'error': f'Missing required fields: {missing_fields}',
                    'success': False
                }), 400

            # Extract patient data
            age = float(extracted_data['Age'])
            sex = str(extracted_data['Sex']).upper()
            height = float(extracted_data['Height'])

            # Validate ranges
            if not (3 <= age <= 95) or sex not in ['M', 'F'] or not (100 <= height <= 250):
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                return jsonify({
                    'error': 'Invalid patient data ranges',
                    'success': False
                }), 400

            # Extract measured values (always FEV1/FVC/ratio)
            measured_values = {}
            for field in ['FEV1_PRE', 'FVC_PRE', 'FEV 1 % FVC_PRE']:
                if field in extracted_data and extracted_data[field]:
                    try:
                        measured_values[field] = float(extracted_data[field])
                    except (ValueError, TypeError):
                        pass

            if (
                not measured_values.get('FEV1_PRE')
                and measured_values.get('FVC_PRE')
                and measured_values.get('FEV 1 % FVC_PRE')
            ):
                fvc = measured_values['FVC_PRE']
                ratio_percent = measured_values['FEV 1 % FVC_PRE']
                ratio = ratio_percent / 100 if ratio_percent > 1 else ratio_percent
                calculated_fev1 = fvc * ratio
                measured_values['FEV1_PRE'] = calculated_fev1
                print(f"🔧 CALCULATED FEV1: {calculated_fev1:.2f}L from FVC={fvc}L × ratio={ratio:.3f}")


            # Perform calculations and interpretation
            if CLINICAL_INTERPRETER_AVAILABLE:
                murray_calc = MurrayCalculator()
                murray_results = murray_calc.calculate_patient(age, sex, height)

                gli_calc = WorkingGLI2012Calculator()
                gli_results = {}
                if gli_calc.load_gli_tables():
                    gli_results = gli_calc.calculate_patient(age, sex, height)
                
                clinical_interpretation = perform_clinical_interpretation(
                    murray_results, gli_results, measured_values, age, sex, extracted_data
                )
                print(f"🏥 Clinical interpretation completed")
                if clinical_interpretation.get('has_extended_data'):
                    print(f"🫁 Complete PFT interpretation included")
                else:
                    print(f"📊 Basic spirometry only - no extended PFT data")
                
                # Add method agreement if both methods available
                if (clinical_interpretation and 
                    'ers2022' in clinical_interpretation and 
                    'traditional' in clinical_interpretation):
                    
                    method_agreement = analyze_method_agreement(
                        clinical_interpretation['ers2022'],
                        clinical_interpretation['traditional'],
                        measured_values
                    )
                    clinical_interpretation['method_agreement'] = method_agreement

                # Filter response based on criteria
                if criteria == 'ers2022' and clinical_interpretation:
                    response_interpretation = {
                        'ers2022': clinical_interpretation.get('ers2022'),
                        'method': 'ERS 2022 Standards Only'
                    }
                elif criteria == 'traditional' and clinical_interpretation:
                    response_interpretation = {
                        'traditional': clinical_interpretation.get('traditional'),
                        'method': 'Traditional GOLD Only'
                    }
                else:
                    response_interpretation = clinical_interpretation

                return jsonify({
                    'success': True,
                    'analysis_type': criteria,
                    'patient_info': {
                        'age': age,
                        'sex': sex,
                        'height': height
                    },
                    'measured_values': measured_values,
                    'murray_predictions': murray_results,
                    'gli_predictions': gli_results,
                    'clinical_interpretation': response_interpretation,
                    'pdf_filename': safe_filename,
                    'timestamp': datetime.now().isoformat(),
                    'message': f'Analysis completed using {criteria} method(s)'
                })

            else:
                return jsonify({
                    'error': 'Clinical interpretation module not available',
                    'success': False
                }), 503

        except Exception as e:
            # Clean up on processing error
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            print(f"❌ Processing error: {e}")
            raise e

    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500
    
# ==================== BATCH ANALYSIS ENDPOINT ====================

@app.route('/analyze/batch', methods=['POST'])
@require_auth
def batch_clinical_analysis():
    """
    Batch Clinical Analysis - Analyze multiple PDFs at once
    """
    if not PDF_EXTRACTOR_AVAILABLE:
        return jsonify({
            'error': 'PDF extractor not available — check server logs for the import error.',
            'success': False
        }), 503

    try:
        # Get files from FormData
        files = []
        for key in request.files:
            if key.startswith('file'):
                file = request.files[key]
                if file and file.filename:
                    files.append(file)
        
        criteria = request.form.get('criteria', 'comparison')
        
        if len(files) == 0:
            return jsonify({'error': 'No files provided', 'success': False}), 400
            
        if len(files) > 5:
            return jsonify({'error': 'Maximum 5 files allowed', 'success': False}), 400
        
        print(f"📁 Received {len(files)} files for batch analysis")
        
        results = []
        successful_count = 0
        
        for i, uploaded_file in enumerate(files):
            print(f"🔄 Processing file {i+1}/{len(files)}: {uploaded_file.filename}")
            
            if not uploaded_file.filename or not uploaded_file.filename.lower().endswith('.pdf'):
                results.append({
                    'filename': uploaded_file.filename or f'file_{i}',
                    'success': False,
                    'error': 'Invalid file type',
                    'index': i
                })
                continue
            
            try:
                # Create secure filename with batch identifier
                filename = secure_filename(uploaded_file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_filename = f"batch_{timestamp}_{i:02d}_{filename}"
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
                
                uploaded_file.save(pdf_path)
                
                # Extract data using PDF extractor
                extracted_data = get_data_from_file(pdf_path)
                
                # Validate and process (similar to single analysis)
                required_fields = ['Age', 'Sex', 'Height']
                missing_fields = [field for field in required_fields 
                                 if field not in extracted_data or not extracted_data[field]]
                
                if missing_fields:
                    os.remove(pdf_path)
                    results.append({
                        'filename': uploaded_file.filename,
                        'success': False,
                        'error': f'Missing required fields: {missing_fields}',
                        'index': i
                    })
                    continue
                
                # Extract patient data
                age = float(extracted_data['Age'])
                sex = str(extracted_data['Sex']).upper()
                height = float(extracted_data['Height'])
                
                # Validate ranges
                if not (3 <= age <= 95) or sex not in ['M', 'F'] or not (100 <= height <= 250):
                    os.remove(pdf_path)
                    results.append({
                        'filename': uploaded_file.filename,
                        'success': False,
                        'error': 'Invalid patient data ranges',
                        'index': i
                    })
                    continue
                
                # Perform calculations
                murray_calc = MurrayCalculator()
                murray_results = murray_calc.calculate_patient(age, sex, height)
                
                gli_calc = WorkingGLI2012Calculator()
                gli_results = {}
                if gli_calc.load_gli_tables():
                    gli_results = gli_calc.calculate_patient(age, sex, height)
                
                # Extract measured values
                measured_values = {}
                for field in ['FEV1_PRE', 'FVC_PRE', 'FEV 1 % FVC_PRE']:
                    if field in extracted_data and extracted_data[field]:
                        try:
                            measured_values[field] = float(extracted_data[field])
                        except (ValueError, TypeError):
                            pass
                
                # Validation warnings
                validation_warnings = []
                if CLINICAL_INTERPRETER_AVAILABLE:
                    validation_warnings = validate_measurements(
                        fev1=measured_values.get('FEV1_PRE', 0),
                        fvc=measured_values.get('FVC_PRE', 0),
                        ratio=measured_values.get('FEV 1 % FVC_PRE', 0),
                        age=age,
                        height=height
                    )

                # Clinical interpretation (same pipeline as single /analyze)
                clinical_interpretation = {}
                if CLINICAL_INTERPRETER_AVAILABLE and measured_values and (murray_results or gli_results):
                    try:
                        clinical_interpretation = perform_clinical_interpretation(
                            murray_results, gli_results, measured_values, age, sex, extracted_data
                        )
                        if ('ers2022' in clinical_interpretation and
                                'traditional' in clinical_interpretation):
                            clinical_interpretation['method_agreement'] = analyze_method_agreement(
                                clinical_interpretation['ers2022'],
                                clinical_interpretation['traditional'],
                                measured_values
                            )
                    except Exception as e:
                        clinical_interpretation = {'error': f'Interpretation failed: {str(e)}'}

                # Add successful result
                results.append({
                    'filename': uploaded_file.filename,
                    'success': True,
                    'index': i,
                    'patient_info': {
                        'age': age,
                        'sex': sex,
                        'height': height
                    },
                    'measured_values': measured_values,
                    'murray_predictions': murray_results,
                    'gli_predictions': gli_results,
                    'validation_warnings': validation_warnings,
                    'clinical_interpretation': clinical_interpretation,
                    'pdf_filename': safe_filename,
                    'timestamp': datetime.now().isoformat()
                })

                successful_count += 1
                print(f"✅ Successfully processed {uploaded_file.filename}")

            except Exception as e:
                if 'pdf_path' in locals() and os.path.exists(pdf_path):
                    os.remove(pdf_path)

                print(f"❌ Error processing {uploaded_file.filename}: {str(e)}")
                results.append({
                    'filename': uploaded_file.filename,
                    'success': False,
                    'error': f'Processing error: {str(e)}',
                    'index': i
                })

        # Summary counts for frontend status line
        copd_cases = borderline_cases = normal_cases = 0
        for r in results:
            if r.get('success'):
                ratio = r.get('measured_values', {}).get('FEV 1 % FVC_PRE', 1)
                if ratio < 0.70:
                    copd_cases += 1
                elif ratio < 0.75:
                    borderline_cases += 1
                else:
                    normal_cases += 1

        return jsonify({
            'success': True,
            'total_files': len(files),
            'successful_analyses': successful_count,
            'failed_analyses': len(files) - successful_count,
            'results': results,
            'summary': {
                'copd_cases': copd_cases,
                'borderline_cases': borderline_cases,
                'normal_cases': normal_cases,
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Batch analysis error: {e}")
        return jsonify({
            'error': f'Batch analysis failed: {str(e)}',
            'success': False
        }), 500

# ==================== CLEANUP ENDPOINT ====================

@app.route('/cleanup/old-pdfs', methods=['POST'])
@require_auth
def cleanup_old_pdfs():
    """Clean up PDFs older than 24 hours"""
    try:
        import time
        current_time = time.time()
        cleanup_count = 0
        
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.endswith('.pdf'):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_age = current_time - os.path.getctime(file_path)
                
                # Delete files older than 24 hours (86400 seconds)
                if file_age > 86400:
                    os.remove(file_path)
                    cleanup_count += 1
                    print(f"🗑️ Cleaned up old PDF: {filename}")
        
        return jsonify({
            'success': True,
            'cleaned_files': cleanup_count,
            'message': f'Cleaned up {cleanup_count} old PDF files'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ==================== SEARCH & DIAGNOSIS ENDPOINTS ====================

@app.route('/search/patient/<patient_id>', methods=['GET'])
@require_auth
def search_patient_tests(patient_id):
    """Get all tests for a specific patient ID"""
    try:
        df = read_database()
        
        if df.empty:
            return jsonify({
                'success': True,
                'tests': [],
                'message': 'No database found'
            })
        
        # Filter by patient ID
        patient_tests = df[df['ID'].astype(str) == str(patient_id)]
        
        if patient_tests.empty:
            return jsonify({
                'success': True,
                'tests': [],
                'message': f'No tests found for patient ID: {patient_id}'
            })
        
        # Convert to list of dictionaries
        tests = []
        for _, row in patient_tests.iterrows():
            dlcoc_field = get_dlcoc_field(row)
            test_data = {
                'id': row.get('ID'),
                'date_pre': row.get('Date_PRE'),
                'date_post': row.get('Date_POST'),
                'format': row.get('Format'),
                'age': row.get('Age'),
                'sex': row.get('Sex'),
                'height': row.get('Height'),
                'validator': row.get('Validator'),
                'diagnosis': row.get('Diagnosis', ''),
                # Key parameters
                'fev1_pre': row.get('FEV1_PRE'),
                'fvc_pre': row.get('FVC_PRE'),
                'fev1_fvc_pre': row.get('FEV 1 % FVC_PRE'),
                'dlcoc_pre': row.get(dlcoc_field) if dlcoc_field else None,
                'dlcoc_va_pre': row.get('DLCOc/VA_PRE') or row.get('DLCO/VA_PRE'),
                'rv_pre': row.get('RV_PRE'),
                'tlc_pre': row.get('TLC_PRE'),
                # Predicted values for comparison
                'fev1_pred': row.get('FEV1_PRED'),
                'fvc_pred': row.get('FVC_PRED'),
                'rv_pred': row.get('RV_PRED'),
                'tlc_pred': row.get('TLC_PRED'),
                # Percentages
                'fev1_percent': row.get('FEV1_PRE_PERCENT'),
                'fvc_percent': row.get('FVC_PRE_PERCENT')
            }
            tests.append(test_data)
        
        # Sort by date (most recent first)
        tests.sort(key=lambda x: x.get('date_pre', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'tests': tests,
            'total_tests': len(tests),
            'patient_id': patient_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error searching patient tests: {str(e)}'
        }), 500

@app.route('/search/date-range', methods=['POST'])
@require_auth
def search_tests_by_date():
    """Get tests within a date range"""
    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({
                'success': False,
                'error': 'start_date and end_date are required'
            }), 400
        
        df = read_database()
        
        if df.empty:
            return jsonify({
                'success': True,
                'tests': [],
                'message': 'No database found'
            })
        
        # Convert date strings to datetime for comparison
        start_dt = pd.to_datetime(start_date, errors='coerce')
        end_dt = pd.to_datetime(end_date, errors='coerce')
        
        # Filter by date range
        df['Date_PRE_dt'] = pd.to_datetime(df['Date_PRE'], errors='coerce')
        filtered_tests = df[
            (df['Date_PRE_dt'] >= start_dt) & 
            (df['Date_PRE_dt'] <= end_dt)
        ]
        
        # Convert to list format
        tests = []
        for _, row in filtered_tests.iterrows():
            test_data = {
                'id': row.get('ID'),
                'first_name': row.get('First Name'),
                'last_name': row.get('Last Name'),
                'date_pre': row.get('Date_PRE'),
                'format': row.get('Format'),
                'validator': row.get('Validator'),
                'diagnosis': row.get('Diagnosis', ''),
                # Key parameters for quick view
                'fev1_pre': row.get('FEV1_PRE'),
                'fvc_pre': row.get('FVC_PRE'),
                'fev1_fvc_pre': row.get('FEV 1 % FVC_PRE')
            }
            tests.append(test_data)
        
        tests.sort(key=lambda x: x.get('date_pre', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'tests': tests,
            'total_tests': len(tests),
            'date_range': f"{start_date} to {end_date}"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error searching by date range: {str(e)}'
        }), 500

@app.route('/diagnosis/save', methods=['POST'])
@require_auth
def save_diagnosis():
    """Save physician's confirmed diagnosis"""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        test_date = data.get('test_date')
        diagnosis = data.get('diagnosis')
        severity = data.get('severity', '')
        
        if not all([patient_id, test_date, diagnosis]):
            return jsonify({
                'success': False,
                'error': 'patient_id, test_date, and diagnosis are required'
            }), 400
        
        df = read_database()
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': 'Database not found'
            }), 404
        
        # Find the specific test
        mask = (df['ID'].astype(str) == str(patient_id)) & (df['Date_PRE'] == test_date)
        matching_tests = df[mask]
        
        if matching_tests.empty:
            return jsonify({
                'success': False,
                'error': f'Test not found for patient {patient_id} on {test_date}'
            }), 404
        
        # Update diagnosis
        df.loc[mask, 'Diagnosis'] = diagnosis
        if severity:
            df.loc[mask, 'Severity'] = severity
        
        # Add timestamp
        df.loc[mask, 'Diagnosis_Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save database
        if save_database(df):
            return jsonify({
                'success': True,
                'message': 'Diagnosis saved successfully',
                'patient_id': patient_id,
                'diagnosis': diagnosis,
                'severity': severity
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save diagnosis to database'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error saving diagnosis: {str(e)}'
        }), 500

@app.route('/diagnosis/suggest', methods=['POST'])
@require_auth
def suggest_diagnosis():
    """Analyze test results and suggest obstructive pattern diagnosis"""
    try:
        data = request.get_json()
        
        fev1_fvc_ratio = data.get('fev1_fvc_ratio')
        fev1_predicted_percent = data.get('fev1_predicted_percent')
        method = data.get('method', 'murray')
        age = data.get('age')
        
        print(f"🔍 Diagnosis Analysis: ratio={fev1_fvc_ratio}, fev1%={fev1_predicted_percent}, method={method}, age={age}")
        
        suggestions = {
            'has_obstruction': False,
            'severity': None,
            'criteria_met': [],
            'method_used': method,
            'recommendations': []
        }
        
        # Check for obstruction (both methods use 0.70 threshold for now)
        if fev1_fvc_ratio and fev1_fvc_ratio < 0.70:
            suggestions['has_obstruction'] = True
            suggestions['criteria_met'].append(f'FEV1/FVC ratio: {fev1_fvc_ratio:.3f} < 0.70')
            print(f"✅ Obstruction detected: {fev1_fvc_ratio:.3f} < 0.70")
            
            # Determine severity based on FEV1 % predicted
            if fev1_predicted_percent:
                if fev1_predicted_percent >= 80:
                    suggestions['severity'] = 'mild'
                elif fev1_predicted_percent >= 50:
                    suggestions['severity'] = 'moderate'
                elif fev1_predicted_percent >= 30:
                    suggestions['severity'] = 'severe'
                else:
                    suggestions['severity'] = 'very severe'
                
                suggestions['criteria_met'].append(f'FEV1 % predicted: {fev1_predicted_percent:.1f}%')
                print(f"📊 Severity: {suggestions['severity']} (FEV1: {fev1_predicted_percent:.1f}%)")
            
            # Add recommendations
            suggestions['recommendations'].append('Consider post-bronchodilator testing if not already performed')
            suggestions['recommendations'].append('Evaluate clinical symptoms and smoking history')
            
            if age and age > 40:
                suggestions['recommendations'].append('Consider COPD diagnosis given age and obstructive pattern')
        else:
            print(f"❌ No obstruction: ratio {fev1_fvc_ratio} >= 0.70")
        
        print(f"📋 Final suggestions: {suggestions}")
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        print(f"❌ Error in diagnosis suggestion: {e}")
        return jsonify({
            'success': False,
            'error': f'Error generating diagnosis suggestions: {str(e)}'
        }), 500

@app.route('/database/patients', methods=['GET'])
@require_auth
def get_all_patients():
    """Get all unique patient IDs for search autocomplete"""
    try:
        df = read_database()
        
        if df.empty:
            return jsonify({
                'success': True,
                'patients': [],
                'message': 'No database found'
            })
        
        # Get unique patient IDs with basic info
        unique_patients = df.groupby('ID').agg({
            'First Name': 'first',
            'Last Name': 'first',
            'Date_PRE': 'max',  # Most recent test date
            'Age': 'first',
            'Sex': 'first'
        }).reset_index()
        
        patients = []
        for _, row in unique_patients.iterrows():
            patients.append({
                'id': row['ID'],
                'first_name': row.get('First Name', ''),
                'last_name': row.get('Last Name', ''),
                'last_test_date': row.get('Date_PRE'),
                'age': row.get('Age'),
                'sex': row.get('Sex')
            })
        
        return jsonify({
            'success': True,
            'patients': patients,
            'total_patients': len(patients)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting patient list: {str(e)}'
        }), 500

# ==================== RESEARCH MODULE ENDPOINTS ====================

@app.route('/research/batch-xlsx', methods=['POST'])
@require_auth
def batch_xlsx_upload():
    """Handle XLSX file upload with hospital server links"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided', 'success': False}), 400
        
        files = request.files.getlist('files')
        xlsx_files = [f for f in files if f.filename.endswith('.xlsx')]
        
        if not xlsx_files:
            return jsonify({'error': 'No XLSX files found', 'success': False}), 400
        
        results = []
        total_records = 0
        
        for file in xlsx_files:
            try:
                # Save uploaded XLSX file temporarily
                filename = secure_filename(file.filename)
                temp_path = os.path.join('temp', filename)
                os.makedirs('temp', exist_ok=True)
                file.save(temp_path)
                
                # Read XLSX file to get server links and metadata
                df = pd.read_excel(temp_path)
                
                # Mock processing - in real implementation, you'd process the server links
                file_record_count = len(df) if not df.empty else 0
                total_records += file_record_count
                
                results.append({
                    'filename': filename,
                    'records_found': file_record_count,
                    'status': 'processed',
                    'server_links_found': file_record_count  # Assuming each row has a server link
                })
                
                # Clean up temp file
                os.remove(temp_path)
                
            except Exception as e:
                results.append({
                    'filename': file.filename,
                    'records_found': 0,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'total_files_processed': len(xlsx_files),
            'total_records_found': total_records,
            'file_results': results,
            'message': f'Processed {len(xlsx_files)} XLSX files with {total_records} total records',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Batch XLSX processing failed: {str(e)}',
            'success': False
        }), 500

@app.route('/research/database/status', methods=['GET'])
@require_auth
def database_status():
    """Get current database status and statistics"""
    try:
        database_path = DATABASE_FILE_NAME
        
        if os.path.exists(database_path):
            # Read the Excel database
            df = pd.read_excel(database_path, engine='openpyxl')
            
            # Calculate statistics
            total_records = len(df)
            validated_records = len(df[df.get('Validator', '') == 'OK']) if 'Validator' in df.columns else 0
            
            # Get column information
            available_columns = list(df.columns)
            
            # File info
            file_size = os.path.getsize(database_path)
            last_modified = datetime.fromtimestamp(os.path.getmtime(database_path))
            
            return jsonify({
                'success': True,
                'database_info': {
                    'filename': DATABASE_FILE_NAME,
                    'location': 'Backend/Scripts/',
                    'file_size_mb': round(file_size / (1024*1024), 2),
                    'last_modified': last_modified.isoformat(),
                    'status': 'active'
                },
                'statistics': {
                    'total_records': total_records,
                    'validated_records': validated_records,
                    'validation_rate': round((validated_records/total_records)*100, 1) if total_records > 0 else 0,
                    'total_columns': len(available_columns)
                },
                'pipeline_info': {
                    'extraction_script': 'save_data.py',
                    'validation_script': 'verification.py',
                    'calculator_script': 'working_calculator.py'
                },
                'columns_available': available_columns[:10],  # First 10 columns
                'timestamp': datetime.now().isoformat()
            })
            
        else:
            return jsonify({
                'success': False,
                'error': 'Database file not found',
                'expected_path': database_path
            }), 404
            
    except Exception as e:
        return jsonify({
            'error': f'Database status check failed: {str(e)}',
            'success': False
        }), 500

@app.route('/research/database/export', methods=['GET'])
@require_auth
def export_database():
    """Export database in various formats"""
    try:
        export_format = request.args.get('format', 'excel')  # excel, csv, json
        
        database_path = DATABASE_FILE_NAME
        
        if not os.path.exists(database_path):
            return jsonify({'error': 'Database file not found', 'success': False}), 404
        
        df = pd.read_excel(database_path, engine='openpyxl')
        
        if export_format == 'csv':
            # Export as CSV
            output_path = 'temp/copd_data_export.csv'
            os.makedirs('temp', exist_ok=True)
            df.to_csv(output_path, index=False)
            
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f'copd_data_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mimetype='text/csv'
            )
            
        elif export_format == 'json':
            # Export as JSON
            return jsonify({
                'success': True,
                'data': df.to_dict('records'),
                'total_records': len(df),
                'export_timestamp': datetime.now().isoformat()
            })
            
        else:  # Default to excel
            return send_file(
                database_path,
                as_attachment=True,
                download_name=f'copd_data_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
    except Exception as e:
        return jsonify({
            'error': f'Database export failed: {str(e)}',
            'success': False
        }), 500

@app.route('/research/database/import', methods=['POST'])
@require_auth
def import_database():
    """Replace the database with an uploaded xlsx file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided', 'success': False}), 400
        file = request.files['file']
        if not file.filename.endswith('.xlsx'):
            return jsonify({'error': 'File must be an .xlsx file', 'success': False}), 400
        df = pd.read_excel(file, engine='openpyxl')
        df.to_excel(DATABASE_FILE_NAME, index=False, engine='openpyxl')
        return jsonify({
            'success': True,
            'message': f'Database imported successfully: {len(df)} records loaded',
            'records': len(df)
        })
    except Exception as e:
        return jsonify({'error': f'Import failed: {str(e)}', 'success': False}), 500

@app.route('/research/database/query', methods=['POST'])
@require_auth
def query_database():
    """Query database with filters"""
    try:
        data = request.get_json()
        filters = data.get('filters', {})
        limit = data.get('limit', 100)
        
        database_path = DATABASE_FILE_NAME
        
        if not os.path.exists(database_path):
            return jsonify({'error': 'Database file not found', 'success': False}), 404
        
        df = pd.read_excel(database_path, engine='openpyxl')
        
        # Apply filters
        filtered_df = df.copy()
        
        for column, filter_value in filters.items():
            if column in df.columns:
                if isinstance(filter_value, dict):
                    # Range filter
                    if 'min' in filter_value:
                        filtered_df = filtered_df[filtered_df[column] >= filter_value['min']]
                    if 'max' in filter_value:
                        filtered_df = filtered_df[filtered_df[column] <= filter_value['max']]
                else:
                    # Exact match
                    filtered_df = filtered_df[filtered_df[column] == filter_value]
        
        # Limit results
        result_df = filtered_df.head(limit)
        
        return jsonify({
            'success': True,
            'total_matches': len(filtered_df),
            'returned_records': len(result_df),
            'data': result_df.to_dict('records'),
            'applied_filters': filters,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Database query failed: {str(e)}',
            'success': False
        }), 500

# ==================== DATABASE MANAGEMENT FUNCTIONS ====================

def read_database():
    """Read the Excel database safely"""
    try:
        if os.path.exists(DATABASE_FILE_NAME):
            df = pd.read_excel(DATABASE_FILE_NAME, engine='openpyxl')
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error reading database: {e}")
        return pd.DataFrame()

def save_database(df):
    """Save DataFrame to Excel database"""
    try:
        df.to_excel(DATABASE_FILE_NAME, index=False, engine='openpyxl')
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

def get_dlcoc_field(row):
    """Determine correct DLCOc field based on format"""
    format_type = row.get('Format', '')
    
    if 'OLD' in str(format_type):
        # Check for both variations in old format
        if pd.notna(row.get('DLCOc SB_PRE')):
            return 'DLCOc SB_PRE'
        elif pd.notna(row.get('DLCO SB_PRE')):
            return 'DLCO SB_PRE'
    else:
        # New format
        if pd.notna(row.get('DLCOc_PRE')):
            return 'DLCOc_PRE'
    
    return None

# ==================== REACT STATIC FILE SERVING ====================

@app.route('/<path:path>')
def serve_react_app(path):
    """Catch-all: serve React assets or fall back to index.html for client-side routing."""
    if not os.path.isdir(REACT_BUILD):
        return jsonify({'error': 'React build not found'}), 404
    full = os.path.join(REACT_BUILD, path)
    if os.path.isfile(full):
        return send_from_directory(REACT_BUILD, path)
    return send_from_directory(REACT_BUILD, 'index.html')

# ==================== SERVER STARTUP ====================

if __name__ == '__main__':
    print("🌟 Flask server starting...")
    print(f"🔧 PDF Extractor: {'Available' if PDF_EXTRACTOR_AVAILABLE else 'Not Available'}")
    print(f"🏥 Clinical Interpreter: {'Available' if CLINICAL_INTERPRETER_AVAILABLE else 'Not Available'}")
    print("📡 Server will be available at http://localhost:5000")
    print("🏥 API Endpoints:")
    print("   GET  / - API information")
    print("   GET  /health - Health check")
    print("   POST /upload - Upload PDF for extraction" + (" ✅" if PDF_EXTRACTOR_AVAILABLE else " ❌"))
    print("   GET  /test - Test PDF extraction" + (" ✅" if PDF_EXTRACTOR_AVAILABLE else " ❌"))
    print("   POST /analyze - Clinical analysis ✅")
    print("   POST /analyze/batch - Batch analysis ✅")
    print("   POST /cleanup/old-pdfs - Clean up old files ✅")
    print("   🔍 Enhanced Search & Diagnosis:")
    print("   GET  /search/patient/<id> - Patient test history ✅")
    print("   POST /search/date-range - Date range search ✅")
    print("   POST /diagnosis/save - Save physician diagnosis ✅")
    print("   POST /diagnosis/suggest - Obstructive pattern suggestions ✅")
    print("   GET  /database/patients - All patient IDs ✅")
    print("   📊 Research Module:")
    print("   POST /research/batch-xlsx - XLSX batch processing ✅")
    print("   GET  /research/database/status - Database statistics ✅")
    print("   GET  /research/database/export - Export database ✅")
    print("   POST /research/database/query - Query with filters ✅")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)