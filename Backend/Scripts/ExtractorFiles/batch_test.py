import os
import sys
import csv
import argparse
from datetime import datetime

# Add the current directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


# TODO: hardcoded path — set POPPLER_PATH in deployment env instead. # Fallback paths for local dev if not set in .env
os.environ.setdefault('POPPLER_PATH', r'C:\Users\Noadi\Poppler\Library\bin')
os.environ.setdefault('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')

from pdf_extractor import get_data_from_file


def run_batch_test(pdf_folder, output_csv=None, format_filter=None):
    """
    format_filter: None = all files, 'old' = only old format PDFs, 'new' = only new format PDFs
    Filter is applied by filename — expects files to have 'old' or 'new' in their name.
    """
    all_pdfs = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]

    if format_filter == 'old':
        pdf_files = [f for f in all_pdfs if 'old' in f.lower()]
        print(f"Running OLD FORMAT batch ({len(pdf_files)} files)")
    elif format_filter == 'new':
        pdf_files = [f for f in all_pdfs if 'new' in f.lower()]
        print(f"Running NEW FORMAT batch ({len(pdf_files)} files)")
    else:
        pdf_files = all_pdfs
        print(f"Running ALL FORMATS batch ({len(pdf_files)} files)")

    pdf_files.sort()

    if output_csv is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = f"_{format_filter}" if format_filter else "_all"
         # TODO: hardcoded absolute path — make relative before hospital deployment / moving the project.
        # Portable version: output_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = r"C:\Users\Noadi\COPD_PulmonWebApp\Backend\Scripts"
        output_csv = os.path.join(output_dir, f"batch_test_results{suffix}_{timestamp}.csv")
        
    print(f"Results will be saved to: {output_csv}\n")

    fieldnames = [
        'filename', 'format', 'patient_id', 'age', 'sex', 'height',
        'fvc_pred', 'fvc_pre', 'fvc_ok',
        'fev1_pred', 'fev1_pre', 'fev1_ok',
        'ratio_pre', 'ratio_ok',
        'tlc_pred', 'tlc_pre', 'tlc_ok',
        'rv_pred', 'rv_pre', 'rv_ok',
        'dlco_pred', 'dlco_pre', 'dlco_ok',
        'validator', 'missing', 'error'
    ]

    results = []

    for i, filename in enumerate(pdf_files):
        pdf_path = os.path.join(pdf_folder, filename)
        print(f"[{i+1}/{len(pdf_files)}] Processing {filename}...")

        row = {k: '' for k in fieldnames}
        row['filename'] = filename

        try:
            data = get_data_from_file(pdf_path)

            row['format']     = data.get('Format', '')
            row['patient_id'] = data.get('ID', '')
            row['age']        = data.get('Age', '')
            row['sex']        = data.get('Sex', '')
            row['height']     = data.get('Height', '')

            row['fvc_pred']   = data.get('FVC_PRED', '')
            row['fvc_pre']    = data.get('FVC_PRE', '')
            row['fvc_ok']     = 'Y' if data.get('FVC_PRE') else 'N'

            row['fev1_pred']  = data.get('FEV1_PRED', '')
            row['fev1_pre']   = data.get('FEV1_PRE', '')
            row['fev1_ok']    = 'Y' if data.get('FEV1_PRE') else 'N'

            row['ratio_pre']  = data.get('FEV 1 % FVC_PRE', '')
            row['ratio_ok']   = 'Y' if data.get('FEV 1 % FVC_PRE') else 'N'

            row['tlc_pred']   = data.get('TLC_PRED', '')
            row['tlc_pre']    = data.get('TLC_PRE', '')
            row['tlc_ok']     = 'Y' if data.get('TLC_PRE') else 'N'

            row['rv_pred']    = data.get('RV_PRED', '')
            row['rv_pre']     = data.get('RV_PRE', '')
            row['rv_ok']      = 'Y' if data.get('RV_PRE') else 'N'

            row['dlco_pred']  = data.get('DLCOc_PRED', '')
            row['dlco_pre']   = data.get('DLCOc_PRE', '')
            row['dlco_ok']    = 'Y' if data.get('DLCOc_PRE') else 'N'

            row['validator']  = data.get('Validator', '')
            row['missing']    = data.get('Missing', '')

            fvc_ok   = 1 if data.get('FVC_PRE') else 0
            fev1_ok  = 1 if data.get('FEV1_PRE') else 0
            ratio_ok = 1 if data.get('FEV 1 % FVC_PRE') else 0
            score = (fvc_ok + fev1_ok + ratio_ok) / 3 * 100
            print(f"    Format: {row['format']} | FVC: {row['fvc_ok']} | FEV1: {row['fev1_ok']} | Ratio: {row['ratio_ok']} | TLC: {row['tlc_ok']} | Score: {score:.0f}%")

        except Exception as e:
            row['error'] = str(e)
            print(f"    ERROR: {e}")

        results.append(row)

    # Write CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print summary
    total = len(results)
    if total == 0:
        print("No files processed.")
        return

    fvc_ok   = sum(1 for r in results if r.get('fvc_ok') == 'Y')
    fev1_ok  = sum(1 for r in results if r.get('fev1_ok') == 'Y')
    ratio_ok = sum(1 for r in results if r.get('ratio_ok') == 'Y')
    tlc_ok   = sum(1 for r in results if r.get('tlc_ok') == 'Y')
    dlco_ok  = sum(1 for r in results if r.get('dlco_ok') == 'Y')
    errors   = sum(1 for r in results if r.get('error'))

    print(f"\n{'='*50}")
    print(f"BATCH TEST SUMMARY — {total} files")
    print(f"{'='*50}")
    print(f"FVC extracted:   {fvc_ok}/{total} ({fvc_ok/total*100:.0f}%)")
    print(f"FEV1 extracted:  {fev1_ok}/{total} ({fev1_ok/total*100:.0f}%)")
    print(f"Ratio extracted: {ratio_ok}/{total} ({ratio_ok/total*100:.0f}%)")
    print(f"TLC extracted:   {tlc_ok}/{total} ({tlc_ok/total*100:.0f}%)")
    print(f"DLCO extracted:  {dlco_ok}/{total} ({dlco_ok/total*100:.0f}%)")
    print(f"Errors:          {errors}/{total}")
    print(f"\nResults saved to: {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Batch test PDF extraction')
    parser.add_argument('--format', choices=['old', 'new', 'all'], default='all',
                        help='Filter PDFs by format: old, new, or all (default)')
    parser.add_argument('--folder', default=r"C:\Users\Noadi\COPD_PulmonWebApp\Backend\Scripts\Data\PDF",
                    # TODO: hardcoded path — make relative/configurable before deployment
                    help='Path to folder containing test PDFs')
    parser.add_argument('--output', default=None,
                        help='Output CSV filename (optional)')
    args = parser.parse_args()

    format_filter = None if args.format == 'all' else args.format
    run_batch_test(args.folder, args.output, format_filter)
