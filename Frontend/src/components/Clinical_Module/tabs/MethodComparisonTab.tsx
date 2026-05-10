import { BarChart3, AlertTriangle, CheckCircle, Activity } from 'lucide-react';
import ExtendedPFTDisplay from './ExtendedPFTDisplay';
import { t } from '../../../translations';

const pctColor = (pct?: number) => {
  if (pct == null) return 'text-slate-400';
  if (pct >= 100) return 'text-emerald-600 font-bold';
  if (pct >= 80)  return 'text-amber-600 font-semibold';
  return 'text-red-600 font-bold';
};

const MethodComparisonTab = ({ analysisResults }: { analysisResults: any }) => {
  const fmt = (value: any, dec = 3) =>
    value != null && !isNaN(value) ? Number(value).toFixed(dec) : 'N/A';

  const keyParams = [
    {
      name: 'FEV1',
      measured: analysisResults.measured?.FEV1,
      murrayPred: analysisResults.murray?.FEV1?.pred,
      murrayLLN:  analysisResults.murray?.FEV1?.lln,
      murrayPct:  analysisResults.murray?.FEV1?.percent,
      gliPred:    analysisResults.gli?.FEV1?.pred,
      gliLLN:     analysisResults.gli?.FEV1?.lln,
      gliPct:     analysisResults.gli?.FEV1?.percent,
      unit: 'L',
    },
    {
      name: 'FVC',
      measured: analysisResults.measured?.FVC,
      murrayPred: analysisResults.murray?.FVC?.pred,
      murrayLLN:  analysisResults.murray?.FVC?.lln,
      murrayPct:  analysisResults.murray?.FVC?.percent,
      gliPred:    analysisResults.gli?.FVC?.pred,
      gliLLN:     analysisResults.gli?.FVC?.lln,
      gliPct:     analysisResults.gli?.FVC?.percent,
      unit: 'L',
    },
    {
      name: 'FEV1/FVC',
      measured:   analysisResults.measured?.ratio,
      murrayPred: null,
      murrayLLN:  analysisResults.murray?.ratio?.lln,
      murrayPct:  null,
      gliPred:    null,
      gliLLN:     analysisResults.gli?.ratio?.lln,
      gliPct:     null,
      unit: 'ratio',
    },
  ];

  const ersPattern  = analysisResults.clinical_interpretation?.ers2022?.primary_pattern as string | undefined;
  const ersSeverity = analysisResults.clinical_interpretation?.ers2022?.severity as string | undefined;
  const tradPattern  = analysisResults.clinical_interpretation?.traditional?.primary_pattern as string | undefined;
  const tradSeverity = analysisResults.clinical_interpretation?.traditional?.severity as string | undefined;

  const hasERS  = !!ersPattern;
  const hasTrad = !!tradPattern;
  const methodsDisagree = hasERS && hasTrad && ersPattern !== tradPattern;

  const bd = analysisResults.clinical_interpretation?.bd_response;
  const ageBiasWarning = analysisResults.clinical_interpretation?.age_bias_warning as string | undefined;

  const bdRowClass = (significant: boolean) =>
    significant ? 'text-emerald-700 font-bold' : 'text-slate-600';

  return (
    <div className="space-y-5">

      {/* ── Bronchodilator Response ── */}
      {bd?.has_post_bd && (
        <div className={`border-2 rounded-xl p-5 ${bd.overall_significant ? 'bg-emerald-50 border-emerald-300' : 'bg-slate-50 border-slate-200'}`}>
          <h3 className="text-base font-bold mb-4 flex items-center gap-2 text-slate-800">
            <Activity className="w-5 h-5" />
            {t.methodBdTitle}
            {bd.overall_significant ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 text-sm font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                <CheckCircle className="w-4 h-4" /> {t.methodSignificantLabel}
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                {t.methodNotSignificantLabel}
              </span>
            )}
          </h3>

          <table className="w-full text-sm mb-3">
            <thead>
              <tr className="text-slate-500 border-b-2 border-slate-200">
                <th className="text-start pb-2.5 font-semibold">{t.colParam}</th>
                <th className="text-end pb-2.5 font-semibold">{t.colPreBd}</th>
                <th className="text-end pb-2.5 font-semibold">{t.colPostBd}</th>
                <th className="text-end pb-2.5 font-semibold">{t.colDeltaMl}</th>
                <th className="text-end pb-2.5 font-semibold">{t.colDeltaPctPred}</th>
                <th className="text-end pb-2.5 font-semibold">{t.colCriterion}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {bd.fev1?.pre != null && (
                <tr>
                  <td className="py-2.5 font-bold text-slate-800">FEV1</td>
                  <td className="py-2.5 text-end font-mono text-slate-700">{bd.fev1.pre} L</td>
                  <td className="py-2.5 text-end font-mono text-slate-700">{bd.fev1.post} L</td>
                  <td className={`py-2.5 text-end font-mono ${bdRowClass(bd.fev1.significant)}`}>
                    {bd.fev1.delta_l != null ? `${(bd.fev1.delta_l * 1000).toFixed(0)} mL` : '—'}
                  </td>
                  <td className={`py-2.5 text-end font-mono ${bdRowClass(bd.fev1.significant)}`}>
                    {bd.fev1.delta_pct_pred != null ? `${bd.fev1.delta_pct_pred.toFixed(1)}%` : '—'}
                  </td>
                  <td className="py-2.5 text-end">
                    {bd.fev1.significant
                      ? <span className="text-emerald-700 font-semibold">{t.bdThreshold}</span>
                      : <span className="text-slate-400">{t.bdBelowThreshold}</span>}
                  </td>
                </tr>
              )}
              {bd.fvc?.pre != null && (
                <tr>
                  <td className="py-2.5 font-bold text-slate-800">FVC</td>
                  <td className="py-2.5 text-end font-mono text-slate-700">{bd.fvc.pre} L</td>
                  <td className="py-2.5 text-end font-mono text-slate-700">{bd.fvc.post} L</td>
                  <td className={`py-2.5 text-end font-mono ${bdRowClass(bd.fvc.significant)}`}>
                    {bd.fvc.delta_l != null ? `${(bd.fvc.delta_l * 1000).toFixed(0)} mL` : '—'}
                  </td>
                  <td className={`py-2.5 text-end font-mono ${bdRowClass(bd.fvc.significant)}`}>
                    {bd.fvc.delta_pct_pred != null ? `${bd.fvc.delta_pct_pred.toFixed(1)}%` : '—'}
                  </td>
                  <td className="py-2.5 text-end">
                    {bd.fvc.significant
                      ? <span className="text-emerald-700 font-semibold">{t.bdThreshold}</span>
                      : <span className="text-slate-400">{t.bdBelowThreshold}</span>}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          <p className="text-sm text-slate-600 italic border-t border-slate-200 pt-3">{bd.interpretation}</p>
        </div>
      )}

      {/* ── Primary Pattern Assessment ── */}
      {(hasERS || hasTrad) && (
        <div className="border border-slate-200 rounded-xl overflow-hidden shadow-sm">
          <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center gap-3">
            <h3 className="text-base font-bold text-slate-800">{t.methodPrimaryPattern}</h3>
            {methodsDisagree ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 text-sm font-semibold rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                <AlertTriangle className="w-4 h-4" /> {t.methodsDisagreeLabel}
              </span>
            ) : hasERS && hasTrad ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 text-sm font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                <CheckCircle className="w-4 h-4" /> {t.methodsAgreeLabel}
              </span>
            ) : null}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2">
            {hasERS ? (
              <div className="border-r border-slate-200">
                <div className="bg-blue-600 px-5 py-3">
                  <span className="text-sm font-bold text-white uppercase tracking-wider">ERS 2022 (GLI)</span>
                </div>
                <div className="px-5 py-5">
                  <p className="text-lg font-black text-slate-900">{ersPattern}</p>
                  {ersSeverity && <p className="text-sm text-slate-500 mt-1 font-medium">{t.methodSeverityLabel} {ersSeverity}</p>}
                </div>
              </div>
            ) : (
              <div className="border-r border-slate-200 flex items-center justify-center p-8">
                <span className="text-sm text-slate-400 italic">{t.methodErsNotAvailable}</span>
              </div>
            )}

            {hasTrad ? (
              <div>
                <div className="bg-orange-500 px-5 py-3">
                  <span className="text-sm font-bold text-white uppercase tracking-wider">Traditional GOLD (Murray)</span>
                </div>
                <div className="px-5 py-5">
                  <p className="text-lg font-black text-slate-900">{tradPattern}</p>
                  {tradSeverity && <p className="text-sm text-slate-500 mt-1 font-medium">{t.methodSeverityLabel} {tradSeverity}</p>}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center p-8">
                <span className="text-sm text-slate-400 italic">{t.methodTradNotAvailable}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Age-bias warning ── */}
      {ageBiasWarning && (
        <div className="flex items-start gap-3 bg-amber-50 border-l-4 border-amber-400 rounded-lg px-5 py-4">
          <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
          <p className="text-sm text-amber-800">{ageBiasWarning}</p>
        </div>
      )}

      {/* ── Prediction Method Comparison Table ── */}
      <div className="border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <div className="bg-slate-50 px-6 py-4 border-b border-slate-200">
          <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-slate-500" />
            {t.methodCompTable}
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr>
                <th rowSpan={2} className="px-4 py-3 text-start text-xs font-bold text-slate-500 uppercase tracking-wider align-middle bg-slate-50 border-b border-slate-200">
                  {t.methodParamCol}
                </th>
                <th rowSpan={2} className="px-4 py-3 text-start text-xs font-bold text-blue-600 uppercase tracking-wider align-middle bg-blue-50 border-b border-slate-200">
                  {t.methodMeasuredCol}
                </th>
                <th colSpan={3} className="px-4 py-2.5 text-center text-xs font-bold text-orange-700 uppercase tracking-wider bg-orange-50 border-b border-slate-200">
                  Murray
                </th>
                <th colSpan={3} className="px-4 py-2.5 text-center text-xs font-bold text-emerald-700 uppercase tracking-wider bg-emerald-50 border-b border-slate-200">
                  GLI 2012
                </th>
                <th rowSpan={2} className="px-4 py-3 text-start text-xs font-bold text-slate-500 uppercase tracking-wider align-middle bg-slate-50 border-b border-slate-200">
                  {t.methodAgreementCol}
                </th>
              </tr>
              <tr>
                <th className="px-4 py-2 text-start text-xs font-semibold text-orange-500 uppercase bg-orange-50">{t.colGliPred}</th>
                <th className="px-4 py-2 text-start text-xs font-semibold text-orange-500 uppercase bg-orange-50">{t.colGliLln}</th>
                <th className="px-4 py-2 text-start text-xs font-semibold text-orange-500 uppercase bg-orange-50">{t.colPctPred}</th>
                <th className="px-4 py-2 text-start text-xs font-semibold text-emerald-600 uppercase bg-emerald-50">{t.colGliPred}</th>
                <th className="px-4 py-2 text-start text-xs font-semibold text-emerald-600 uppercase bg-emerald-50">{t.colGliLln}</th>
                <th className="px-4 py-2 text-start text-xs font-semibold text-emerald-600 uppercase bg-emerald-50">{t.colPctPred}</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-100">
              {keyParams.map((param, i) => {
                const murrayNormal = param.measured != null && param.murrayLLN != null
                  ? param.measured >= param.murrayLLN : null;
                const gliNormal = param.measured != null && param.gliLLN != null
                  ? param.measured >= param.gliLLN : null;
                const agreement = murrayNormal !== null && gliNormal !== null
                  ? murrayNormal === gliNormal : null;

                return (
                  <tr key={param.name} className={i % 2 === 0 ? 'bg-white hover:bg-slate-50' : 'bg-slate-50/40 hover:bg-slate-100/60'}>
                    <td className="px-4 py-4 font-bold text-slate-900 text-base">{param.name}</td>
                    <td className="px-4 py-4 font-extrabold text-blue-600 text-base">
                      {fmt(param.measured)}{param.unit !== 'ratio' && <span className="text-xs text-blue-400 font-normal ms-1">{param.unit}</span>}
                    </td>
                    <td className="px-4 py-4 text-orange-600 font-mono">{fmt(param.murrayPred)}</td>
                    <td className="px-4 py-4 text-orange-600 font-mono">{fmt(param.murrayLLN)}</td>
                    <td className={`px-4 py-4 font-mono ${pctColor(param.murrayPct)}`}>
                      {param.murrayPct != null ? `${param.murrayPct}%` : '—'}
                    </td>
                    <td className="px-4 py-4 text-emerald-700 font-mono">{fmt(param.gliPred)}</td>
                    <td className="px-4 py-4 text-emerald-700 font-mono">{fmt(param.gliLLN)}</td>
                    <td className={`px-4 py-4 font-mono ${pctColor(param.gliPct)}`}>
                      {param.gliPct != null ? `${param.gliPct}%` : '—'}
                    </td>
                    <td className="px-4 py-4">
                      {agreement === null ? (
                        <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-100 text-slate-500">N/A</span>
                      ) : (
                        <span className={`px-2.5 py-1 text-xs font-bold rounded-full ${
                          agreement ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {agreement ? t.methodAgree : t.methodDisagree}
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <ExtendedPFTDisplay clinicalInterpretation={analysisResults.clinical_interpretation} />
      </div>
    </div>
  );
};

export default MethodComparisonTab;
