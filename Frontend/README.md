# [PolmunApp] — Pulmonary Spirometry Analysis Platform

> A clinical-grade web application for spirometry interpretation, built for the Pulmonary Institute at Tel Aviv Sourasky Medical Center. Compares Murray (traditional) and GLI 2012 reference equations side-by-side to support evidence-based COPD diagnosis.

---

## Key Features

| Feature | Description |
|---|---|
| **Dual-Method Comparison** | Side-by-side Murray vs GLI 2012 spirometry analysis with LLN-based range indicators |
| **ERS/ATS 2022 Algorithm** | Full Figure 8 decision-path logic with transparent step-by-step interpretation |
| **Batch PDF Processing** | Upload up to 5 spirometry PDFs at once; per-patient tab view with integrated PDF viewer |
| **Clinical Interpretation** | Severity classification, next clinical action, and physician notes with quick-insert chips |
| **Research Module** | XLSX batch processing, population statistics, and live database export (Excel / CSV / JSON) |
| **Patient Search** | Look up test history by patient ID or date range |
| **Responsive Design** | Desktop-first layout with fluid grid; works across modern browsers |
| **Accessible UI** | `:focus-visible` ring, sufficient contrast ratios, keyboard-navigable controls |
| **Optimized Performance** | Vite-bundled, lazy PDF rendering via `react-pdf` + `pdfjs-dist` web worker |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | React 18 + TypeScript |
| Build Tool | Vite 5 |
| Styling | Tailwind CSS 4 |
| Icons | Lucide React |
| PDF Rendering | react-pdf 10 / pdfjs-dist 5 |
| HTTP | Fetch API (native) |
| Backend | Flask 3 (Python) — separate service on `:5000` |
| Data | Axios, PapaParse, SheetJS (xlsx) |
| Linting | ESLint + eslint-plugin-react-hooks |

---

## Getting Started

### Prerequisites

- Node.js **18+**
- npm **9+**
- The Flask backend running on `http://localhost:5000` (see `Backend/Scripts/ExtractorFiles/`)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd COPD_PulmonWebApp/Frontend

# Install dependencies
npm install
```

### Development

```bash
npm run dev
```

The app starts at **`http://localhost:5173`** with Hot Module Replacement enabled.

### Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start development server with HMR |
| `npm run build` | Compile and bundle for production |
| `npm run preview` | Preview the production build locally |

---

## Project Structure

```
Frontend/
├── public/
│   └── images/               # Static assets (logos, GIFs)
├── src/
│   ├── App.tsx               # Root component
│   ├── App.css               # Global styles + Tailwind directives
│   ├── main.tsx              # Entry point
│   └── components/
│       ├── Dashboard.tsx     # Navigation + module routing
│       ├── ViewPDF.tsx       # PDF viewer (zoom, rotate, fullscreen)
│       ├── ResearchModule.tsx
│       ├── Clinical_Module/
│       │   ├── ClinicalAnalysisModule.tsx   # Single + batch PDF analysis
│       │   ├── EnhancedAnalysisResults.tsx  # 10-section results layout
│       │   ├── DiagnosisModal.tsx
│       │   └── tabs/                        # ERS2022, Traditional, Method Comparison
│       └── shared/
│           ├── SearchPanel.tsx
│           ├── SearchResultsTable.tsx
│           ├── BatchUploadSection.tsx
│           └── BatchResultsTable.tsx
├── package.json
├── vite.config.ts
├── tailwind_config.js
└── tsconfig.app.json
```

---

## Styling Guide

### Root Scale

```css
/* App.css */
html { font-size: 17px; }
```

A **17px base** was chosen deliberately for clinical readability. Spirometry reports are data-dense — physicians scan multiple numeric values under time pressure. Slightly larger base text reduces eye strain and lowers the risk of misreading critical values (e.g., FEV1/FVC ratios).

### Typography Overrides

Tailwind's default scale is boosted ~15% above defaults to compensate for the 17px root:

```css
.text-xs   { font-size: 0.78rem; }   /* ~13 px */
.text-sm   { font-size: 0.90rem; }   /* ~15 px */
.text-base { font-size: 1.05rem; }   /* ~18 px */
.text-lg   { font-size: 1.20rem; }   /* ~20 px */
.text-xl   { font-size: 1.40rem; }   /* ~24 px */
```

### Design Tokens

