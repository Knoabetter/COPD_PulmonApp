import React, { useState } from 'react';
import { FileText, Activity, Loader2, AlertTriangle } from 'lucide-react';
import ViewPDF from '../ViewPDF';
import EnhancedAnalysisResults from './EnhancedAnalysisResults';
import DiagnosisModal from './DiagnosisModal';
import BatchUploadSection from '../shared/BatchUploadSection';
import { authFetch } from '../../utils/authFetch';
import { t } from '../../translations';

const API_BASE = import.meta.env.VITE_API_URL ?? '';

const ClinicalAnalysisModule = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [diagnosticCriteria, setDiagnosticCriteria] = useState('comparison');
  const [uploadStatus, setUploadStatus] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [pdfFilename, setPdfFilename] = useState<string | null>(null);

  const [showDiagnosisModal, setShowDiagnosisModal] = useState(false);
  const [diagnosisSuggestions, setDiagnosisSuggestions] = useState<any>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [batchResults, setBatchResults] = useState<any[] | null>(null);
  const [selectedBatchIndex, setSelectedBatchIndex] = useState(0);
  const [currentView, setCurrentView] = useState<'single' | 'batch'>('single');
  const [_pdfError, setPdfError] = useState<string | null>(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [processingStartTime, setProcessingStartTime] = useState<number | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const setPdfUrlSafely = (filename: string | null) => {
    if (filename) {
      setPdfLoading(true);
      setPdfError(null);
      const url = `${API_BASE}/api/pdf/${filename}`;
      authFetch(url, { method: 'HEAD' })
        .then(response => {
          if (response.ok) setPdfUrl(url);
          else throw new Error(`PDF not accessible: ${response.status}`);
        })
        .catch(error => {
          setPdfError(`Unable to load PDF: ${error.message}`);
          setPdfUrl(null);
        })
        .finally(() => setPdfLoading(false));
    }
  };

  const cleanupObjectUrl = () => {
    if (pdfUrl && pdfUrl.startsWith('blob:')) URL.revokeObjectURL(pdfUrl);
  };

  // ─── Transform a raw batch result into the shape EnhancedAnalysisResults expects ─
  const transformBatchResult = (result: any): any => {
    const t: any = {
      patient: {
        age: result.patient_info?.age || 0,
        sex: result.patient_info?.sex || '',
        height: result.patient_info?.height || 0,
      },
      measured: {
        FEV1: result.measured_values?.FEV1_PRE || 0,
        FVC:  result.measured_values?.FVC_PRE  || 0,
        ratio: result.measured_values?.['FEV 1 % FVC_PRE'] || 0,
      },
      murray: {
        FEV1:  { pred: result.murray_predictions?.FEV1_Murray_pred  || 0, lln: result.murray_predictions?.FEV1_Murray_LLN  || 0, measured: result.measured_values?.FEV1_PRE || 0 },
        FVC:   { pred: result.murray_predictions?.FVC_Murray_pred   || 0, lln: result.murray_predictions?.FVC_Murray_LLN   || 0, measured: result.measured_values?.FVC_PRE  || 0 },
        ratio: { pred: result.murray_predictions?.FEV1_FVC_Murray_pred || 0, lln: result.murray_predictions?.FEV1_FVC_Murray_LLN || 0, measured: result.measured_values?.['FEV 1 % FVC_PRE'] || 0 },
      },
      gli: {
        FEV1:  { pred: result.gli_predictions?.FEV1_GLI_pred  || 0, lln: result.gli_predictions?.FEV1_GLI_LLN  || 0, measured: result.measured_values?.FEV1_PRE || 0 },
        FVC:   { pred: result.gli_predictions?.FVC_GLI_pred   || 0, lln: result.gli_predictions?.FVC_GLI_LLN   || 0, measured: result.measured_values?.FVC_PRE  || 0 },
        ratio: { pred: result.gli_predictions?.FEV1_FVC_GLI_pred || 0, lln: result.gli_predictions?.FEV1_FVC_GLI_LLN || 0, measured: result.measured_values?.['FEV 1 % FVC_PRE'] || 0 },
      },
      validation: {
        status: (result.validation_warnings?.length ?? 0) > 0 ? 'WARNINGS' : 'OK',
        errors: [],
        warnings: result.validation_warnings ?? [],
      },
      extraction_info: result.extraction_info ?? null,
    };
    if (result.clinical_interpretation) t.clinical_interpretation = result.clinical_interpretation;
    return t;
  };

  const getDiagnosisFromRatio = (ratio: number) => {
    if (ratio < 0.70) return 'COPD (Obstructive)';
    if (ratio < 0.75) return 'Borderline';
    return 'Normal';
  };

  const checkForObstructivePattern = async (analysisData: any) => {
    try {
      const measuredRatio = analysisData.measured?.ratio;
      const fev1Percent = analysisData.murray?.FEV1?.percent;
      if (!measuredRatio || measuredRatio >= 0.70) return;
      const response = await authFetch(`${API_BASE}/diagnosis/suggest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fev1_fvc_ratio: measuredRatio,
          fev1_predicted_percent: fev1Percent,
          method: diagnosticCriteria === 'murray' ? 'murray' : 'gli',
          age: analysisData.patient?.age,
        }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const suggestions = await response.json();
      if (suggestions.success && suggestions.suggestions.has_obstruction) {
        setDiagnosisSuggestions(suggestions.suggestions);
        setShowDiagnosisModal(true);
      }
    } catch (error) {
      console.error('Error checking obstructive pattern:', error);
    }
  };

  const saveDiagnosis = async (diagnosis: string, severity: string) => {
    const response = await authFetch(`${API_BASE}/diagnosis/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient_id: analysisResults?.patient?.id || 'Unknown',
        test_date: new Date().toISOString().split('T')[0],
        diagnosis,
        severity,
      }),
    });
    const result = await response.json();
    if (!result.success) throw new Error(result.error);
  };

  const handleDiagnosisConfirm = async (severity: string, _criteria: any) => {
    try {
      await saveDiagnosis(`Obstructive pattern - ${severity} severity`, severity);
      alert(t.diagnosisConfirmed);
    } catch (error) {
      alert(t.diagnosisError + ': ' + (error as Error).message);
    }
  };

  const handleDiagnosisDecline = async (customDiagnosis: string) => {
    try {
      await saveDiagnosis(customDiagnosis, '');
      alert(t.customDiagnosisSaved);
    } catch (error) {
      alert(t.diagnosisError + ': ' + (error as Error).message);
    }
  };

  // Cleanup blob URLs on unmount
  React.useEffect(() => {
    return () => { cleanupObjectUrl(); };
  }, [pdfUrl]);

  // Elapsed-time timer
  React.useEffect(() => {
    if (!isProcessing || processingStartTime === null) { setElapsedSeconds(0); return; }
    const interval = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - processingStartTime) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [isProcessing, processingStartTime]);

  // Load PDF for the active batch tab
  React.useEffect(() => {
    if (currentView !== 'batch' || !batchResults || !batchResults[selectedBatchIndex]?.success) return;
    const r = batchResults[selectedBatchIndex];
    if (r.pdf_filename) { cleanupObjectUrl(); setPdfUrlSafely(r.pdf_filename); }
    else { setPdfUrl(null); setPdfError('PDF not available for this result'); }
  }, [selectedBatchIndex, batchResults, currentView]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    cleanupObjectUrl();
    setAnalysisResults(null);
    setPdfError(null);
    setUploadStatus('');
    setUploadProgress(0);

    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setPdfFilename(file.name);
      setPdfUrl(URL.createObjectURL(file));
      setUploadStatus('PDF loaded. Ready for analysis.');
    } else if (file) {
      setUploadStatus('Please select a valid PDF file.');
      setSelectedFile(null);
      setPdfFilename(null);
      setPdfUrl(null);
    }
  };

  const handleBatchAnalysis = async (files: File[]) => {
    setIsProcessing(true);
    setBatchResults(null);
    setAnalysisResults(null);
    setProcessingStartTime(Date.now());
    setElapsedSeconds(0);
    setUploadProgress(0);

    let progressInterval: ReturnType<typeof setInterval> | null = null;
    let simProgress = 0;
    progressInterval = setInterval(() => {
      simProgress = Math.min(85, simProgress + (85 - simProgress) * 0.04);
      setUploadProgress(Math.floor(simProgress));
    }, 250);

    try {
      const formData = new FormData();
      files.forEach((file: File, index: number) => formData.append(`file_${index}`, file));
      formData.append('criteria', diagnosticCriteria);
      setUploadStatus(`Processing ${files.length} file${files.length > 1 ? 's' : ''}…`);

      const response = await authFetch(`${API_BASE}/analyze/batch`, { method: 'POST', body: formData });
      if (progressInterval) { clearInterval(progressInterval); progressInterval = null; }

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const result = await response.json();

      if (result.success) {
        setBatchResults(result.results);
        setSelectedBatchIndex(0);
        setUploadProgress(100);
        const summary = result.summary || {};
        setUploadStatus(
          `Batch complete: ${result.successful_analyses}/${result.total_files} successful — ` +
          `${summary.copd_cases || 0} COPD, ${summary.normal_cases || 0} normal, ${summary.borderline_cases || 0} borderline.`
        );
      } else {
        throw new Error(result.error || 'Batch analysis failed');
      }
    } catch (error) {
      if (progressInterval) { clearInterval(progressInterval); progressInterval = null; }
      setUploadStatus(`Batch analysis failed: ${(error as Error).message}`);
      setUploadProgress(0);
    } finally {
      if (progressInterval) clearInterval(progressInterval);
      setIsProcessing(false);
      setTimeout(() => setUploadProgress(0), 3000);
    }
  };

  const handleAnalysis = async () => {
    if (!selectedFile) { setUploadStatus('Please select a PDF file to analyze.'); return; }
    setIsProcessing(true);
    setUploadProgress(0);
    setProcessingStartTime(Date.now());
    setElapsedSeconds(0);

    let progressInterval: ReturnType<typeof setInterval> | null = null;

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('criteria', diagnosticCriteria);

      let simProgress = 0;
      progressInterval = setInterval(() => {
        simProgress = Math.min(85, simProgress + (85 - simProgress) * 0.06);
        setUploadProgress(Math.floor(simProgress));
      }, 250);

      const response = await authFetch(`${API_BASE}/analyze`, { method: 'POST', body: formData });
      clearInterval(progressInterval);
      progressInterval = null;

      if (!response.ok) {
        let errorMsg = `Server error ${response.status}`;
        try { const e = await response.json(); errorMsg = e.error || errorMsg; } catch {}
        throw new Error(errorMsg);
      }
      const results = await response.json();
      setUploadProgress(100);

      if (results.success) {
        const measured_fev1  = results.measured_values?.FEV1_PRE || 0;
        const measured_fvc   = results.measured_values?.FVC_PRE  || 0;
        const measured_ratio = results.measured_values?.['FEV 1 % FVC_PRE'] || 0;

        const transformedResults: any = {
          patient: { age: results.patient_info?.age || 0, sex: results.patient_info?.sex || '', height: results.patient_info?.height || 0 },
          measured: { FEV1: measured_fev1, FVC: measured_fvc, ratio: measured_ratio },
          murray: {
            FEV1:  { pred: results.murray_predictions?.FEV1_Murray_pred  || 0, lln: results.murray_predictions?.FEV1_Murray_LLN  || 0, measured: measured_fev1, percent: measured_fev1 && results.murray_predictions?.FEV1_Murray_pred  ? Math.round((measured_fev1 / results.murray_predictions.FEV1_Murray_pred)  * 100) : 0 },
            FVC:   { pred: results.murray_predictions?.FVC_Murray_pred   || 0, lln: results.murray_predictions?.FVC_Murray_LLN   || 0, measured: measured_fvc,  percent: measured_fvc  && results.murray_predictions?.FVC_Murray_pred   ? Math.round((measured_fvc  / results.murray_predictions.FVC_Murray_pred)   * 100) : 0 },
            ratio: { pred: results.murray_predictions?.FEV1_FVC_Murray_pred || 0, lln: results.murray_predictions?.FEV1_FVC_Murray_LLN || 0, measured: measured_ratio },
          },
          gli: {
            FEV1:  { pred: results.gli_predictions?.FEV1_GLI_pred  || 0, lln: results.gli_predictions?.FEV1_GLI_LLN  || 0, measured: measured_fev1, percent: measured_fev1 && results.gli_predictions?.FEV1_GLI_pred  ? Math.round((measured_fev1 / results.gli_predictions.FEV1_GLI_pred)  * 100) : 0 },
            FVC:   { pred: results.gli_predictions?.FVC_GLI_pred   || 0, lln: results.gli_predictions?.FVC_GLI_LLN   || 0, measured: measured_fvc,  percent: measured_fvc  && results.gli_predictions?.FVC_GLI_pred   ? Math.round((measured_fvc  / results.gli_predictions.FVC_GLI_pred)   * 100) : 0 },
            ratio: { pred: results.gli_predictions?.FEV1_FVC_GLI_pred || 0, lln: results.gli_predictions?.FEV1_FVC_GLI_LLN || 0, measured: measured_ratio },
          },
          agreement: {
            diagnosis: getDiagnosisFromRatio(measured_ratio),
            ratioDiff: Math.abs((results.gli_predictions?.FEV1_FVC_GLI_pred || 0) - (results.murray_predictions?.FEV1_FVC_Murray_pred || 0)),
            percentDiff: results.murray_predictions?.FEV1_FVC_Murray_pred
              ? Math.abs(((results.gli_predictions?.FEV1_FVC_GLI_pred || 0) - results.murray_predictions.FEV1_FVC_Murray_pred) / results.murray_predictions.FEV1_FVC_Murray_pred * 100) : 0,
            clinicalImpact: 'Both methods agree',
          },
          validation: {
            status: (results.validation_warnings?.length ?? 0) > 0 ? 'WARNINGS' : 'OK',
            errors: [],
            warnings: [...(results.validation_warnings ?? []), ...(results.patient_info?.age > 80 ? [`Age ${results.patient_info.age} is at upper range for reference values`] : [])],
          },
          extraction_info: results.extraction_info ?? null,
          rawData: results,
        };
        if (results.clinical_interpretation) transformedResults.clinical_interpretation = results.clinical_interpretation;

        setAnalysisResults(transformedResults);
        setUploadStatus('Analysis complete!');
        await checkForObstructivePattern(transformedResults);

        if (results.pdf_filename) { cleanupObjectUrl(); setPdfUrlSafely(results.pdf_filename); }
        else setPdfError('PDF processing completed but file not available for viewing');
      } else {
        throw new Error(results.error || 'Analysis failed');
      }
    } catch (error) {
      setUploadStatus(`Analysis failed: ${(error as Error).message}`);
      setUploadProgress(0);
    } finally {
      if (progressInterval) clearInterval(progressInterval);
      setIsProcessing(false);
      setTimeout(() => setUploadProgress(0), 3000);
    }
  };

  // ─── Criteria pill options ─────────────────────────────────────────────────
  const criteriaOptions = [
    { value: 'murray',     label: t.murray,  activeClass: 'bg-blue-600 text-white border-blue-600' },
    { value: 'gli',        label: t.gli,     activeClass: 'bg-purple-600 text-white border-purple-600' },
    { value: 'comparison', label: t.compare, activeClass: 'bg-emerald-600 text-white border-emerald-600' },
  ];

  const activeBatchResult = batchResults?.[selectedBatchIndex] ?? null;
  const activeBatchAnalysis = activeBatchResult?.success ? transformBatchResult(activeBatchResult) : null;

  return (
    <div className="max-w-full mx-auto p-6 space-y-6">

      {/* ── Compact control card ─────────────────────────────────────────── */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-5 shadow-sm">

        {/* Single / Batch toggle */}
        <div className="flex gap-2">
          {(['single', 'batch'] as const).map(mode => (
            <button
              key={mode}
              onClick={() => { setCurrentView(mode); setBatchResults(null); setAnalysisResults(null); setUploadStatus(''); }}
              className={`px-5 py-2 rounded-full text-sm font-bold border-2 transition-all ${
                currentView === mode
                  ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                  : 'bg-white text-slate-500 border-slate-200 hover:border-slate-400 hover:text-slate-700'
              }`}
            >
              {mode === 'single' ? t.singlePdf : t.batch}
            </button>
          ))}
        </div>

        {/* Upload area */}
        {currentView === 'single' ? (
          <div className={`border-2 border-dashed rounded-xl transition-colors ${
            selectedFile ? 'border-emerald-400 bg-emerald-50/40' : 'border-slate-200 hover:border-slate-400'
          }`}>
            <input type="file" accept=".pdf" onChange={handleFileChange} className="hidden" id="pdf-upload" />
            <label htmlFor="pdf-upload" className="flex items-center gap-3 px-5 py-4 cursor-pointer">
              <FileText className={`w-5 h-5 shrink-0 ${selectedFile ? 'text-emerald-600' : 'text-slate-400'}`} />
              <span className={`text-sm ${selectedFile ? 'text-slate-900 font-semibold' : 'text-slate-500'}`}>
                {selectedFile ? selectedFile.name : t.clickToSelectPdf}
              </span>
              {selectedFile && <span className="ms-auto text-sm text-emerald-600 font-bold">{t.ready}</span>}
            </label>
          </div>
        ) : (
          <BatchUploadSection onBatchAnalysis={handleBatchAnalysis} isProcessing={isProcessing} />
        )}

        {/* Criteria pills */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider me-1">{t.reference}</span>
          {criteriaOptions.map(opt => (
            <button
              key={opt.value}
              onClick={() => setDiagnosticCriteria(opt.value)}
              className={`px-4 py-1.5 rounded-full text-sm border-2 font-bold transition-all ${
                diagnosticCriteria === opt.value ? opt.activeClass + ' shadow-sm' : 'bg-white text-slate-600 border-slate-200 hover:border-slate-400'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {/* Analyze button — single mode only */}
        {currentView === 'single' && (
          <button
            onClick={handleAnalysis}
            disabled={!selectedFile || isProcessing}
            className={`w-full py-3.5 px-4 rounded-xl font-bold text-base flex items-center justify-center transition-all shadow-sm ${
              !selectedFile || isProcessing
                ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-emerald-600 to-teal-500 text-white hover:from-emerald-700 hover:to-teal-600 shadow-emerald-200 shadow-md'
            }`}
          >
            {isProcessing
              ? <><Loader2 className="w-5 h-5 me-2 animate-spin" />{t.processingBtn}</>
              : <><Activity className="w-5 h-5 me-2" />{t.analyzeSpirometry}</>
            }
          </button>
        )}
      </div>

      {/* Status line (both modes) */}
      {uploadStatus && (
        <p className={`text-center text-sm font-medium -mt-2 ${
          uploadStatus.includes('failed') ? 'text-red-600' :
          uploadStatus.includes('complete') ? 'text-emerald-600' : 'text-blue-600'
        }`}>
          {uploadStatus}
        </p>
      )}

      {/* Processing — centered gif */}
      {isProcessing && (
        <div className="flex flex-col items-center justify-center py-10">
          <img
            src="/images/analyzing.gif"
            alt="Analyzing..."
            className="w-[36rem] h-[36rem] object-contain"
          />
          <div className="flex items-center gap-3 text-sm text-slate-500 mt-2">
            <span className="font-bold text-blue-600">{uploadProgress}%</span>
            <span>•</span>
            <span className="font-mono">{`${String(Math.floor(elapsedSeconds / 60)).padStart(2, '0')}:${String(elapsedSeconds % 60).padStart(2, '0')}`} {t.elapsed}</span>
          </div>
        </div>
      )}

      {/* ── Batch results — tab bar + split view ───────────────────────── */}
      {currentView === 'batch' && batchResults && batchResults.length > 0 && (
        <>
          {/* Tab bar */}
          <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
            <div className="flex overflow-x-auto border-b border-slate-200 bg-slate-50/60">
              {batchResults.map((r, idx) => {
                const label = (r.filename || `File ${idx + 1}`).replace(/\.pdf$/i, '');
                const short = label.length > 22 ? '…' + label.slice(-20) : label;
                const info  = r.success && r.patient_info ? ` · ${r.patient_info.age}y ${r.patient_info.sex}` : '';
                return (
                  <button
                    key={idx}
                    onClick={() => setSelectedBatchIndex(idx)}
                    className={`flex-shrink-0 px-5 py-4 text-sm font-semibold border-b-2 transition-all whitespace-nowrap ${
                      selectedBatchIndex === idx
                        ? 'border-blue-500 text-blue-700 bg-white'
                        : r.success
                          ? 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-white/60'
                          : 'border-transparent text-red-400 hover:bg-red-50'
                    }`}
                  >
                    {!r.success && '⚠ '}{short}{info}
                  </button>
                );
              })}
            </div>

            {/* Failed tab error message */}
            {activeBatchResult && !activeBatchResult.success && (
              <div className="flex items-start gap-3 p-5">
                <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5 shrink-0" />
                <p className="text-base text-red-700 font-medium">
                  Analysis failed: {activeBatchResult.error || 'Unknown error'}
                </p>
              </div>
            )}
          </div>

          {/* Split view for the active (successful) tab */}
          {activeBatchResult?.success && activeBatchAnalysis && (
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 h-[800px]">
              <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
                <div className="bg-slate-900 px-5 py-4 border-b border-slate-700">
                  <h3 className="font-bold text-white flex items-center gap-2 text-sm">
                    <FileText className="w-4 h-4 text-slate-400" />
                    {activeBatchResult.filename}
                  </h3>
                </div>
                <div className="h-full p-4">
                  <ViewPDF pdfUrl={pdfUrl ?? undefined} filename={activeBatchResult.filename} isLoading={pdfLoading} />
                </div>
              </div>
              <div className="overflow-y-auto">
                <EnhancedAnalysisResults analysisResults={activeBatchAnalysis} />
              </div>
            </div>
          )}
        </>
      )}

      {/* ── Single mode — split view ────────────────────────────────────── */}
      {currentView === 'single' && !isProcessing && (analysisResults || selectedFile) && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 h-[800px]">
          <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
            <div className="bg-slate-900 px-5 py-4 border-b border-slate-700">
              <h3 className="font-bold text-white flex items-center gap-2 text-sm">
                <FileText className="w-4 h-4 text-slate-400" />
                {t.spirometryReport}
              </h3>
            </div>
            <div className="h-full p-4">
              <ViewPDF pdfUrl={pdfUrl ?? undefined} filename={pdfFilename ?? undefined} isLoading={pdfLoading} />
            </div>
          </div>
          <div className="overflow-y-auto">
            {analysisResults && <EnhancedAnalysisResults analysisResults={analysisResults} />}
          </div>
        </div>
      )}

      <DiagnosisModal
        isOpen={showDiagnosisModal}
        onClose={() => setShowDiagnosisModal(false)}
        suggestions={diagnosisSuggestions}
        onConfirm={handleDiagnosisConfirm}
        onDecline={handleDiagnosisDecline}
      />
    </div>
  );
};

export default ClinicalAnalysisModule;
