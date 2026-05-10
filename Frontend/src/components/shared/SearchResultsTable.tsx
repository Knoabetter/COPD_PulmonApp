import { FileText } from 'lucide-react';
import { t } from '../../translations';

interface SearchRow {
  id: string | number;
  date_pre?: string;
  fev1_pre?: number | null;
  fvc_pre?: number | null;
  fev1_fvc_pre?: number | null;
  diagnosis?: string | null;
  [key: string]: unknown;
}

const diagnosisBadge = (diagnosis?: string | null) => {
  if (!diagnosis) return <span className="text-slate-400">—</span>;
  const lc = diagnosis.toLowerCase();
  const cls = lc.includes('copd') || lc.includes('obstruct')
    ? 'bg-red-100 text-red-800 border-red-200'
    : lc.includes('borderline')
    ? 'bg-amber-100 text-amber-800 border-amber-200'
    : lc.includes('normal')
    ? 'bg-emerald-100 text-emerald-800 border-emerald-200'
    : 'bg-slate-100 text-slate-700 border-slate-200';
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-semibold border ${cls}`}>
      {diagnosis}
    </span>
  );
};

const SearchResultsTable = ({ searchResults }: { searchResults: SearchRow[] }) => {
  if (!searchResults || searchResults.length === 0) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      <div className="px-5 py-3.5 border-b border-slate-100 bg-slate-50 flex items-center gap-2.5">
        <FileText className="w-4 h-4 text-slate-400" />
        <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">
          {t.searchResults}
          <span className="ms-2 px-2 py-0.5 rounded-full bg-slate-200 text-slate-600 text-xs font-bold">{searchResults.length}</span>
        </h3>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-100">
              <th className="px-5 py-3 text-start">{t.colPatientId}</th>
              <th className="px-4 py-3 text-start">{t.colDate}</th>
              <th className="px-4 py-3 text-end">{t.colFev1}</th>
              <th className="px-4 py-3 text-end">{t.colFvc}</th>
              <th className="px-4 py-3 text-end">{t.colRatio}</th>
              <th className="px-4 py-3 text-start">{t.colDiagnosis}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {searchResults.map((test, i) => (
              <tr key={i} className="hover:bg-slate-50/60">
                <td className="px-5 py-3 font-semibold text-slate-900">{test.id}</td>
                <td className="px-4 py-3 text-slate-500">{test.date_pre || '—'}</td>
                <td className="px-4 py-3 text-end font-mono text-slate-700">{test.fev1_pre?.toFixed(2) ?? '—'}</td>
                <td className="px-4 py-3 text-end font-mono text-slate-700">{test.fvc_pre?.toFixed(2) ?? '—'}</td>
                <td className="px-4 py-3 text-end font-mono text-slate-700">{test.fev1_fvc_pre?.toFixed(3) ?? '—'}</td>
                <td className="px-4 py-3">{diagnosisBadge(test.diagnosis)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SearchResultsTable;
