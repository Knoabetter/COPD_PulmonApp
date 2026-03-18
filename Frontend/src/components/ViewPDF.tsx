import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { ZoomIn, ZoomOut, RotateCw, Download, Maximize2, Minimize2, RefreshCw, AlertCircle, FileText } from 'lucide-react';
import workerSrc from "pdfjs-dist/build/pdf.worker.min.mjs?url";
pdfjs.GlobalWorkerOptions.workerSrc = workerSrc;

interface ViewPDFProps {
  pdfUrl?: string;
  filename?: string;
  isLoading?: boolean;
  onLoadSuccess?: (numPages: number) => void;
  onLoadError?: (error: Error) => void;
  className?: string;
}

const ViewPDF: React.FC<ViewPDFProps> = ({ 
  pdfUrl, 
  filename, 
  isLoading = false,
  onLoadSuccess,
  onLoadError,
  className = ""
}) => {
  // State management
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [rotation, setRotation] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isRetrying, setIsRetrying] = useState(false);
  const [workerError, setWorkerError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  
  // Refs
  const containerRef = useRef<HTMLDivElement>(null);
  const documentRef = useRef<any>(null);

  // Maximum retry attempts
  const MAX_RETRIES = 3;

  // Enhanced document load success handler
  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    console.log(`✅ PDF loaded successfully: ${numPages} pages`);
    setNumPages(numPages);
    setLoadError(null);
    setWorkerError(false);
    setRetryCount(0);
    setIsRetrying(false);
    
    // Call parent callback if provided
    if (onLoadSuccess) {
      onLoadSuccess(numPages);
    }
  }, [onLoadSuccess]);

  // Enhanced document load error handler
  const onDocumentLoadError = useCallback((error: Error) => {
    console.error('❌ PDF load error:', error);
    
    let errorMessage = 'Failed to load PDF document.';
    
    // Categorize error types for better user feedback
    if (error.message.includes('PDF.js')) {
      errorMessage = 'PDF rendering engine error. Please try refreshing the page.';
      setWorkerError(true);
    } else if (error.message.includes('fetch') || error.message.includes('network')) {
      errorMessage = 'Network error loading PDF. Please check your connection.';
    } else if (error.message.includes('Invalid PDF')) {
      errorMessage = 'Invalid or corrupted PDF file.';
    } else if (error.message.includes('password')) {
      errorMessage = 'Password-protected PDF files are not supported.';
    } else if (error.message.includes('CORS')) {
      errorMessage = 'PDF access blocked. Please contact support.';
    }
    
    setLoadError(errorMessage);
    setIsRetrying(false);
    
    // Call parent callback if provided
    if (onLoadError) {
      onLoadError(error);
    }
  }, [onLoadError]);

  // Enhanced retry mechanism
  const handleRetry = useCallback(async () => {
    if (retryCount >= MAX_RETRIES) {
      setLoadError('Maximum retry attempts reached. Please refresh the page or contact support.');
      return;
    }

    setIsRetrying(true);
    setLoadError(null);

    try {
      if (workerError) {
        console.log('🔄 Reconfiguring PDF worker...');
        pdfjs.GlobalWorkerOptions.workerSrc = workerSrc;
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      setRetryCount(prev => prev + 1);

      if (documentRef.current) {
        documentRef.current.forceUpdate?.();
      }

    } catch (error) {
      console.error('Retry failed:', error);
      setLoadError('Retry failed. Please refresh the page.');
      setIsRetrying(false);
    }
  }, [retryCount, workerError]);

  // Zoom controls
  const handleZoomIn = useCallback(() => {
    setScale(prev => Math.min(prev + 0.25, 3.0));
  }, []);

  const handleZoomOut = useCallback(() => {
    setScale(prev => Math.max(prev - 0.25, 0.5));
  }, []);

  const handleRotate = useCallback(() => {
    setRotation(prev => (prev + 90) % 360);
  }, []);

  const handleReset = useCallback(() => {
    setScale(1.0);
    setRotation(0);
    setPageNumber(1);
  }, []);

  // Page navigation
  const handlePrevPage = useCallback(() => {
    setPageNumber(prev => Math.max(prev - 1, 1));
  }, []);

  const handleNextPage = useCallback(() => {
    setPageNumber(prev => Math.min(prev + 1, numPages || 1));
  }, [numPages]);

  // Download handler with error handling
  const handleDownload = useCallback(async () => {
    if (!pdfUrl) return;
    
    try {
      // Check if URL is accessible
      const response = await fetch(pdfUrl, { method: 'HEAD' });
      if (!response.ok) {
        throw new Error(`Download failed: ${response.status}`);
      }
      
      const link = document.createElement('a');
      link.href = pdfUrl;
      link.download = filename || 'spirometry-report.pdf';
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again or contact support.');
    }
  }, [pdfUrl, filename]);

  // Fullscreen toggle
  const toggleFullscreen = useCallback(() => {
    setIsFullscreen(prev => !prev);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!isFullscreen) return;
      
      switch (event.key) {
        case 'Escape':
          setIsFullscreen(false);
          break;
        case 'ArrowLeft':
        case 'PageUp':
          handlePrevPage();
          break;
        case 'ArrowRight':
        case 'PageDown':
          handleNextPage();
          break;
        case '=':
        case '+':
          handleZoomIn();
          break;
        case '-':
          handleZoomOut();
          break;
        case '0':
          handleReset();
          break;
      }
    };

    if (isFullscreen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isFullscreen, handlePrevPage, handleNextPage, handleZoomIn, handleZoomOut, handleReset]);

  // Loading state
  if (isLoading) {
    return (
      <div className={`h-full flex items-center justify-center bg-slate-50 rounded-xl ${className}`}>
        <div className="text-center">
          <img
            src="/images/analyzing.gif"
            alt="Analyzing..."
            className="w-96 h-96 object-contain mx-auto"
          />
          <p className="text-slate-500 mt-2 text-sm">Analyzing spirometry report…</p>
        </div>
      </div>
    );
  }

  // No PDF state
  if (!pdfUrl) {
    return (
      <div className={`h-full flex items-center justify-center bg-slate-50 rounded-xl ${className}`}>
        <div className="text-center text-slate-400">
          <div className="w-14 h-14 mx-auto mb-4 bg-slate-200 rounded-xl flex items-center justify-center">
            <FileText className="w-7 h-7 text-slate-400" />
          </div>
          <p className="font-semibold text-slate-600">No PDF loaded</p>
          <p className="text-sm mt-1 text-slate-400">Upload a spirometry report to view it here</p>
        </div>
      </div>
    );
  }

  const iconBtn = 'p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors';

  return (
    <div
      ref={containerRef}
      className={`flex flex-col h-full bg-white border border-slate-200 rounded-xl ${
        isFullscreen ? 'fixed inset-0 z-50 rounded-none border-0' : ''
      } ${className}`}
    >
      {/* Toolbar */}
      <div className="flex items-center justify-between px-3 py-2.5 border-b border-slate-100 bg-slate-50 flex-shrink-0 gap-2">
        <div className="flex items-center gap-1">
          <button onClick={handleZoomOut} disabled={scale <= 0.5} className={iconBtn} title="Zoom out">
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-xs font-mono px-2 py-1 bg-white border border-slate-200 rounded-md min-w-[3.5rem] text-center text-slate-700">
            {Math.round(scale * 100)}%
          </span>
          <button onClick={handleZoomIn} disabled={scale >= 3.0} className={iconBtn} title="Zoom in">
            <ZoomIn className="w-4 h-4" />
          </button>

          <div className="w-px h-4 bg-slate-200 mx-1" />

          <button onClick={handleRotate} className={iconBtn} title="Rotate 90°">
            <RotateCw className="w-4 h-4" />
          </button>
          <button
            onClick={handleReset}
            className="px-2.5 py-1 text-xs font-semibold bg-white border border-slate-200 text-slate-600 hover:bg-slate-100 rounded-md transition-colors"
            title="Reset view"
          >
            Reset
          </button>
        </div>

        <div className="flex items-center gap-1">
          {filename && (
            <span className="text-xs text-slate-400 truncate max-w-[180px] mr-1" title={filename}>
              {filename}
            </span>
          )}
          <button onClick={handleDownload} className={iconBtn} title="Download PDF">
            <Download className="w-4 h-4" />
          </button>
          <button onClick={toggleFullscreen} className={iconBtn} title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}>
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* PDF Content Area */}
      <div className="flex-1 overflow-auto bg-slate-100">
        {loadError ? (
          <div className="h-full flex items-center justify-center p-8">
            <div className="text-center max-w-sm">
              <div className="w-14 h-14 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="w-7 h-7 text-red-500" />
              </div>
              <h3 className="text-base font-semibold text-slate-800 mb-1">Unable to load PDF</h3>
              <p className="text-sm text-red-600 mb-4">{loadError}</p>
              <div className="space-y-2">
                {retryCount < MAX_RETRIES && (
                  <button
                    onClick={handleRetry}
                    disabled={isRetrying}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isRetrying ? (
                      <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />Retrying…</>
                    ) : (
                      <><RefreshCw className="w-4 h-4" />Retry ({retryCount}/{MAX_RETRIES})</>
                    )}
                  </button>
                )}
                <button
                  onClick={() => window.location.reload()}
                  className="block w-full px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-semibold transition-colors"
                >
                  Refresh page
                </button>
                {workerError && (
                  <p className="text-xs text-slate-500 mt-2">
                    If problems persist, try a different browser or disable ad blockers.
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex justify-center p-4">
            <Document
              ref={documentRef}
              file={pdfUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={
                <div className="flex items-center justify-center p-8">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2" />
                    <p className="text-sm text-slate-500">Loading PDF…</p>
                  </div>
                </div>
              }
              error={
                <div className="flex items-center justify-center p-8">
                  <div className="text-center text-red-500">
                    <AlertCircle className="w-8 h-8 mx-auto mb-2" />
                    <p className="text-sm">Failed to load PDF</p>
                  </div>
                </div>
              }
            >
              <Page
                pageNumber={pageNumber}
                scale={scale}
                rotate={rotation}
                renderTextLayer={false}
                renderAnnotationLayer={false}
                className="shadow-md"
                loading={
                  <div className="animate-pulse bg-slate-200 w-full h-96 rounded-lg" />
                }
                error={
                  <div className="flex items-center justify-center p-4 border border-red-200 rounded-lg bg-red-50">
                    <div className="text-center text-red-500">
                      <AlertCircle className="w-6 h-6 mx-auto mb-1" />
                      <p className="text-sm">Page rendering failed</p>
                    </div>
                  </div>
                }
              />
            </Document>
          </div>
        )}
      </div>

      {/* Page Navigation */}
      {numPages && numPages > 1 && !loadError && (
        <div className="flex items-center justify-between px-4 py-2.5 border-t border-slate-100 bg-slate-50 flex-shrink-0">
          <button
            onClick={handlePrevPage}
            disabled={pageNumber <= 1}
            className="px-3 py-1.5 bg-white border border-slate-200 text-slate-700 rounded-lg text-sm font-semibold hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            ← Prev
          </button>

          <div className="flex items-center gap-2 text-sm text-slate-500">
            <span>Page</span>
            <input
              type="number"
              min={1}
              max={numPages}
              value={pageNumber}
              onChange={e => {
                const page = parseInt(e.target.value);
                if (page >= 1 && page <= numPages) setPageNumber(page);
              }}
              className="w-14 px-2 py-1 text-sm text-center border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <span>of {numPages}</span>
          </div>

          <button
            onClick={handleNextPage}
            disabled={pageNumber >= numPages}
            className="px-3 py-1.5 bg-white border border-slate-200 text-slate-700 rounded-lg text-sm font-semibold hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Next →
          </button>
        </div>
      )}

      {isFullscreen && (
        <div className="absolute top-4 right-4 bg-slate-900/80 text-white px-3 py-1.5 rounded-lg text-xs font-medium">
          Press ESC to exit
        </div>
      )}
    </div>
  );
};

export default ViewPDF;