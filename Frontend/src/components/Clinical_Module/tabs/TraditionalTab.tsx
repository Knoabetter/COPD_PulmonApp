import { BookOpen, CheckCircle } from 'lucide-react';
import { t } from '../../../translations';

const TraditionalTab = ({ analysisResults }) => {
  const traditionalResults = analysisResults.clinical_interpretation?.traditional;

  if (!traditionalResults) {
    return (
      <div className="bg-white border rounded-lg p-6">
        <p className="text-gray-500">{t.tradNotAvailable}</p>
      </div>
    );
  }

  const getGoldColor = (severity) => {
    if (severity?.includes('GOLD 1')) return 'bg-green-100 text-green-800 border-green-200';
    if (severity?.includes('GOLD 2')) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    if (severity?.includes('GOLD 3')) return 'bg-orange-100 text-orange-800 border-orange-200';
    if (severity?.includes('GOLD 4')) return 'bg-red-100 text-red-800 border-red-200';
    if (severity?.includes('Normal')) return 'bg-gray-100 text-gray-800 border-gray-200';
    return 'bg-gray-100 text-gray-800 border-gray-200';
  };

  return (
    <div className="space-y-6">
      <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <BookOpen className="w-6 h-6 text-orange-600 mr-2" />
          <h3 className="text-lg font-semibold text-orange-900">{t.tradTabTitle}</h3>
        </div>
        <p className="text-orange-700 text-sm">{t.tradTabDesc}</p>
      </div>

      <div className="bg-white border rounded-lg p-6">
        <h4 className="text-md font-semibold mb-4">{t.tradGoldAssessment}</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className={`p-4 rounded-lg border ${getGoldColor(traditionalResults.severity)}`}>
            <div className="flex items-center justify-between">
              <span className="font-medium">{t.tradPatternLabel}</span>
              <span className="font-semibold">{traditionalResults.primary_pattern}</span>
            </div>
          </div>
          <div className={`p-4 rounded-lg border ${getGoldColor(traditionalResults.severity)}`}>
            <div className="flex items-center justify-between">
              <span className="font-medium">{t.tradSeverityLabel}</span>
              <span className="font-semibold">{traditionalResults.severity}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border rounded-lg p-6">
        <h4 className="text-md font-semibold mb-4">{t.tradClinicalNotes}</h4>
        <div className="space-y-2">
          {traditionalResults.clinical_notes?.map((note, index) => (
            <div key={index} className="flex items-start space-x-2">
              <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700">{note}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TraditionalTab;
