import { useState } from 'react';
import { Search, Calendar, User, Loader2 } from 'lucide-react';
import { authFetch } from '../../utils/authFetch';
import { t } from '../../translations';

const API_BASE = import.meta.env.VITE_API_URL ?? '';

const SearchPanel = ({ onSearchResults }: { onSearchResults: (results: any[], type: string) => void }) => {
  const [searchType, setSearchType] = useState<'patient' | 'date'>('patient');
  const [patientId, setPatientId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState('');

  const handlePatientSearch = async () => {
    if (!patientId.trim()) return;
    setIsSearching(true);
    setError('');
    try {
      const response = await authFetch(`${API_BASE}/search/patient/${patientId}`);
      const data = await response.json();
      if (data.success) onSearchResults(data.tests, 'patient');
      else setError(data.error || t.noRecordsPatient);
    } catch {
      setError(t.networkError);
    } finally {
      setIsSearching(false);
    }
  };

  const handleDateRangeSearch = async () => {
    if (!startDate || !endDate) return;
    setIsSearching(true);
    setError('');
    try {
      const response = await authFetch(`${API_BASE}/search/date-range`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start_date: startDate, end_date: endDate }),
      });
      const data = await response.json();
      if (data.success) onSearchResults(data.tests, 'date');
      else setError(data.error || t.noRecordsDate);
    } catch {
      setError(t.networkError);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-slate-100 bg-slate-50 flex items-center gap-2.5">
        <Search className="w-4 h-4 text-slate-400" />
        <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">{t.searchPatientRecords}</h3>
      </div>

      <div className="p-5 space-y-4">
        {/* Type toggle */}
        <div className="flex gap-2">
          {(['patient', 'date'] as const).map(type => (
            <button
              key={type}
              onClick={() => { setSearchType(type); setError(''); }}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-semibold border-2 transition-all ${
                searchType === type
                  ? 'bg-slate-900 text-white border-slate-900'
                  : 'bg-white text-slate-500 border-slate-200 hover:border-slate-400 hover:text-slate-700'
              }`}
            >
              {type === 'patient' ? <User className="w-3.5 h-3.5" /> : <Calendar className="w-3.5 h-3.5" />}
              {type === 'patient' ? t.patientId : t.dateRange}
            </button>
          ))}
        </div>

        {/* Search form */}
        {searchType === 'patient' ? (
          <div className="flex gap-2">
            <input
              type="text"
              value={patientId}
              onChange={e => { setPatientId(e.target.value); setError(''); }}
              onKeyDown={e => e.key === 'Enter' && handlePatientSearch()}
              placeholder={t.enterPatientId}
              className="flex-1 px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400 placeholder-slate-400"
            />
            <button
              onClick={handlePatientSearch}
              disabled={isSearching || !patientId.trim()}
              className="flex items-center gap-1.5 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed transition-colors"
            >
              {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              {isSearching ? t.searching : t.search}
            </button>
          </div>
        ) : (
          <div className="flex flex-wrap items-center gap-2">
            <input
              type="date"
              value={startDate}
              onChange={e => { setStartDate(e.target.value); setError(''); }}
              className="px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400"
            />
            <span className="text-slate-400 text-sm">{t.dateTo}</span>
            <input
              type="date"
              value={endDate}
              onChange={e => { setEndDate(e.target.value); setError(''); }}
              className="px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400"
            />
            <button
              onClick={handleDateRangeSearch}
              disabled={isSearching || !startDate || !endDate}
              className="flex items-center gap-1.5 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed transition-colors"
            >
              {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              {isSearching ? t.searching : t.search}
            </button>
          </div>
        )}

        {error && (
          <p className="text-sm text-red-600 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-red-500 shrink-0" />{error}
          </p>
        )}
      </div>
    </div>
  );
};

export default SearchPanel;
