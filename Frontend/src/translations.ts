// ─── UI Translations ──────────────────────────────────────────────────────────
// All values are English placeholders. Replace each string with its Hebrew equivalent.
// Function entries handle dynamic strings with interpolated values.

export const t = {

  // ── App-wide ────────────────────────────────────────────────────────────────
  appTitle:           'PulmonApp',
  institutionName:    'Tel Aviv Sourasky Medical Center',
  institutionBadge:   'Pulmonary Institute · Tel Aviv Sourasky Medical Center',

  // ── LoginPage ───────────────────────────────────────────────────────────────
  signIn:             'Sign in',
  signingIn:          'Signing in…',
  username:           'Username',
  password:           'Password',
  loginFailed:        'Login failed',
  serverUnreachable:  'Unable to reach server',

  // ── Dashboard / Navigation ──────────────────────────────────────────────────
  homeNavButton:          '← Home',
  breadcrumbSpirometry:   'Spirometry Analysis',
  breadcrumbResearch:     'Research Module',
  disclaimerText:         'Decision-support tool only — all results require physician verification before clinical use.',
  homePageSubtitle:       'Spirometry analysis and research platform for pulmonary function testing using Murray and GLI 2012 reference equations.',

  // Module cards
  clinicalTitle:  'Spirometry Analysis',
  clinicalDesc:   'Upload individual or batch spirometry PDFs for automated analysis comparing Murray vs GLI 2012 reference equations with ERS/ATS 2022 interpretation.',
  clinicalCap1:   'Single and batch PDF upload',
  clinicalCap2:   'ERS/ATS 2022 + Traditional GOLD interpretation',
  clinicalCap3:   'Bronchodilator response assessment',
  clinicalCap4:   'Side-by-side method comparison',
  clinicalButton: 'Open Spirometry Analysis',

  researchTitle:  'Research Module',
  researchDesc:   'Batch process XLSX datasets from the hospital server, run population-level analyses, and manage the spirometry database.',
  researchCap1:   'XLSX batch processing',
  researchCap2:   'Hospital server data extraction',
  researchCap3:   'Population demographics & COPD rates',
  researchCap4:   'Database export and management',
  researchButton: 'Open Research Tools',

  // ── ClinicalAnalysisModule ──────────────────────────────────────────────────
  singlePdf:          'Single PDF',
  batch:              'Batch',
  clickToSelectPdf:   'Click to select a spirometry PDF…',
  ready:              '✓ Ready',
  reference:          'Reference:',
  murray:             'Murray',
  gli:                'GLI 2012',
  compare:            'Compare',
  analyzeSpirometry:  'Analyze Spirometry',
  processingBtn:      'Processing…',
  analysisComplete:   'Analysis complete!',
  analysisFailed:     'Analysis failed',
  batchFailed:        'Batch analysis failed',
  selectPdfFirst:     'Please select a PDF file to analyze.',
  spirometryReport:   'Spirometry Report',
  diagnosisConfirmed: 'Diagnosis confirmed and saved successfully',
  diagnosisError:     'Error saving diagnosis',
  customDiagnosisSaved: 'Custom diagnosis saved successfully',
  elapsed:            'elapsed',

  // ── ResearchModule ──────────────────────────────────────────────────────────
  researchModuleTitle:    'Research Module',
  researchModuleSubtitle: 'Batch processing, population analysis, and database management for hospital spirometry data.',

  tabBatchProcessing:   'Batch Processing',
  tabPopulationStudies: 'Population Studies',
  tabDatabase:          'Database',

  xlsxUploadTitle:    'XLSX Batch Upload',
  xlsxUploadSubtitle: 'Upload files containing hospital server links',
  clickToUploadXlsx:  'Click to upload XLSX files with server links',
  xlsxRecordsHint:    'Each file may contain up to 2000 hospital records',

  hospitalExtractionTitle:    'Hospital Server Extraction',
  hospitalExtractionSubtitle: 'Extract tests by time period',
  startDate:      'Start Date',
  endDate:        'End Date',
  extractionHint: 'Tests are fetched from the hospital server by time period. PDF download is fast; OCR data extraction takes longer depending on volume.',

  selectXlsxOrDate:       'Please select XLSX files or set a date range.',
  startBatchProcessing:   'Start Batch Processing',
  processingHospitalData: 'Processing Hospital Data…',
  processingResults:      'Processing Results',
  newAnalysis:            '← New Analysis',
  extractionSummary:      'Extraction Summary',
  fileResults:            'File Results',
  filesProcessed:         'Files Processed',
  recordsFound:           'Records Found',
  successful:             'Successful',
  failed:                 'Failed',

  colFile:        'File',
  colStatus:      'Status',
  colRecords:     'Records',
  colServerLinks: 'Server Links',
  statusOk:       'OK',
  statusFailed:   'Failed',

  downloadReport:     'Download Report',
  exportToExcel:      'Export to Excel',
  exportToCsv:        'Export to CSV',
  importDatabase:     'Import Database',
  importing:          'Importing…',
  viewRecords:        'View Records',
  filterRecords:      'Filter Records',
  validationSettings: 'Validation Settings',

  // Population studies
  popStudiesTitle:    'Population Studies',
  popStudiesSubtitle: 'Analysis tools for population-level research',
  comingSoon:         'Coming soon',
  studyAge:           'Age-Stratified Analysis',
  studyAgeDesc:       'Compare diagnostic method performance across age groups to identify age-related biases.',
  studySex:           'Sex-Based Comparison',
  studySexDesc:       'Analyze differences in diagnostic accuracy between male and female populations.',
  studySeverity:      'Severity Distribution',
  studySeverityDesc:  'Examine COPD severity classifications using different reference equations.',
  studyLongitudinal:  'Longitudinal Tracking',
  studyLongitudinalDesc: 'Track patient spirometry changes over time using consistent reference standards.',

  // Database
  databaseStatus:          'Database Status',
  activeStatus:            'Active',
  totalRecords:            'Total Records',
  validated:               'Validated',
  validationRate:          'Validation Rate',
  columns:                 'Columns',
  backendDirectory:        'Backend/Scripts/ directory',
  processingPipelineTitle: 'Processing Pipeline',
  processingPipelineDesc:  'PDF Extraction → OCR Processing → Data Validation → Excel Database (save_data.py)',
  importSuccess:           'Import successful',
  importRequestFailed:     'Import request failed',

  // ── SearchPanel ─────────────────────────────────────────────────────────────
  searchPatientRecords: 'Search Patient Records',
  patientId:            'Patient ID',
  dateRange:            'Date Range',
  enterPatientId:       'Enter Patient ID (numerical)',
  search:               'Search',
  searching:            'Searching…',
  dateTo:               'to',
  noRecordsPatient:     'No records found for this patient ID.',
  noRecordsDate:        'No records found in this date range.',
  networkError:         'Unable to connect to server.',

  // ── SearchResultsTable ──────────────────────────────────────────────────────
  searchResults: 'Search Results',
  colPatientId:  'Patient ID',
  colDate:       'Date',
  colFev1:       'FEV1',
  colFvc:        'FVC',
  colRatio:      'FEV1/FVC',
  colDiagnosis:  'Diagnosis',

  // ── BatchUploadSection ──────────────────────────────────────────────────────
  pdfOnly:        'Please select only PDF files.',
  selectAtLeastOne: 'Please select at least one PDF.',

  dragDropOrClick: (max: number) => `Drag & drop or click to add PDFs (max ${max})`,
  limitReached:    (max: number) => `${max}/${max} files — limit reached`,
  filesProgress:   (current: number, max: number) => `${current}/${max} — add more`,
  maxFilesError:   (max: number, selected: number) => `Maximum ${max} files allowed. You have ${selected} selected.`,
  analyzeFiles:    (n: number) => `Analyze ${n || ''} File${n !== 1 ? 's' : ''}`,
  processingFiles: (n: number) => `Processing ${n} file${n !== 1 ? 's' : ''}…`,

  // ── BatchResultsTable ───────────────────────────────────────────────────────
  batchSummary: 'Batch Summary',
  total:        'Total',
  copd:         'COPD',
  borderline:   'Borderline',
  colPatient:   'Patient',
  colFev1Fvc:   'FEV1/FVC',
  colSeverity:  'Severity',
  colAction:    'Action',
  viewResult:   'View →',
  generated:    'Generated',

  // ── EnhancedAnalysisResults ─────────────────────────────────────────────────
  extractionWarnings:    'Extraction Warnings — verify values before proceeding',
  verifyBeforeAccepting: 'Verify before accepting results',

  // Patient bar
  patientLabel: 'Patient',
  ageLabel:     'Age',
  yrUnit:       'yr',
  sexLabel:     'Sex',
  htLabel:      'Ht',
  cmUnit:       'cm',
  lUnit:        'L',

  clinicalInterpretationLabel: 'Clinical Interpretation — ERS/ATS 2022',
  methodsAgree:    'Methods agree',
  methodsDisagree: 'Methods disagree',
  traditionalGold: 'Traditional GOLD:',
  tlcRequired:     'TLC measurement required — spirometry alone cannot confirm restriction.',

  // Evidence panel
  evidenceTitle: 'Evidence — Measured Values',
  colParam:      'Param',
  colMeasured:   'Measured',
  colGliPred:    'GLI Pred',
  colGliLln:     'GLI LLN',
  colPctPred:    '% Pred',
  colZScore:     'Z-score',
  colRange:      'Range',
  normalStatus:  'Normal',
  belowLln:      'Below LLN',

  // Bronchodilator
  bronchodilatorTitle: 'Bronchodilator Response',
  significant:         'Significant',
  notSignificant:      'Not significant',
  colPreBd:            'Pre-BD',
  colPostBd:           'Post-BD',
  colDeltaMl:          'Δ mL',
  colDeltaPctPred:     'Δ % pred',
  colCriterion:        'Criterion',
  bdThreshold:         '✓ ≥150 mL + ≥10%',
  bdBelowThreshold:    'below threshold',

  // Collapsible sections
  derivationTitle: 'How this result was derived',
  nextStepTitle:   'Recommended Next Step',
  insertToNotes:   '+ Notes',

  // Method comparison
  methodComparisonTitle: 'Method Comparison',
  ersGliLabel:           'ERS/ATS 2022 (GLI)',
  goldMurrayLabel:       'Traditional GOLD (Murray)',
  severityLabel:         'Severity:',

  // Physician notes
  physicianNotesTitle:     'Physician Notes',
  copy:                    'Copy',
  copied:                  'Copied',
  quickInsert:             'Quick insert',
  selectFindings:          'Select findings to populate note',
  noteTextareaPlaceholder: 'Select criteria above or use quick insert, or type directly...',
  downloadReportBtn:       'Download Report',
  addToResearchDb:         'Add to Research DB',

  // Guideline traceability
  guidelineTraceability: 'Guideline Traceability',
  ersAtsMethod:          'ERS/ATS 2022 Method',
  goldMethod:            'Traditional GOLD Method',
  ethnicEquityNote:      'Ethnic equity note: GLI 2012 equations were derived primarily from European/Caucasian populations. For non-European patients, consider GLI 2021 equations with broader ethnic coverage where available.',

  // Quick phrases (appear in physician notes)
  qp1: 'Spirometry within normal limits',
  qp2: 'Suspected restrictive pattern — TLC recommended',
  qp3: 'Obstructive ventilatory defect confirmed',
  qp4: 'Significant bronchodilator response',
  qp5: 'No significant bronchodilator response',
  qp6: 'Correlate clinically',
  qp7: 'Repeat spirometry recommended',

  // Generated note format
  noteMeasuredValues: 'Measured Values:',
  noteClinicalFindings: 'Clinical Findings:',
  noteNotes:            'Notes:',
  noteBasedOn:          'Based on: ERS/ATS 2022 | GLI 2012 Reference Equations',
  noteReportTitle:      (date: string) => `Spirometry Report — ${date}`,
  noteInterpretation:   (pattern: string) => `Interpretation (ERS/ATS 2022): ${pattern}`,
  noteSeverity:         (s: string) => `Severity: ${s}`,
  noteTraditional:      (pattern: string) => `Traditional (GOLD): ${pattern}`,
  noteRecommendation:   (text: string) => `Recommendation: ${text}`,

  // ── DiagnosticCriteriaButtons ────────────────────────────────────────────────
  dcTitle: 'בחירת קריטריונים אבחנתיים',

  dcRestrictiveTitle:    'דפוסים מגבילים',
  dcObstructiveTitle:    'דפוסים חסימתיים',
  dcBronchodilatorTitle: 'תגובה לברונכודיל',
  dcLungVolumesTitle:    'נפחי ריאות',
  dcAirTrappingTitle:    'לכידת אוויר',
  dcDiffusionTitle:      'יכולת דיפוזיה (DLCO / KCO)',
  dcDlcoCorrectionTitle: 'תיקון DLCO לנפח מכתשי',

  dcRestOpt1: 'ללא פגיעה מגבילה',
  dcRestOpt2: 'פגיעה מגבילה קלה',
  dcRestOpt3: 'פגיעה מגבילה בינונית',
  dcRestOpt4: 'פגיעה מגבילה קשה',

  dcObstOpt1: 'ללא פגיעה חסימתית',
  dcObstOpt2: 'פגיעה חסימתית קלה',
  dcObstOpt3: 'פגיעה חסימתית בינונית',
  dcObstOpt4: 'פגיעה חסימתית בינונית–קשה',
  dcObstOpt5: 'פגיעה חסימתית קשה',
  dcObstOpt6: 'פגיעה חסימתית קשה מאוד',

  dcBdOpt1: 'ללא תגובה משמעותית לברונכודיל',
  dcBdOpt2: 'תגובה חלקית לברונכודיל',
  dcBdOpt3: 'תגובה משמעותית (חיובית) לברונכודיל',
  dcBdOpt4: 'ברונכודיל לא ניתן',

  dcLvOpt1: 'נפחי ריאות בגדר הנורמה',
  dcLvOpt2: 'נפחי ריאות מופחתים; מומלצת פלתיסמוגרפיה',

  dcAtOpt1: 'ללא לכידת אוויר',
  dcAtOpt2: 'קיימת לכידת אוויר',
  dcAtOpt3: 'לכידת אוויר קשה',

  dcDfOpt1: 'יכולת דיפוזיה שמורה',
  dcDfOpt2: 'ירידה קלה ביכולת הדיפוזיה',
  dcDfOpt3: 'ירידה בינונית ביכולת הדיפוזיה',
  dcDfOpt4: 'ירידה קשה ביכולת הדיפוזיה',

  dcDcOpt1: 'יכולת הדיפוזיה מתנרמלת לאחר תיקון לנפח המכתשי (KCO תקין)',
  dcDcOpt2: 'שיפור חלקי ביכולת הדיפוזיה לאחר תיקון לנפח המכתשי',
  dcDcOpt3: 'ללא שיפור ביכולת הדיפוזיה לאחר תיקון לנפח המכתשי',

  // ── EnhancedAnalysisResults — criteria labels ────────────────────────────────
  criteriaRestrictive:    'דפוס מגביל',
  criteriaObstructive:    'דפוס חסימתי',
  criteriaBronchodilator: 'תגובה לברונכודיל',
  criteriaLungVolumes:    'נפחי ריאות',
  criteriaAirTrapping:    'לכידת אוויר',
  criteriaDiffusion:      'יכולת דיפוזיה (DLCO/KCO)',
  criteriaDlcoCorrection: 'תיקון DLCO לנפח מכתשי',

  // Summary lines
  summaryNormal:      'הספירומטריה בגבולות הנורמה לגיל, מין וגובה.',
  summaryNonSpecific: 'ה-FVC מופחת ביחס FEV₁/FVC תקין. נדרשת מדידת TLC להבדלת דפוס מגביל מדפוס לא-ספציפי.',
  summaryMixed:       'זוהה דפוס חסימתי-מגביל מעורב. מומלצת בדיקת ריאות מלאה.',
  summaryRestrictive: 'ייתכן פגם אוורור מגביל. נדרשת מדידת TLC לאישור.',
  summaryObstructive: 'יחס FEV₁/FVC נמוך מהגבול התחתון של הנורמה, מעיד על פגם אוורור חסימתי.',
  summaryDefault:     'מומלצת קורלציה קלינית.',

  // Next action
  nextNormal:             'אין צורך בבדיקת ספירומטריה נוספת. יש לתאם עם הסימפטומים הקלינית.',
  nextTlcRequired:        'יש למדוד נפח ריאות כולל (TLC) בפלתיסמוגרפיה גופנית או בדילול הליום לאישור או שלילת דפוס מגביל.',
  nextObstructiveNoBd:    'מומלצת בדיקת ברונכודיל, אם לא בוצעה עדיין, להערכת ההפיכות.',
  nextObstructiveWithBd:  'דפוס חסימתי מאושר. קורלציה קלינית ומעקב לפי קווים מנחים GOLD/COPD.',
  nextMixed:              'מומלצת בדיקת ריאות מלאה כולל נפחי ריאות (TLC) ויכולת דיפוזיה (DLCO).',
  nextDefault:            'מומלצת קורלציה קלינית. שקול חזרה על ספירומטריה אם הממצאים אינם עקביים.',

  // Derive steps
  deriveRatioBelow:       (ratio: string, lln: string) => `יחס FEV₁/FVC (${ratio}) נמוך מ-LLN (${lln}) — חסימה`,
  deriveRatioAbove:       (ratio: string, lln: string) => `יחס FEV₁/FVC (${ratio}) ≥ LLN (${lln}) — ללא חסימה`,
  deriveSevMild:          (pct: string) => `FEV₁ הוא ${pct}% מהצפוי — קל (FEV₁ ≥ 80%)`,
  deriveSevModerate:      (pct: string) => `FEV₁ הוא ${pct}% מהצפוי — בינוני (FEV₁ 50–79%)`,
  deriveSevSevere:        (pct: string) => `FEV₁ הוא ${pct}% מהצפוי — קשה (FEV₁ 30–49%)`,
  deriveSevVerySevere:    (pct: string) => `FEV₁ הוא ${pct}% מהצפוי — קשה מאוד (FEV₁ < 30%)`,
  deriveFvcBelowLln:      (fvc: string, lln: string) => `FVC (${fvc} L) נמוכה מ-LLN (${lln} L) — FVC מופחת עם יחס תקין`,
  deriveTlcNeeded:        'נדרשת TLC להבדיל דפוס מגביל מדפוס לא-ספציפי',
  deriveFvcNormal:        (fvc: string, lln: string) => `FVC (${fvc} L) ≥ LLN (${lln} L) — FVC תקין`,
  deriveFev1Normal:       (fev1: string, lln: string) => `FEV₁ (${fev1} L) ≥ LLN (${lln} L) — ספירומטריה תקינה מאושרת`,
  deriveFev1NonSpec:      (fvc: string, fev1: string, lln: string) => `FVC (${fvc} L) ≥ LLN, אך FEV₁ (${fev1} L) < LLN (${lln} L) — דפוס לא-ספציפי`,
  deriveBdSignificant:    (d: string) => `תגובת ברונכודיל: משמעותית${d} — מרכיב הפיך`,
  deriveBdNotSignificant: 'תגובת ברונכודיל: לא משמעותית — הגבלת זרימת אוויר קבועה',

  // ── ERS2022Tab ───────────────────────────────────────────────────────────────
  ersNotAvailable:    'פירוש ERS 2022 אינו זמין',
  ersTabTitle:        'תקן ERS/ATS 2022 הטכני',
  ersTabDesc:         'משתמש במשוואות GLI 2012 עם גבולות תחתיים של נורמה (LLN) תלויי-גיל (אחוזון 5). עוקב אחר אלגוריתם ERS 2022 (איור 8) לפירוש ספירומטריה.',
  ersEthnicNote:      'הערה אתנית: משוואות GLI 2012 נגזרו בעיקר מאוכלוסיות אירופאיות/קווקזיות. האוכלוסייה הישראלית מגוונת אתנית (אשכנזים, ספרדים, מזרחים, ערבים, יוצאי אתיופיה). ניתן לשקול משוואות GLI 2021 לכיסוי אתני רחב יותר.',
  ersPrimaryPattern:  'הערכת דפוס ראשי',
  ersTlcNote:         'נדרשת מדידת TLC',
  ersTlcDesc:         'ספירומטריה לבדה אינה יכולה לאשר הגבלה. נדרשת מדידת נפח ריאות כוללת (פלתיסמוגרפיה גופנית או דילול הליום) לאימות TLC < אחוזון 5.',
  ersClinicalNotes:   'הערות קלינית',
  ersPatternLabel:    'דפוס:',
  ersSeverityLabel:   'חומרה:',

  // ── TraditionalTab ───────────────────────────────────────────────────────────
  tradNotAvailable:   'פירוש מסורתי אינו זמין',
  tradTabTitle:       'שיטת GOLD המסורתית',
  tradTabDesc:        'משתמש במשוואות מוריי המסורתיות עם סף קבוע FEV₁/FVC < 0.70 ו-LLN של 80% מהצפוי. דירוג חומרה GOLD מבוסס על FEV₁ % מהצפוי.',
  tradGoldAssessment: 'הערכת GOLD',
  tradClinicalNotes:  'הערות קליניות',
  tradPatternLabel:   'דפוס:',
  tradSeverityLabel:  'חומרה:',

  // ── MethodComparisonTab ──────────────────────────────────────────────────────
  methodBdTitle:              'תגובה לברונכודיל',
  methodSignificantLabel:     'משמעותית',
  methodNotSignificantLabel:  'לא משמעותית',
  methodPrimaryPattern:       'הערכת דפוס ראשי',
  methodsDisagreeLabel:       'השיטות אינן מסכימות',
  methodsAgreeLabel:          'השיטות מסכימות',
  methodSeverityLabel:        'חומרה:',
  methodErsNotAvailable:      'הערכת ERS 2022 אינה זמינה',
  methodTradNotAvailable:     'הערכת מסורתית אינה זמינה',
  methodCompTable:            'השוואת שיטות חיזוי',
  methodParamCol:             'פרמטר',
  methodMeasuredCol:          'נמדד',
  methodAgreementCol:         'הסכמה',
  methodAgree:                '✓ מסכים',
  methodDisagree:             '✗ לא מסכים',

  // ── ExtendedPFTDisplay ───────────────────────────────────────────────────────
  extIntegratedTitle: 'הערכה PFT משולבת',
  extLungVolumes:     'נפחי ריאות',
  extGasTransfer:     'העברת גז',
  extPatternLabel:    'דפוס',

  // ── ResultsComponent ─────────────────────────────────────────────────────────
  resultsKeyParams:   'פרמטרים עיקריים של תפקוד ריאות',
  resultsParamCol:    'פרמטר',
  resultsMeasuredCol: 'נמדד',
  resultsMurrayPred:  'צפוי (מוריי)',
  resultsGliPred:     'צפוי (GLI)',
  resultsStatusCol:   'סטטוס',

  // ── ViewPDF ─────────────────────────────────────────────────────────────────
  zoomOut:          'Zoom out',
  zoomIn:           'Zoom in',
  rotate:           'Rotate 90°',
  resetView:        'Reset view',
  resetBtn:         'Reset',
  downloadPdf:      'Download PDF',
  fullscreen:       'Fullscreen',
  exitFullscreen:   'Exit fullscreen',
  analyzingReport:  'Analyzing spirometry report…',
  noPdfLoaded:      'No PDF loaded',
  noPdfMessage:     'Upload a spirometry report to view it here',
  page:             'Page',
  prevPage:         '← Prev',
  nextPage:         'Next →',
  pressEscToExit:   'Press ESC to exit',
  loadingPdf:       'Loading PDF…',
  failedLoadPdf:    'Failed to load PDF',
  unableLoadPdf:    'Unable to load PDF',
  retry:            'Retry',
  refreshPage:      'Refresh page',
  refreshPageNote:  'If problems persist, try a different browser or disable ad blockers.',
  maxRetriesError:  'Maximum retry attempts reached. Please refresh the page or contact support.',
  retryFailed:      'Retry failed. Please refresh the page.',
  pdfEngineError:   'PDF rendering engine error. Please try refreshing the page.',
  pdfNetworkError:  'Network error loading PDF. Please check your connection.',
  invalidPdf:       'Invalid or corrupted PDF file.',
  passwordProtected: 'Password-protected PDF files are not supported.',
  corsError:        'PDF access blocked. Please contact support.',
  pageRenderError:  'Page rendering failed',
};
