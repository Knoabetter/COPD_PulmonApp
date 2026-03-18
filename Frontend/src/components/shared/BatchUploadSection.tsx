import React, { useState } from 'react';
import { Plus, FileText, Loader2, BarChart3, Trash2, CheckCircle2 } from 'lucide-react';

const MAX_FILES = 5;

const BatchUploadSection = ({ onBatchAnalysis, isProcessing }: { onBatchAnalysis: (files: File[]) => void; isProcessing: boolean }) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [fileProgress, setFileProgress] = useState<number[]>([]);
  const [filesDone, setFilesDone] = useState(false);

  React.useEffect(() => {
    if (isProcessing) {
      setFilesDone(false);
      setFileProgress(selectedFiles.map(() => 0));
      let ticks = 0;
      const interval = setInterval(() => {
        ticks++;
        setFileProgress(prev => prev.map((p, i) => {
          if (ticks < i * 4) return p;
          return Math.min(88, p + (88 - p) * 0.07);
        }));
      }, 250);
      return () => clearInterval(interval);
    } else if (fileProgress.length > 0) {
      setFileProgress(prev => prev.map(() => 100));
      setFilesDone(true);
    }
  }, [isProcessing]);

  const handleFiles = (files: FileList | File[]) => {
    const pdfFiles = Array.from(files).filter((f: File) => f.type === 'application/pdf');
    if (pdfFiles.length === 0) { alert('Please select only PDF files.'); return; }
    if (selectedFiles.length + pdfFiles.length > MAX_FILES) {
      alert(`Maximum ${MAX_FILES} files allowed. You have ${selectedFiles.length} selected.`);
      return;
    }
    const newFiles = pdfFiles.filter(nf => !selectedFiles.some(ef => ef.name === nf.name && ef.size === nf.size));
    setSelectedFiles(prev => [...prev, ...newFiles]);
    setFilesDone(false);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) handleFiles(e.target.files);
    e.target.value = '';
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setFileProgress(prev => prev.filter((_, i) => i !== index));
  };

  const showProgress = isProcessing || filesDone;

  return (
    <div className="space-y-3">
      {/* Drop zone */}
      <div
        className={`border-2 border-dashed rounded-xl transition-colors ${
          dragActive ? 'border-blue-400 bg-blue-50/40' : 'border-slate-200 hover:border-slate-300'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file" accept=".pdf" multiple
          onChange={handleFileInput}
          className="hidden" id="batch-pdf-upload"
          disabled={isProcessing || selectedFiles.length >= MAX_FILES}
        />
        <label
          htmlFor="batch-pdf-upload"
          className={`flex items-center gap-3 px-5 py-4 cursor-pointer ${
            isProcessing || selectedFiles.length >= MAX_FILES ? 'cursor-not-allowed opacity-50' : ''
          }`}
        >
          <Plus className={`w-4 h-4 shrink-0 ${dragActive ? 'text-blue-500' : 'text-slate-400'}`} />
          <span className="text-sm text-slate-500">
            {selectedFiles.length === 0
              ? `Drag & drop or click to add PDFs (max ${MAX_FILES})`
              : selectedFiles.length >= MAX_FILES
              ? `${MAX_FILES}/${MAX_FILES} files — limit reached`
              : `${selectedFiles.length}/${MAX_FILES} — add more`}
          </span>
        </label>
      </div>

      {/* File list */}
      {selectedFiles.length > 0 && (
        <div className="space-y-1.5">
          {selectedFiles.map((file, i) => {
            const progress = fileProgress[i] ?? 0;
            const done = filesDone && progress === 100;
            return (
              <div key={i} className="bg-slate-50 rounded-lg px-3 py-2.5 border border-slate-100">
                <div className="flex items-center gap-2">
                  {done
                    ? <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    : isProcessing
                    ? <Loader2 className="w-4 h-4 text-blue-500 shrink-0 animate-spin" />
                    : <FileText className="w-4 h-4 text-slate-400 shrink-0" />}
                  <span className="text-sm text-slate-700 truncate flex-1" title={file.name}>{file.name}</span>
                  <span className="text-xs text-slate-400 shrink-0">{(file.size / 1024 / 1024).toFixed(1)} MB</span>
                  {!isProcessing && !filesDone && (
                    <button onClick={() => removeFile(i)} className="text-slate-300 hover:text-red-500 p-0.5 shrink-0 transition-colors">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                  {showProgress && !done && (
                    <span className="text-xs font-medium text-blue-600 w-8 text-right shrink-0">{Math.round(progress)}%</span>
                  )}
                </div>
                {showProgress && (
                  <div className="mt-1.5 w-full bg-slate-200 rounded-full h-1">
                    <div
                      className={`h-1 rounded-full transition-all duration-300 ${done ? 'bg-emerald-500' : 'bg-blue-500'}`}
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Analyze button */}
      <button
        onClick={() => { if (selectedFiles.length === 0) { alert('Please select at least one PDF.'); return; } onBatchAnalysis(selectedFiles); }}
        disabled={selectedFiles.length === 0 || isProcessing}
        className={`w-full py-2.5 px-4 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-colors ${
          selectedFiles.length === 0 || isProcessing
            ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {isProcessing
          ? <><Loader2 className="w-4 h-4 animate-spin" />Processing {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''}…</>
          : <><BarChart3 className="w-4 h-4" />Analyze {selectedFiles.length || ''} File{selectedFiles.length !== 1 ? 's' : ''}</>}
      </button>
    </div>
  );
};

export default BatchUploadSection;
