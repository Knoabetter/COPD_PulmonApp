import { BarChart3, FileText, Download } from 'lucide-react';
import { t } from '../../translations';

interface BatchResult {
  filename: string;
  success?: boolean;
  error?: string;
  patient_info?: { age?: number; sex?: string; height?: number };
  measured_values?: { 'FEV 1 % FVC_PRE'?: number; [key: string]: unknown };
  diagnosis?: string;
  severity?: string;
  [key: string]: unknown;
}

const statusBadge = (success: boolean | undefined) =>
  success
    ? <span className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">{t.statusOk}</span>
    : <span className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800 border border-red-200">{t.statusFailed}</span>;

const diagnosisBadge = (diagnosis?: string) => {
  if (!diagnosis) return <span className="text-slate-400">—</span>;
  const lc = diagnosis.toLowerCase();
  const cls = lc.includes('copd') || lc.includes('obstruct')
    ? 'bg-red-100 text-red-800 border-red-200'
    : lc.includes('borderline')
    ? 'bg-amber-100 text-amber-800 border-amber-200'
    : 'bg-emerald-100 text-emerald-800 border-emerald-200';
  return <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-semibold border ${cls}`}>{diagnosis}</span>;
};

const severityBadge = (severity?: string) => {
  if (!severity) return null;
  const colors: Record<string, string> = {
    mild: 'bg-amber-100 text-amber-800 border-amber-200',
    moderate: 'bg-orange-100 text-orange-800 border-orange-200',
    severe: 'bg-red-100 text-red-800 border-red-200',
    'very severe': 'bg-red-200 text-red-900 border-red-300',
  };
  return <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-semibold border ${colors[severity] ?? 'bg-slate-100 text-slate-700 border-slate-200'}`}>{severity}</span>;
};

const BatchResultsTable = ({ batchResults, onViewResult }: {
  batchResults: BatchResult[];
  onViewResult?: (result: BatchResult) => void;
}) => {
  if (!batchResults || batchResults.length === 0) return null;

  const successful  = batchResults.filter(r => r.success);
  const failed      = batchResults.filter(r => !r.success);
  const copdCases   = successful.filter(r => r.diagnosis?.toLowerCase().includes('copd'));
  const borderline  = successful.filter(r => r.diagnosis?.toLowerCase().includes('borderline'));

  const exportCSV = () => {
    const rows = batchResults.map(r => [
      r.filename, r.success ? 'OK' : 'Failed',
      r.patient_info?.age ?? '', r.patient_info?.sex ?? '', r.patient_info?.height ?? '',
      r.measured_values?.['FEV 1 % FVC_PRE']?.toFixed(3) ?? '',
      r.diagnosis ?? '', r.severity ?? '', r.error ?? '',
    ].join(','));
    const csv = 'data:text/csv;charset=utf-8,Filename,Status,Age,Sex,Height,FEV1/FVC,Diagnosis,Severity,Error\n' + rows.join('\n');
    const a = document.createElement('a');
    a.setAttribute('href', encodeURI(csv));
    a.setAttribute('download', `batch_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
  };

  const exportJSON = () => {
    const json = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(batchResults, null, 2));
    const a = document.createElement('a');
    a.setAttribute('href', json);
    a.setAttribute('download', `batch_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
  };

  return (
    <div className="space-y-4">
      {/* Summary strip */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="px-5 py-3.5 border-b border-slate-100 bg-slate-50 flex items-center gap-2.5">
          <BarChart3 className="w-4 h-4 text-slate-400" />
          <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">{t.batchSummary}</h3>
          <span className="ms-auto text-xs text-slate-400">{batchResults.length} {batchResults.length !== 1 ? t.colFile + 's' : t.colFile}</span>
        </div>
        <div className="px-6 py-4 grid grid-cols-2 sm:grid-cols-5 gap-4">
          {[
            { val: batchResults.length, label: t.total,      color: 'text-blue-700' },
            { val: successful.length,   label: t.successful, color: 'text-emerald-700' },
            { val: failed.length,       label: t.failed,     color: 'text-red-700' },
            { val: copdCases.length,    label: t.copd,       color: 'text-orange-700' },
            { val: borderline.length,   label: t.borderline, color: 'text-amber-700' },
          ].map(s => (
            <div key={s.label} className="text-center">
              <div className={`text-xl font-bold ${s.color}`}>{s.val}</div>
              <div className="text-xs text-slate-500 mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Results table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-100">
                <th className="px-5 py-3 text-start">{t.colFile}</th>
                <th className="px-4 py-3 text-start">{t.colStatus}</th>
                <th className="px-4 py-3 text-start">{t.colPatient}</th>
                <th className="px-4 py-3 text-end">{t.colFev1Fvc}</th>
                <th className="px-4 py-3 text-start">{t.colDiagnosis}</th>
                <th className="px-4 py-3 text-start">{t.colSeverity}</th>
                {onViewResult && <th className="px-4 py-3 text-start">{t.colAction}</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {batchResults.map((r, i) => {
                const ratio = r.success ? r.measured_values?.['FEV 1 % FVC_PRE'] : undefined;
                const diag  = r.diagnosis ?? (ratio != null ? (ratio < 0.70 ? 'COPD (Obstructive)' : ratio < 0.75 ? 'Borderline' : 'Normal') : undefined);
                return (
                  <tr key={i} className="hover:bg-slate-50/60">
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                        <span className="font-medium text-slate-800 truncate max-w-[180px]" title={r.filename}>{r.filename}</span>
                      </div>
                      {!r.success && r.error && (
                        <p className="text-xs text-red-600 mt-0.5 ps-6 truncate" title={r.error}>{r.error}</p>
                      )}
                    </td>
                    <td className="px-4 py-3">{statusBadge(r.success)}</td>
                    <td className="px-4 py-3">
                      {r.success && r.patient_info
                        ? <div className="text-slate-700"><span className="font-semibold">{r.patient_info.age}y</span> {r.patient_info.sex}<span className="text-slate-400 text-xs ms-1">{r.patient_info.height}cm</span></div>
                        : <span className="text-slate-400">—</span>}
                    </td>
                    <td className="px-4 py-3 text-end font-mono font-semibold text-slate-700">{ratio != null ? ratio.toFixed(3) : '—'}</td>
                    <td className="px-4 py-3">{diagnosisBadge(diag)}</td>
                    <td className="px-4 py-3">{severityBadge(r.severity)}</td>
                    {onViewResult && (
                      <td className="px-4 py-3">
                        {r.success
                          ? <button onClick={() => onViewResult(r)} className="text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors">{t.viewResult}</button>
                          : null}
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="px-5 py-3.5 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
          <span className="text-xs text-slate-400">
            {t.generated} {new Date().toLocaleString()}
          </span>
          <div className="flex gap-2">
            <button onClick={exportCSV} className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-100 transition-colors">
              <Download className="w-3.5 h-3.5" />CSV
            </button>
            <button onClick={exportJSON} className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-100 transition-colors">
              <Download className="w-3.5 h-3.5" />JSON
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BatchResultsTable;
