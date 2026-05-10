import { Stethoscope, BarChart3, Activity, AlertTriangle } from 'lucide-react';
import { t } from '../../../translations';

const ExtendedPFTDisplay = ({ clinicalInterpretation }) => {
  if (!clinicalInterpretation?.has_extended_data) return null;

  const lungVolumes = clinicalInterpretation.lung_volumes;
  const gasTransfer = clinicalInterpretation.gas_transfer;
  const completeSummary = clinicalInterpretation.complete_summary;

  const getPatternColor = (pattern) => {
    if (pattern?.toLowerCase().includes('normal'))        return 'text-green-600';
    if (pattern?.toLowerCase().includes('restrictive'))   return 'text-orange-600';
    if (pattern?.toLowerCase().includes('hyperinflation')) return 'text-red-600';
    if (pattern?.toLowerCase().includes('reduced'))       return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getValueBgColor = (value) => {
    if (value < 80)  return 'bg-red-50 border-red-200';
    if (value > 120) return 'bg-orange-50 border-orange-200';
    return 'bg-green-50 border-green-200';
  };

  const fmtAbs = (v) => (v != null ? Number(v).toFixed(2) : null);
  const fmtPct = (v) => (v != null ? `${Number(v).toFixed(1)}%` : null);

  return (
    <div className="space-y-6 mt-6">
      {completeSummary && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-3 flex items-center">
            <Stethoscope className="w-4 h-4 mr-1.5" />
            {t.extIntegratedTitle}
          </h3>

          <div className="flex flex-wrap items-baseline gap-3 mb-3">
            <span className={`text-base font-bold ${getPatternColor(completeSummary.overall_pattern)}`}>
              {completeSummary.overall_pattern}
            </span>
            {completeSummary.severity && completeSummary.severity !== 'Normal' && (
              <span className="text-sm text-gray-600">— {completeSummary.severity}</span>
            )}
          </div>

          {completeSummary.key_findings && completeSummary.key_findings.length > 0 && (() => {
            const clinical = completeSummary.key_findings.filter(
              (f: string) => f.length > 20 && !/^\s*(FEV1|FVC|TLC|RV|KCO|TLCO):\s*\d/.test(f)
            );
            return clinical.length > 0 ? (
              <ul className="space-y-1">
                {clinical.map((finding: string, index: number) => (
                  <li key={index} className="text-xs text-blue-800 flex items-start gap-1.5">
                    <span className="mt-0.5 shrink-0">•</span>
                    <span>{finding}</span>
                  </li>
                ))}
              </ul>
            ) : null;
          })()}
        </div>
      )}

      {lungVolumes && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            {t.extLungVolumes}
          </h3>

          <div className="mb-4">
            <div className="text-sm text-gray-600 mb-1">{t.extPatternLabel}</div>
            <div className={`font-semibold ${getPatternColor(lungVolumes.pattern)}`}>
              {lungVolumes.pattern}
            </div>
          </div>

          {lungVolumes.values && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              {lungVolumes.values['RV_%pred'] != null && (
                <div className={`p-3 border rounded-lg ${getValueBgColor(lungVolumes.values['RV_%pred'])}`}>
                  <div className="text-sm text-gray-600">RV</div>
                  {fmtAbs(lungVolumes.values['RV_meas']) && (
                    <div className="font-semibold text-lg">{fmtAbs(lungVolumes.values['RV_meas'])} L</div>
                  )}
                  <div className={`text-sm font-medium ${getValueBgColor(lungVolumes.values['RV_%pred']).includes('red') ? 'text-red-700' : getValueBgColor(lungVolumes.values['RV_%pred']).includes('orange') ? 'text-orange-700' : 'text-green-700'}`}>
                    {fmtPct(lungVolumes.values['RV_%pred'])} pred
                  </div>
                </div>
              )}
              {lungVolumes.values['TLC_%pred'] != null && (
                <div className={`p-3 border rounded-lg ${getValueBgColor(lungVolumes.values['TLC_%pred'])}`}>
                  <div className="text-sm text-gray-600">TLC</div>
                  {fmtAbs(lungVolumes.values['TLC_meas']) && (
                    <div className="font-semibold text-lg">{fmtAbs(lungVolumes.values['TLC_meas'])} L</div>
                  )}
                  <div className={`text-sm font-medium ${getValueBgColor(lungVolumes.values['TLC_%pred']).includes('red') ? 'text-red-700' : getValueBgColor(lungVolumes.values['TLC_%pred']).includes('orange') ? 'text-orange-700' : 'text-green-700'}`}>
                    {fmtPct(lungVolumes.values['TLC_%pred'])} pred
                  </div>
                </div>
              )}
              {lungVolumes.values['RV/TLC_%pred'] != null && (
                <div className={`p-3 border rounded-lg ${getValueBgColor(lungVolumes.values['RV/TLC_%pred'])}`}>
                  <div className="text-sm text-gray-600">RV/TLC</div>
                  {fmtAbs(lungVolumes.values['RV/TLC_meas']) && (
                    <div className="font-semibold text-lg">{fmtAbs(lungVolumes.values['RV/TLC_meas'])}</div>
                  )}
                  <div className={`text-sm font-medium ${getValueBgColor(lungVolumes.values['RV/TLC_%pred']).includes('red') ? 'text-red-700' : getValueBgColor(lungVolumes.values['RV/TLC_%pred']).includes('orange') ? 'text-orange-700' : 'text-green-700'}`}>
                    {fmtPct(lungVolumes.values['RV/TLC_%pred'])} pred
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {gasTransfer && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            {t.extGasTransfer}
          </h3>

          <div className="mb-4">
            <div className="text-sm text-gray-600 mb-1">{t.extPatternLabel}</div>
            <div className={`font-semibold ${getPatternColor(gasTransfer.pattern)}`}>
              {gasTransfer.pattern}
            </div>
          </div>

          {gasTransfer.values && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              {gasTransfer.values['TLCO_%pred'] != null && (
                <div className={`p-3 border rounded-lg ${getValueBgColor(gasTransfer.values['TLCO_%pred'])}`}>
                  <div className="text-sm text-gray-600">TLCO (DLCO)</div>
                  {fmtAbs(gasTransfer.values['TLCO_meas']) && (
                    <div className="font-semibold text-lg">{fmtAbs(gasTransfer.values['TLCO_meas'])} mmol/min/kPa</div>
                  )}
                  <div className={`text-sm font-medium ${getValueBgColor(gasTransfer.values['TLCO_%pred']).includes('red') ? 'text-red-700' : getValueBgColor(gasTransfer.values['TLCO_%pred']).includes('orange') ? 'text-orange-700' : 'text-green-700'}`}>
                    {fmtPct(gasTransfer.values['TLCO_%pred'])} pred
                  </div>
                </div>
              )}
              {gasTransfer.values['KCO_%pred'] != null && (
                <div className={`p-3 border rounded-lg ${getValueBgColor(gasTransfer.values['KCO_%pred'])}`}>
                  <div className="text-sm text-gray-600">KCO</div>
                  {fmtAbs(gasTransfer.values['KCO_meas']) && (
                    <div className="font-semibold text-lg">{fmtAbs(gasTransfer.values['KCO_meas'])} mmol/min/kPa/L</div>
                  )}
                  <div className={`text-sm font-medium ${getValueBgColor(gasTransfer.values['KCO_%pred']).includes('red') ? 'text-red-700' : getValueBgColor(gasTransfer.values['KCO_%pred']).includes('orange') ? 'text-orange-700' : 'text-green-700'}`}>
                    {fmtPct(gasTransfer.values['KCO_%pred'])} pred
                  </div>
                </div>
              )}
            </div>
          )}

          {gasTransfer.hb_correction_notice && (
            <div className="flex items-start gap-2 bg-yellow-50 border border-yellow-200 rounded-lg px-3 py-2 mt-1">
              <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5 shrink-0" />
              <p className="text-xs text-yellow-800">{gasTransfer.hb_correction_notice}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ExtendedPFTDisplay;
