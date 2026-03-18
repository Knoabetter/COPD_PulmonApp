import { useState } from 'react';
import { AlertCircle, CheckCircle2, X } from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  suggestions?: {
    severity?: string;
    criteria_met?: string[];
    [key: string]: unknown;
  } | null;
  onConfirm: (severity: string, criteria: unknown) => void;
  onDecline: (customDiagnosis: string) => void;
}

const DiagnosisModal = ({ isOpen, onClose, suggestions, onConfirm, onDecline }: Props) => {
  const [customDiagnosis, setCustomDiagnosis] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);

  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm(suggestions?.severity ?? '', suggestions?.criteria_met);
    onClose();
  };

  const handleCustomSubmit = () => {
    if (customDiagnosis.trim()) {
      onDecline(customDiagnosis);
      onClose();
      setCustomDiagnosis('');
      setShowCustomInput(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md border border-slate-200 overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 text-orange-500" />
            <h3 className="text-base font-bold text-slate-900">Obstructive Pattern Detected</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-4">
          <p className="text-sm text-slate-600">
            An obstructive ventilatory defect was identified. Suggested classification:
          </p>

          <div className="bg-orange-50 border border-orange-200 rounded-xl px-4 py-4">
            <p className="text-sm font-bold text-orange-900 capitalize mb-2">
              {suggestions?.severity ?? '—'} severity
            </p>
            {suggestions?.criteria_met && suggestions.criteria_met.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-orange-800 uppercase tracking-wide mb-1.5">Criteria met:</p>
                <ul className="space-y-1">
                  {suggestions.criteria_met.map((c, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-orange-700">
                      <span className="mt-1 w-1 h-1 rounded-full bg-orange-500 shrink-0" />
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <p className="text-xs text-slate-400 italic">
            Confirm to save this diagnosis to the database, or enter a custom classification.
          </p>
        </div>

        {/* Actions */}
        <div className="px-6 pb-6 space-y-3">
          {!showCustomInput ? (
            <div className="flex gap-3">
              <button
                onClick={handleConfirm}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 transition-colors"
              >
                <CheckCircle2 className="w-4 h-4" /> Confirm & Save
              </button>
              <button
                onClick={() => setShowCustomInput(true)}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl text-sm font-semibold hover:bg-slate-50 transition-colors"
              >
                <X className="w-4 h-4" /> Enter Custom
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wide">
                  Custom diagnosis:
                </label>
                <input
                  type="text"
                  value={customDiagnosis}
                  onChange={e => setCustomDiagnosis(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleCustomSubmit()}
                  placeholder="e.g. Normal post-BD, Non-specific pattern…"
                  className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400"
                  autoFocus
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleCustomSubmit}
                  disabled={!customDiagnosis.trim()}
                  className="flex-1 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 disabled:bg-slate-100 disabled:text-slate-400 disabled:cursor-not-allowed transition-colors"
                >
                  Save Diagnosis
                </button>
                <button
                  onClick={() => { setShowCustomInput(false); setCustomDiagnosis(''); }}
                  className="px-4 py-2.5 bg-white border border-slate-200 text-slate-600 rounded-xl text-sm font-semibold hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DiagnosisModal;
