import React, { useState, useEffect } from 'react';
import {
  Upload, BarChart3, Database, Download, FileText, Users, TrendingUp,
  AlertCircle, CheckCircle, Settings, Loader2, Eye, Filter, Calendar, Clock,
} from 'lucide-react';
import { authFetch } from '../utils/authFetch';

const API_BASE = import.meta.env.VITE_API_URL ?? '';

// ── Shared design primitives ──────────────────────────────────────
const SectionCard = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => (
  <div className={`bg-white border border-slate-200 rounded-xl shadow-sm ${className}`}>
    {children}
  </div>
);

const SectionHeader = ({ icon, title, subtitle }: { icon?: React.ReactNode; title: string; subtitle?: string }) => (
  <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-3">
    {icon && <span className="text-slate-400">{icon}</span>}
    <div>
      <h2 className="text-sm font-bold text-slate-800">{title}</h2>
      {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
    </div>
  </div>
);

const Stat = ({ value, label, color = 'text-blue-600' }: { value: string | number; label: string; color?: string }) => (
  <div className="text-center">
    <div className={`text-2xl font-bold ${color}`}>{value}</div>
    <div className="text-xs text-slate-500 mt-0.5">{label}</div>
  </div>
);

// ── Types ─────────────────────────────────────────────────────────
type FileResult = {
  filename: string;
  records_found: number;
  status: 'processed' | 'failed';
  server_links_found: number;
  error?: string;
};

type BatchResults = {
  total_files_processed: number;
  total_records_found: number;
  file_results: FileResult[];
  timestamp: string;
};

type DbStatus = {
  database_info: {
    filename: string;
    file_size_mb: number;
    last_modified: string;
  };
  statistics: {
    total_records: number;
    validated_records: number;
    validation_rate: number;
    total_columns: number;
  };
};

// ── Main component ────────────────────────────────────────────────
const ResearchModule = () => {
  const [selectedFiles,        setSelectedFiles]        = useState<File[]>([]);
  const [activeTab,            setActiveTab]            = useState<'batch' | 'population' | 'database'>('batch');
  const [isProcessing,         setIsProcessing]         = useState(false);
  const [batchResults,         setBatchResults]         = useState<BatchResults | null>(null);
  const [extractionPeriod,     setExtractionPeriod]     = useState({ startDate: '', endDate: '' });
  const [uploadStatus,         setUploadStatus]         = useState('');
  const [uploadProgress,       setUploadProgress]       = useState(0);
  const [processingStartTime,  setProcessingStartTime]  = useState<number | null>(null);
  const [elapsedSeconds,       setElapsedSeconds]       = useState(0);
  const [dbStatus,             setDbStatus]             = useState<DbStatus | null>(null);
  const [dbLoading,            setDbLoading]            = useState(false);

  // ── Elapsed timer ────────────────────────────────────────────────
  useEffect(() => {
    if (!isProcessing || processingStartTime === null) { setElapsedSeconds(0); return; }
    const id = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - processingStartTime) / 1000));
    }, 1000);
    return () => clearInterval(id);
  }, [isProcessing, processingStartTime]);

  // ── Load DB status when Database tab opens ────────────────────────
  useEffect(() => {
    if (activeTab !== 'database' || dbStatus !== null) return;
    setDbLoading(true);
    authFetch(`${API_BASE}/research/database/status`)
      .then(r => r.json())
      .then(data => { if (data.success) setDbStatus(data); })
      .catch(() => {})
      .finally(() => setDbLoading(false));
  }, [activeTab]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setSelectedFiles(files.filter(f =>
      f.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || f.name.endsWith('.xlsx')
    ));
  };

  const handleBatchAnalysis = async () => {
    if (selectedFiles.length === 0 && !extractionPeriod.startDate) {
      setUploadStatus('Please select XLSX files or set an extraction period.');
      return;
    }
    setIsProcessing(true);
    setBatchResults(null);
    setUploadStatus('');
    setUploadProgress(0);
    setProcessingStartTime(Date.now());
    setElapsedSeconds(0);

    let progressInterval: ReturnType<typeof setInterval> | null = null;
    let simProgress = 0;
    progressInterval = setInterval(() => {
      simProgress = Math.min(85, simProgress + (85 - simProgress) * 0.04);
      setUploadProgress(Math.floor(simProgress));
    }, 250);

    try {
      const formData = new FormData();
      selectedFiles.forEach(f => formData.append('files', f));
      if (extractionPeriod.startDate) {
        formData.append('start_date', extractionPeriod.startDate);
        formData.append('end_date',   extractionPeriod.endDate);
      }

      const response = await authFetch(`${API_BASE}/research/batch-xlsx`, {
        method: 'POST',
        body: formData,
      });

      if (progressInterval) { clearInterval(progressInterval); progressInterval = null; }

      if (!response.ok) throw new Error(`Server error ${response.status}`);
      const result = await response.json();

      if (result.success) {
        setBatchResults(result);
        setUploadProgress(100);
        const succeeded = (result.file_results as FileResult[]).filter(r => r.status === 'processed').length;
        setUploadStatus(
          `Batch complete: ${succeeded}/${result.total_files_processed} files processed — ` +
          `${result.total_records_found.toLocaleString()} records found.`
        );
      } else {
        throw new Error(result.error || 'Batch processing failed');
      }
    } catch (error) {
      if (progressInterval) { clearInterval(progressInterval); progressInterval = null; }
      setUploadStatus(`Processing failed: ${(error as Error).message}`);
      setUploadProgress(0);
    } finally {
      if (progressInterval) clearInterval(progressInterval);
      setIsProcessing(false);
      setTimeout(() => setUploadProgress(0), 3000);
    }
  };

  const fmt = (s: number) =>
    `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  const tabs: { id: 'batch' | 'population' | 'database'; label: string; icon: React.ReactNode }[] = [
    { id: 'batch',      label: 'Batch Processing',   icon: <Upload className="w-4 h-4" /> },
    { id: 'population', label: 'Population Studies', icon: <TrendingUp className="w-4 h-4" /> },
    { id: 'database',   label: 'Database',           icon: <Database className="w-4 h-4" /> },
  ];

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">

      {/* Page header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900">Research Module</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Batch processing, population analysis, and database management for hospital spirometry data.
        </p>
      </div>

      {/* Tab bar */}
      <div className="border-b border-slate-200">
        <div className="flex gap-0">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold border-b-2 -mb-px transition-all ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab content */}
      {activeTab === 'batch' && (
        <>
          {batchResults
            ? <BatchResultsView results={batchResults} onBack={() => { setBatchResults(null); setUploadStatus(''); }} />
            : <BatchUploadView
                selectedFiles={selectedFiles}
                extractionPeriod={extractionPeriod}
                isProcessing={isProcessing}
                onFileChange={handleFileChange}
                onDateChange={setExtractionPeriod}
                onSubmit={handleBatchAnalysis}
              />
          }

          {/* Progress bar */}
          {isProcessing && (
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-bold text-slate-700">Processing hospital data…</span>
                <div className="flex items-center gap-3 text-sm text-slate-500">
                  <span className="font-bold text-blue-600">{uploadProgress}%</span>
                  <span>•</span>
                  <span className="font-mono">{fmt(elapsedSeconds)} elapsed</span>
                </div>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2.5">
                <div
                  className="h-2.5 rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Status line */}
          {uploadStatus && (
            <p className={`text-center text-sm font-medium -mt-2 ${
              uploadStatus.includes('failed') ? 'text-red-600' :
              uploadStatus.includes('complete') ? 'text-emerald-600' : 'text-blue-600'
            }`}>
              {uploadStatus}
            </p>
          )}
        </>
      )}

      {activeTab === 'population' && <PopulationStudiesView />}
      {activeTab === 'database'   && <DatabaseView dbStatus={dbStatus} dbLoading={dbLoading} onImportSuccess={() => { setDbStatus(null); setDbLoading(true); authFetch(`${API_BASE}/research/database/status`).then(r => r.json()).then(d => { if (d.success) setDbStatus(d); }).catch(() => {}).finally(() => setDbLoading(false)); }} />}
    </div>
  );
};

// ── Batch Upload View ─────────────────────────────────────────────
const BatchUploadView = ({ selectedFiles, extractionPeriod, isProcessing, onFileChange, onDateChange, onSubmit }: {
  selectedFiles: File[];
  extractionPeriod: { startDate: string; endDate: string };
  isProcessing: boolean;
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onDateChange: (v: { startDate: string; endDate: string }) => void;
  onSubmit: () => void;
}) => (
  <div className="space-y-5">
    {/* XLSX upload */}
    <SectionCard>
      <SectionHeader icon={<Upload className="w-4 h-4" />} title="XLSX Batch Upload" subtitle="Upload files containing hospital server links" />
      <div className="p-6 space-y-4">
        <div className={`border-2 border-dashed rounded-xl transition-colors ${
          selectedFiles.length > 0 ? 'border-blue-300 bg-blue-50/40' : 'border-slate-200 hover:border-slate-300'
        }`}>
          <input type="file" accept=".xlsx,.xls" multiple onChange={onFileChange} className="hidden" id="research-upload" />
          <label htmlFor="research-upload" className="flex items-center gap-3 px-5 py-5 cursor-pointer">
            <FileText className={`w-5 h-5 shrink-0 ${selectedFiles.length > 0 ? 'text-blue-600' : 'text-slate-400'}`} />
            <div>
              <p className={`text-sm font-semibold ${selectedFiles.length > 0 ? 'text-slate-900' : 'text-slate-600'}`}>
                {selectedFiles.length > 0
                  ? `${selectedFiles.length} XLSX file${selectedFiles.length > 1 ? 's' : ''} selected`
                  : 'Click to upload XLSX files with server links'}
              </p>
              <p className="text-xs text-slate-400 mt-0.5">Each file may contain up to 2000 hospital records</p>
            </div>
            {selectedFiles.length > 0 && <span className="ml-auto text-sm text-blue-600 font-bold">✓ Ready</span>}
          </label>
        </div>

        {selectedFiles.length > 0 && (
          <div className="space-y-1">
            {selectedFiles.map((f, i) => (
              <div key={i} className="flex items-center justify-between text-sm bg-slate-50 rounded-lg px-3 py-2">
                <span className="text-slate-700 truncate">{f.name}</span>
                <span className="text-xs text-slate-400 ml-2 shrink-0">{(f.size / 1024).toFixed(0)} KB</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </SectionCard>

    {/* Date range extraction */}
    <SectionCard>
      <SectionHeader icon={<Calendar className="w-4 h-4" />} title="Hospital Server Extraction" subtitle="Extract tests by time period" />
      <div className="p-6 space-y-4">
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wide">Start Date</label>
            <input
              type="date"
              value={extractionPeriod.startDate}
              onChange={e => onDateChange({ ...extractionPeriod, startDate: e.target.value })}
              className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wide">End Date</label>
            <input
              type="date"
              value={extractionPeriod.endDate}
              onChange={e => onDateChange({ ...extractionPeriod, endDate: e.target.value })}
              className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400"
            />
          </div>
        </div>
        <div className="flex items-start gap-2.5 bg-slate-50 border border-slate-200 rounded-lg px-4 py-3">
          <Clock className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
          <p className="text-xs text-slate-600">
            Tests are fetched from the hospital server by time period. PDF download is fast; OCR data extraction takes longer depending on volume.
          </p>
        </div>
      </div>
    </SectionCard>

    {/* Submit */}
    <button
      onClick={onSubmit}
      disabled={(selectedFiles.length === 0 && !extractionPeriod.startDate) || isProcessing}
      className={`w-full py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-colors ${
        (selectedFiles.length === 0 && !extractionPeriod.startDate) || isProcessing
          ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
          : 'bg-blue-600 text-white hover:bg-blue-700'
      }`}
    >
      {isProcessing
        ? <><Loader2 className="w-4 h-4 animate-spin" />Processing Hospital Data…</>
        : <><BarChart3 className="w-4 h-4" />Start Batch Processing</>}
    </button>
  </div>
);

// ── Batch Results View ────────────────────────────────────────────
const BatchResultsView = ({ results, onBack }: { results: BatchResults; onBack: () => void }) => {
  const succeeded = results.file_results.filter(r => r.status === 'processed').length;
  const failed    = results.file_results.filter(r => r.status === 'failed').length;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold text-slate-700 uppercase tracking-wider">Processing Results</h2>
        <button onClick={onBack} className="text-xs text-blue-600 hover:underline font-semibold">← New Analysis</button>
      </div>

      {/* Stats */}
      <SectionCard>
        <SectionHeader icon={<BarChart3 className="w-4 h-4" />} title="Extraction Summary" subtitle={new Date(results.timestamp).toLocaleString()} />
        <div className="p-6 grid grid-cols-2 md:grid-cols-4 gap-6">
          <Stat value={results.total_files_processed} label="Files Processed" color="text-blue-600" />
          <Stat value={results.total_records_found.toLocaleString()} label="Records Found" color="text-violet-600" />
          <Stat value={succeeded} label="Successful" color="text-emerald-600" />
          <Stat value={failed} label="Failed" color="text-red-600" />
        </div>
      </SectionCard>

      {/* Per-file table */}
      <SectionCard>
        <SectionHeader icon={<FileText className="w-4 h-4" />} title="File Results" />
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-100">
                <th className="px-5 py-3 text-left">File</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-right">Records</th>
                <th className="px-4 py-3 text-right">Server Links</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {results.file_results.map((r, i) => (
                <tr key={i} className="hover:bg-slate-50/60">
                  <td className="px-5 py-3">
                    <span className="font-medium text-slate-800 truncate max-w-[240px] block" title={r.filename}>{r.filename}</span>
                    {r.status === 'failed' && r.error && (
                      <p className="text-xs text-red-600 mt-0.5">{r.error}</p>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {r.status === 'processed'
                      ? <span className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">OK</span>
                      : <span className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800 border border-red-200">Failed</span>}
                  </td>
                  <td className="px-4 py-3 text-right font-mono font-semibold text-slate-700">
                    {r.status === 'processed' ? r.records_found.toLocaleString() : '—'}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-slate-500">
                    {r.status === 'processed' ? r.server_links_found : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>

      {/* Export actions */}
      <div className="flex flex-wrap gap-3">
        <button className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-colors">
          <Download className="w-4 h-4" /> Download Report
        </button>
        <button className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl text-sm font-semibold hover:bg-slate-50 transition-colors">
          <FileText className="w-4 h-4" /> Export to Excel
        </button>
      </div>
    </div>
  );
};

// ── Population Studies ────────────────────────────────────────────
const PopulationStudiesView = () => {
  const studies = [
    { title: 'Age-Stratified Analysis',  desc: 'Compare diagnostic method performance across age groups to identify age-related biases.' },
    { title: 'Sex-Based Comparison',     desc: 'Analyze differences in diagnostic accuracy between male and female populations.' },
    { title: 'Severity Distribution',    desc: 'Examine COPD severity classifications using different reference equations.' },
    { title: 'Longitudinal Tracking',    desc: 'Track patient spirometry changes over time using consistent reference standards.' },
  ];

  return (
    <SectionCard>
      <SectionHeader icon={<TrendingUp className="w-4 h-4" />} title="Population Studies" subtitle="Analysis tools for population-level research" />
      <div className="p-6 grid sm:grid-cols-2 gap-4">
        {studies.map(s => (
          <div key={s.title} className="border border-slate-200 rounded-xl p-5">
            <div className="flex items-start justify-between gap-3 mb-1.5">
              <h3 className="text-sm font-bold text-slate-800">{s.title}</h3>
              <span className="shrink-0 px-2 py-0.5 text-xs font-semibold bg-slate-100 text-slate-400 rounded-md cursor-not-allowed">
                Coming soon
              </span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">{s.desc}</p>
          </div>
        ))}
      </div>
    </SectionCard>
  );
};

// ── Database Management ───────────────────────────────────────────
const DatabaseView = ({ dbStatus, dbLoading, onImportSuccess }: { dbStatus: DbStatus | null; dbLoading: boolean; onImportSuccess: () => void }) => {
  const [importStatus, setImportStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [importing, setImporting] = useState(false);
  const importInputRef = React.useRef<HTMLInputElement>(null);

  const handleExport = (format: 'excel' | 'csv' | 'json') => {
    window.open(`${API_BASE}/research/database/export?format=${format}`, '_blank');
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImporting(true);
    setImportStatus(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await authFetch(`${API_BASE}/research/database/import`, { method: 'POST', body: formData });
      const data = await res.json();
      if (data.success) {
        setImportStatus({ type: 'success', message: data.message });
        onImportSuccess();
      } else {
        setImportStatus({ type: 'error', message: data.error });
      }
    } catch {
      setImportStatus({ type: 'error', message: 'Import request failed' });
    } finally {
      setImporting(false);
      if (importInputRef.current) importInputRef.current.value = '';
    }
  };

  const skelly = <div className="animate-pulse bg-slate-100 rounded h-4 w-20 inline-block" />;

  return (
    <div className="space-y-5">
      <SectionCard>
        <SectionHeader icon={<Database className="w-4 h-4" />} title="Database Status" />
        <div className="p-6 space-y-5">
          {/* File info row */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-semibold text-slate-800">
                {dbLoading ? skelly : (dbStatus?.database_info.filename ?? 'copd_extracted_data_final.xlsx')}
              </p>
              <p className="text-xs text-slate-400">
                {dbLoading ? skelly : dbStatus
                  ? `${dbStatus.database_info.file_size_mb.toFixed(1)} MB · Last updated ${new Date(dbStatus.database_info.last_modified).toLocaleDateString()}`
                  : 'Backend/Scripts/ directory'
                }
              </p>
            </div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-200">
              <CheckCircle className="w-3.5 h-3.5" /> Active
            </span>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-100">
            <Stat
              value={dbLoading ? '—' : (dbStatus?.statistics.total_records.toLocaleString() ?? '—')}
              label="Total Records" color="text-blue-700"
            />
            <Stat
              value={dbLoading ? '—' : (dbStatus?.statistics.validated_records.toLocaleString() ?? '—')}
              label="Validated" color="text-emerald-700"
            />
            <Stat
              value={dbLoading ? '—' : dbStatus ? `${dbStatus.statistics.validation_rate.toFixed(1)}%` : '—'}
              label="Validation Rate" color="text-violet-700"
            />
            <Stat
              value={dbLoading ? '—' : (dbStatus?.statistics.total_columns ?? '—')}
              label="Columns" color="text-slate-700"
            />
          </div>
        </div>
      </SectionCard>

      {/* Import feedback */}
      {importStatus && (
        <div className={`flex items-center gap-2 px-4 py-3 rounded-xl text-sm font-medium border ${importStatus.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
          {importStatus.type === 'success' ? <CheckCircle className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
          {importStatus.message}
        </div>
      )}

      {/* Actions */}
      <input ref={importInputRef} type="file" accept=".xlsx" className="hidden" onChange={handleImport} />
      <div className="grid sm:grid-cols-2 gap-3">
        <button
          onClick={() => handleExport('excel')}
          className="flex items-center gap-3 px-4 py-3.5 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
        >
          <span className="text-slate-400"><Download className="w-4 h-4" /></span>
          Export to Excel
        </button>
        <button
          onClick={() => handleExport('csv')}
          className="flex items-center gap-3 px-4 py-3.5 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
        >
          <span className="text-slate-400"><Download className="w-4 h-4" /></span>
          Export to CSV
        </button>
        <button
          onClick={() => importInputRef.current?.click()}
          disabled={importing}
          className="flex items-center gap-3 px-4 py-3.5 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50"
        >
          <span className="text-slate-400">{importing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}</span>
          {importing ? 'Importing…' : 'Import Database'}
        </button>
        <button
          className="flex items-center gap-3 px-4 py-3.5 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
        >
          <span className="text-slate-400"><Eye className="w-4 h-4" /></span>
          View Records
        </button>
        <button
          className="flex items-center gap-3 px-4 py-3.5 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
        >
          <span className="text-slate-400"><Filter className="w-4 h-4" /></span>
          Filter Records
        </button>
        <button
          className="flex items-center gap-3 px-4 py-3.5 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
        >
          <span className="text-slate-400"><Settings className="w-4 h-4" /></span>
          Validation Settings
        </button>
      </div>

      {/* Pipeline info */}
      <div className="flex items-start gap-2.5 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5">
        <AlertCircle className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
        <div>
          <p className="text-xs font-semibold text-slate-700 mb-0.5">Processing Pipeline</p>
          <p className="text-xs text-slate-500">PDF Extraction → OCR Processing → Data Validation → Excel Database (save_data.py)</p>
        </div>
      </div>
    </div>
  );
};

export default ResearchModule;
