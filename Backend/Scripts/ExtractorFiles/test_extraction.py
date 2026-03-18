import sys
import os
sys.path.append(r'C:\Users\Noadi\COPD_PulmonWebApp\Backend\Scripts\ExtractorFiles')

from pdf_extractor import get_data_from_file
pdf_path = r"C:\Users\Noadi\COPD_PulmonWebApp\Backend\Scripts\ExtractorFiles\uploads\20251224_110021_old_full_8.pdf"
print("Exists?", os.path.exists(pdf_path), pdf_path)
data = get_data_from_file(pdf_path)

print("Extracted fields:")
for key, value in data.items():
    if any(field in key for field in ['RV', 'TLC', 'DLCO', 'DLCOc']):
        print(f"{key}: {value}")