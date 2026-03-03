from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from pdf_extractor import get_data_from_file
from enum import Enum
from flask_cors import CORS
from consts import FORMATS


app = Flask(__name__)
CORS(app)

# Configure the upload folder (optional)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/file_upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        processing_result = get_data_from_file(filepath)
        processing_result["Format"] = processing_result["Format"].name
        return jsonify({'message': 'File uploaded and processed successfully', 'result': processing_result}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Run the Flask development server