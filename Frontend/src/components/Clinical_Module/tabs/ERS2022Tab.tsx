import { Shield, CheckCircle, FlaskConical } from 'lucide-react';
import ExtendedPFTDisplay from './ExtendedPFTDisplay';
import { t } from '../../../translations';

const ERS2022Tab = ({ analysisResults }) => {
  const ers2022Results = analysisResults.clinical_interpretation?.ers2022;

  if (!ers2022Results) {
    return (
      <div className="bg-white border rounded-lg p-6">
        <p className="text-gray-500">{t.ersNotAvailable}</p>
      </div>
    );
  }

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'normal':     return 'bg-green-100 text-green-800 border-green-200';
      case 'borderline': return 'bg-yellow-50 text-yellow-800 border-yellow-200';
      case 'mild':       return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'moderate':   return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'severe':     return 'bg-red-100 text-red-800 border-red-200';
      default:           return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const hasRestriction = ers2022Results.primary_pattern?.toLowerCase().includes('restriction')
    || ers2022Results.primary_pattern?.toLowerCase().includes('non-specific')
    || ers2022Results.primary_pattern?.toLowerCase().includes('mixed')
    || (ers2022Results.secondary_findings ?? []).some((f: string) => f.includes('TLC'));

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Shield className="w-6 h-6 text-blue-600 mr-2" />
          <h3 className="text-lg font-semibold text-blue-900">{t.ersTabTitle}</h3>
        </div>
        <p className="text-blue-700 text-sm">{t.ersTabDesc}</p>
        <p className="text-blue-600 text-xs mt-2 border-t border-blue-200 pt-2">
          <strong>Ethnic equity note:</strong> {t.ersEthnicNote}
        </p>
      </div>

      <div className="bg-white border rounded-lg p-6">
        <h4 className="text-md font-semibold mb-4">{t.ersPrimaryPattern}</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className={`p-4 rounded-lg border ${getSeverityColor(ers2022Results.severity)}`}>
            <div className="flex items-center justify-between">
              <span className="font-medium">{t.ersPatternLabel}</span>
              <span className="font-semibold">{ers2022Results.primary_pattern}</span>
            </div>
          </div>
          <div className={`p-4 rounded-lg border ${getSeverityColor(ers2022Results.severity)}`}>
            <div className="flex items-center justify-between">
              <span className="font-medium">{t.ersSeverityLabel}</span>
              <span className="font-semibold">{ers2022Results.severity}</span>
            </div>
          </div>
        </div>

        {ers2022Results.fvc_z_score != null && (
          <div className="bg-orange-50 border border-orange-200 rounded-lg px-4 py-3 mt-3 flex items-baseline gap-3">
            <span className="text-sm font-semibold text-orange-900">
              FVC Z-score: {Number(ers2022Results.fvc_z_score).toFixed(2)}
            </span>
            <span className="text-sm text-orange-700">— {ers2022Results.severity} restriction</span>
          </div>
        )}
      </div>

      {hasRestriction && (
        <div className="flex items-start gap-2 bg-amber-50 border border-amber-300 rounded-lg px-4 py-3">
          <FlaskConical className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
          <div>
            <p className="text-sm font-semibold text-amber-900">{t.ersTlcNote}</p>
            <p className="text-xs text-amber-700 mt-0.5">{t.ersTlcDesc}</p>
          </div>
        </div>
      )}

      <div className="bg-white border rounded-lg p-6">
        <h4 className="text-md font-semibold mb-4">{t.ersClinicalNotes}</h4>
        <div className="space-y-2">
          {ers2022Results.clinical_notes?.map((note, index) => (
            <div key={index} className="flex items-start space-x-2">
              <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700">{note}</span>
            </div>
          ))}
        </div>
      </div>

      <ExtendedPFTDisplay clinicalInterpretation={analysisResults.clinical_interpretation} />
    </div>
  );
};

export default ERS2022Tab;