| Role | Class |
|---|---|
| Card | `bg-white border border-slate-200 rounded-xl shadow-sm` |
| Section header | `text-xs font-bold uppercase tracking-wider text-slate-500` |
| Primary action | `bg-blue-600 text-white rounded-xl px-4 py-2.5 font-semibold` |
| Danger / COPD | `bg-red-100 text-red-800 border-red-200 rounded-full` |
| Normal | `bg-emerald-100 text-emerald-800 border-emerald-200 rounded-full` |
| Borderline | `bg-amber-100 text-amber-800 border-amber-200 rounded-full` |

### Accessibility

- Focus rings use `:focus-visible` with a `2px solid #3b82f6` outline — visible to keyboard users, invisible on mouse click.
- Custom scrollbar: 6px width, `#cbd5e1` thumb — subtle but present.
- All icon-only buttons carry `title` attributes for screen readers.

---

## Backend API Reference

The frontend expects a Flask server at `http://localhost:5000`. Key endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/analyze` | Single PDF spirometry analysis |
| `POST` | `/analyze/batch` | Multi-PDF batch analysis (max 5) |
| `GET` | `/api/pdf/<filename>` | Serve stored PDF for viewing |
| `GET` | `/search/patient/<id>` | Patient test history |
| `POST` | `/search/date-range` | Tests within a date range |
| `POST` | `/diagnosis/suggest` | COPD severity suggestion |
| `POST` | `/diagnosis/save` | Save physician diagnosis |
| `POST` | `/research/batch-xlsx` | Batch XLSX hospital data processing |
| `GET` | `/research/database/status` | Database statistics |
| `GET` | `/research/database/export` | Export DB (`?format=excel\|csv\|json`) |

---

## Deployment

The app deploys as a **single unified service** on Render — Flask serves both the API and the pre-built React frontend.

### Architecture

```
Render Web Service (Python/Flask)
  ├── API routes  → /analyze, /health, /search/*, etc.
  └── Everything else → serves Frontend/dist/index.html
```

### Prerequisites on Render

The `render.yaml` at the repo root defines the full service. It:
1. Installs `tesseract-ocr` and `poppler-utils` (system PDF/OCR dependencies)
2. Builds the React frontend (`npm run build`)
3. Installs Python dependencies
4. Starts gunicorn pointing at the Flask app

### Deploy Steps

1. Push the repository to GitHub.
2. In [Render Dashboard](https://dashboard.render.com/), create a **New Web Service**.
3. Connect the GitHub repository — Render will detect `render.yaml` automatically.
4. Click **Deploy**. The full build takes ~3–5 minutes on first run.
5. Visit the service URL — the React app should load.

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `VITE_API_URL` | No | `''` (empty) | Override API base URL. Leave empty — relative URLs work when Flask serves both. |
| `TESSERACT_PATH` | No | `tesseract` | Path to Tesseract binary (auto-found in PATH on Render after apt install). |
| `POPPLER_PATH` | No | `None` (PATH) | Path to Poppler binaries (auto-found after apt install). |
| `DATA_DIR` | No | `../Data` (relative) | Path to `lookuptables.xlsx`. Defaults to `Backend/Scripts/Data/` relative to the Flask file. |
| `FLASK_DEBUG` | No | `0` | Set to `1` only in development. |

### Persistent Storage

Render's filesystem is ephemeral. The `render.yaml` attaches a 1 GB disk at:

```
/opt/render/project/src/Backend/Scripts/ExtractorFiles
```

This keeps `uploads/` and `copd_extracted_data_trial.xlsx` intact across deploys.

> **Important:** `Backend/Scripts/Data/lookuptables.xlsx` contains the GLI 2012 L/M/S spline tables required for clinical calculations. This file must be committed to git (it is not sensitive — it is published reference data).

### Local Development

No environment variables needed — the Vite dev proxy forwards API calls to Flask automatically:

```bash
# Terminal 1 — Flask backend
cd Backend/Scripts/ExtractorFiles
python web_backend.py          # http://localhost:5000

# Terminal 2 — Vite dev server
cd Frontend
npm run dev                    # http://localhost:5173, proxies /analyze etc. → :5000
```

### Manual Production Build

```bash
cd Frontend && npm run build   # writes to Frontend/dist/
cd ../Backend/Scripts/ExtractorFiles
python web_backend.py          # visit http://localhost:5000 → React app loads
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `''` | Override API base URL. Empty = relative URLs (correct for production). |

> `.env.local` is git-ignored by default. Only needed if you want to point to a remote backend in dev.

---

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit your changes following conventional commits: `feat:`, `fix:`, `chore:`
3. Open a pull request against `main`
4. Ensure `npx tsc --noEmit` passes before submitting

---

## License

MIT © Tel Aviv Sourasky Medical Center — Pulmonary Institute
