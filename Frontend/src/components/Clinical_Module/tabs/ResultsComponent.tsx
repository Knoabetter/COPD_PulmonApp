import React from 'react';
import { Activity } from 'lucide-react';
import { formatValue, getStatus, getColorClass } from '../utils';
import type { AnalysisResults } from '../types';

type ResultsComponentProps = {analysisResults: AnalysisResults | null;
};

const ResultsComponent: React.FC<ResultsComponentProps> = ({ analysisResults }) => {
  if (!analysisResults) return null;  const keyParams = [
    {
      name: 'FEV1',
      measured: analysisResults.measured?.FEV1,
      murrayPred: analysisResults.murray?.FEV1?.pred,
      gliPred: analysisResults.gli?.FEV1?.pred,
      unit: 'L'
    },
    {
      name: 'FVC', 
      measured: analysisResults.measured?.FVC,
      murrayPred: analysisResults.murray?.FVC?.pred,
      gliPred: analysisResults.gli?.FVC?.pred,
      unit: 'L'
    },
    {
      name: 'FEV1/FVC',
      measured: analysisResults.measured?.ratio,
      murrayPred: analysisResults.murray?.ratio?.pred,
      gliPred: analysisResults.gli?.ratio?.pred,
      unit: 'ratio'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Your Current Analysis Table */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Activity className="w-5 h-5 mr-2" />
          Key Lung Function Parameters
        </h3>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Parameter</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Measured</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Murray Pred</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">GLI Pred</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {keyParams.map((param) => {
                const murrayStatus = getStatus(param.measured, param.murrayPred);
                const gliStatus = getStatus(param.measured, param.gliPred);
                
                return (
                  <tr key={param.name} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{param.name}</td>
                    <td className={`px-4 py-3 text-sm font-bold`}>
                      {formatValue(param.measured)} {param.unit !== 'ratio' && param.unit}
                    </td>
                    <td className={`px-4 py-3 text-sm ${getColorClass(param.measured, param.murrayPred)}`}>
                      {formatValue(param.murrayPred)} {param.unit !== 'ratio' && param.unit}
                    </td>
                    <td className={`px-4 py-3 text-sm ${getColorClass(param.measured, param.gliPred)}`}>
                      {formatValue(param.gliPred)} {param.unit !== 'ratio' && param.unit}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex space-x-1">
                        <span className={`px-2 py-1 text-xs rounded-full ${murrayStatus.class}`}>
                          M: {murrayStatus.text}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${gliStatus.class}`}>
                          G: {gliStatus.text}
                        </span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default ResultsComponent ;