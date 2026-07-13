# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

PulmonApp — a COPD spirometry diagnostic web app for Tel Aviv Sourasky Medical Center. It extracts spirometry values from scanned PDF reports via OCR, then compares Murray (traditional) vs GLI 2012 reference equations to produce clinical interpretations.

---

## Commands

### Frontend
```bash
cd Frontend
npm install
npm run dev      # Dev server → http://localhost:5173
npm run build    # Production build → dist/
```

### Backend
```bash
# Local dev (from Backend/Scripts/ExtractorFiles/)
python web_backend.py

# Production (matches Dockerfile)
gunicorn --chdir Backend/Scripts/ExtractorFiles web_backend:app \
  --bind 0.0.0.0:10000 --timeout 300 --workers 1
```

### Tests
```bash
# Backend only — no frontend test suite
cd Backend/Scripts/ExtractorFiles
python test_complete_pft_interpretation.py
python test_extraction.py
```

---

## Architecture

### Request flow for a single PDF analysis
1. Frontend (`ClinicalAnalysisModule.tsx`) POSTs the PDF via `authFetch` to `/analyze`
2. `web_backend.py` saves the file to `uploads/`, calls `get_data_from_file(pdf_path)` from `pdf_extractor.py`
3. `pdf_extractor.py` converts PDF pages to JPEGs (poppler), runs tesseract OCR at multiple threshold levels, picks the threshold that matches the most expected fields
4. Extracted dict goes back to `web_backend.py`, which runs `MurrayCalculator` + `WorkingGLI2012Calculator` then `perform_clinical_interpretation()`
5. JSON response → `EnhancedAnalysisResults.tsx` → tabbed display

### PDF format detection
`pdf_extractor.py` supports three PDF layouts (OLD / NEW / THIRD) defined in `consts.py::FORMATS`. On every upload, `separate_new_from_old_format()` runs a fast tesseract pass at threshold=150 to detect which format identifiers appear, then routes the full OCR pass to the matching threshold/iteration settings.

### OCR pipeline
Only pytesseract is used (EasyOCR/PyTorch was removed to fit Render's memory limits). Both format-detection and full-analysis passes use `tesseract_get_recognized_text()` with a binary-threshold loop. The loop runs `num_of_thresholds` iterations starting at `base_threshold_level+1`, stepping by 3, and keeps whichever threshold extracted the most fields.

### Auth
JWT-based, stateless. Backend: `require_auth` decorator reads `Authorization: Bearer <token>` header; `/auth/login` verifies bcrypt hash and issues a 24h token. Frontend: `authFetch.ts` wraps every `fetch` call to inject the token from `localStorage['auth_token']`. Credentials come from env vars `AUTH_USERNAME`, `AUTH_PASSWORD_HASH`, `JWT_SECRET`.

### Key backend modules (`Backend/Scripts/ExtractorFiles/`)
| File | Role |
|---|---|
| `web_backend.py` | Flask app, all endpoints, clinical pipeline orchestration |
| `working_calculator.py` | GLI 2012 spline interpolation + Murray reference equations |
| `pdf_extractor.py` | PDF→JPEG→OCR→dict extraction |
| `consts.py` | `FORMATS` class (plain class, not Enum), all regex patterns, field lists |
| `save_data.py` | Appends verified rows to the Excel database |
| `verification.py` | Post-extraction field validation |

### Frontend structure (`Frontend/src/`)
- `App.tsx` — auth gate: shows `LoginPage` or `Dashboard` based on localStorage token
- `components/Dashboard.tsx` — top nav + routes to clinical or research view
- `components/Clinical_Module/` — single PDF upload, search, diagnosis flow
- `components/ResearchModule.tsx` — batch XLSX processing, DB import/export
- `components/shared/` — `SearchPanel`, `BatchUploadSection`, `BatchResultsTable`, `SearchResultsTable`
- `components/ViewPDF.tsx` — handles errors internally; do not pass `error` or `onRetry` props
- `utils/authFetch.ts` — token-aware fetch; skips `Content-Type` header for `FormData`

### Vite proxy (dev only)
`vite.config.ts` proxies `/analyze`, `/upload`, `/search`, `/diagnosis`, `/research`, `/health`, `/api`, `/cleanup`, `/database` → `http://localhost:5000`.

---

## Deployment (Render)

- Docker service (`render.yaml`, `env: docker`)
- Build installs tesseract-ocr + poppler-utils via apt, builds the React frontend, then installs Python deps
- Single gunicorn worker, 300s timeout — do not increase workers (memory constraint)
- Env vars required at runtime: `AUTH_USERNAME`, `AUTH_PASSWORD_HASH`, `JWT_SECRET`, `FLASK_ENV`, `FLASK_DEBUG`

### `FORMATS` class note
`consts.py` uses `class FORMATS` as a plain class (not `Enum`) containing inner `class OLD(Enum)`, `class NEW(Enum)`, `class THIRD(Enum)`. This is intentional — Python 3.11 breaks nested Enum-inside-Enum.

---

## Known constraints
- `web_backend.py` does `sys.path.insert(0, ...)` at the top so relative imports work under gunicorn `--chdir`
- The Excel database (`copd_extracted_data_trial.xlsx`) is the only persistence layer; it lives in `Backend/Scripts/ExtractorFiles/`
- `process_file()` in `pdf_extractor.py` returns the string `"Bad!"` on parse failure — callers must check `isinstance(extracted_data, dict)` before calling `.get()`
