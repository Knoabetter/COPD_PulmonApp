import React, { useState } from 'react';
import {
  User, AlertTriangle, CheckCircle2, AlertCircle, ChevronDown, ChevronUp,
  FileText, Copy, Check, Download, Eye, Shield, FlaskConical, Activity,
  BookOpen, Stethoscope, ArrowRight, Info,
} from 'lucide-react';
import DiagnosticCriteriaButtons from './DiagnosticCriteriaButtons';
import type { AnalysisResults } from './types';

type Props = {
  analysisResults: AnalysisResults;
  onCriteriaSelect?: (criteria: unknown) => void;
};

// ── Visual range bar (% predicted) ───────────────────────────────
const MetricRangeBar = ({ percent, llnPct = 80 }: { percent?: number; llnPct?: number }) => {
  if (percent == null) return null;
  const MAX = 150;
  const fillW = Math.min(Math.max(percent, 0), MAX) / MAX * 100;
  const llnX  = Math.min(llnPct, MAX) / MAX * 100;
  const ok = percent >= llnPct;
  return (
    <div
      className="relative h-2 bg-slate-200 rounded-full w-28 shrink-0"
      title={`${percent.toFixed(0)}% pred | LLN ≈ ${llnPct.toFixed(0)}%`}
    >
      <div
        className={`absolute left-0 top-0 h-full rounded-full ${ok ? 'bg-emerald-400' : 'bg-red-400'}`}
        style={{ width: `${fillW}%` }}
      />
      <div
        className="absolute top-[-3px] bottom-[-3px] w-px bg-slate-500 z-10"
        style={{ left: `${llnX}%` }}
      />
    </div>
  );
};

// ── Helpers ───────────────────────────────────────────────────────
const fmt = (v: number | undefined | null, d = 2): string =>
  v != null && !isNaN(Number(v)) ? Number(v).toFixed(d) : '—';

const sevConfig = (pattern: string, severity: string) => {
  const lc = `${pattern} ${severity}`.toLowerCase();
  if (lc.includes('normal') && !lc.includes('non-s')) return {
    border: 'border-l-emerald-500', bg: 'bg-white',
    badge: 'bg-emerald-100 text-emerald-800 border-emerald-200', dot: 'bg-emerald-500',
  };
  if (lc.includes('very severe') || (lc.includes('severe') && !lc.includes('mild'))) return {
    border: 'border-l-red-500', bg: 'bg-white',
    badge: 'bg-red-100 text-red-800 border-red-200', dot: 'bg-red-500',
  };
  if (lc.includes('moderate')) return {
    border: 'border-l-orange-500', bg: 'bg-white',
    badge: 'bg-orange-100 text-orange-800 border-orange-200', dot: 'bg-orange-500',
  };
  if (lc.includes('mild')) return {
    border: 'border-l-amber-400', bg: 'bg-white',
    badge: 'bg-amber-100 text-amber-800 border-amber-200', dot: 'bg-amber-400',
  };
  if (lc.includes('restrict') || lc.includes('non-s')) return {
    border: 'border-l-blue-500', bg: 'bg-white',
    badge: 'bg-blue-100 text-blue-800 border-blue-200', dot: 'bg-blue-500',
  };
  if (lc.includes('mixed')) return {
    border: 'border-l-purple-500', bg: 'bg-white',
    badge: 'bg-purple-100 text-purple-800 border-purple-200', dot: 'bg-purple-500',
  };
  if (lc.includes('obstruct') || lc.includes('copd')) return {
    border: 'border-l-orange-500', bg: 'bg-white',
    badge: 'bg-orange-100 text-orange-800 border-orange-200', dot: 'bg-orange-500',
  };
  return {
    border: 'border-l-slate-400', bg: 'bg-white',
    badge: 'bg-slate-100 text-slate-700 border-slate-200', dot: 'bg-slate-400',
  };
};

const summaryLine = (pattern: string): string => {
  const lc = pattern.toLowerCase();
  if (lc.includes('normal') && !lc.includes('non'))
    return 'Spirometry is within normal limits for age, sex, and height.';
  if (lc.includes('non-specific'))
    return 'FVC is reduced with a normal FEV1/FVC ratio. TLC measurement is required to distinguish restrictive from non-specific pattern.';
  if (lc.includes('mixed'))
    return 'Combined obstructive and restrictive pattern detected. Full PFT panel recommended.';
  if (lc.includes('restrict'))
    return 'Possible restrictive ventilatory defect. TLC measurement is required to confirm.';
  if (lc.includes('obstruct') || lc.includes('copd'))
    return 'FEV1/FVC ratio is below the lower limit of normal, indicating an obstructive ventilatory defect.';
  return 'Clinical correlation recommended.';
};

const nextAction = (pattern: string, hasBD: boolean): { text: string; urgent: boolean } => {
  const lc = pattern.toLowerCase();
  if (lc.includes('normal') && !lc.includes('non'))
    return { text: 'No additional spirometry testing required. Correlate with clinical symptoms.', urgent: false };
  if (lc.includes('non-specific') || (lc.includes('restrict') && !lc.includes('obstruct')))
    return { text: 'Measure total lung capacity (TLC) by body plethysmography or helium dilution to confirm or exclude a restrictive pattern.', urgent: true };
  if (lc.includes('obstruct') || lc.includes('copd')) {
    if (!hasBD)
      return { text: 'Bronchodilator test recommended if not already performed to assess reversibility.', urgent: false };
    return { text: 'Obstructive pattern confirmed. Clinical correlation and follow-up per GOLD/COPD guidelines.', urgent: false };
  }
  if (lc.includes('mixed'))
    return { text: 'Full pulmonary function testing including lung volumes (TLC) and diffusion capacity (DLCO) recommended.', urgent: true };
  return { text: 'Clinical correlation recommended. Consider repeat spirometry if findings are inconsistent.', urgent: false };
};

const deriveSteps = (analysisResults: AnalysisResults): string[] => {
  const steps: string[] = [];
  const m  = analysisResults.measured;
  const gl = analysisResults.gli;
  const mu = analysisResults.murray;
  const ratioLLN = gl?.ratio?.lln ?? mu?.ratio?.lln;
  const fvcLLN   = gl?.FVC?.lln   ?? mu?.FVC?.lln;
  const fev1LLN  = gl?.FEV1?.lln  ?? mu?.FEV1?.lln;
  const fev1Pct  = gl?.FEV1?.percent ?? mu?.FEV1?.percent;

  if (m?.ratio != null && ratioLLN != null) {
    if (m.ratio < ratioLLN) {
      steps.push(`FEV1/FVC ratio (${fmt(m.ratio, 3)}) is below LLN (${fmt(ratioLLN, 3)}) → obstruction present`);
      if (fev1Pct != null) {
        const sev =
          fev1Pct >= 80 ? 'Mild (FEV1 ≥ 80% pred)' :
          fev1Pct >= 50 ? 'Moderate (FEV1 50–79% pred)' :
          fev1Pct >= 30 ? 'Severe (FEV1 30–49% pred)' : 'Very Severe (FEV1 < 30% pred)';
        steps.push(`FEV1 is ${Math.round(fev1Pct)}% predicted → ${sev}`);
      }
    } else {
      steps.push(`FEV1/FVC ratio (${fmt(m.ratio, 3)}) ≥ LLN (${fmt(ratioLLN, 3)}) → no obstruction`);
      if (m.FVC != null && fvcLLN != null) {
        if (m.FVC < fvcLLN) {
          steps.push(`FVC (${fmt(m.FVC)} L) is below LLN (${fmt(fvcLLN)} L) → reduced FVC with normal ratio`);
          steps.push(`TLC required to distinguish restrictive from non-specific pattern`);
        } else if (m.FEV1 != null && fev1LLN != null && m.FEV1 < fev1LLN) {
          steps.push(`FVC (${fmt(m.FVC)} L) ≥ LLN, but FEV1 (${fmt(m.FEV1)} L) < LLN (${fmt(fev1LLN)} L) → non-specific pattern`);
        } else {
          steps.push(`FVC (${fmt(m.FVC)} L) ≥ LLN (${fmt(fvcLLN)} L) → FVC normal`);
          if (m.FEV1 != null && fev1LLN != null && m.FEV1 >= fev1LLN) {
            steps.push(`FEV1 (${fmt(m.FEV1)} L) ≥ LLN (${fmt(fev1LLN)} L) → normal spirometry confirmed`);
          }
        }
      }
    }
  }

  const bd = (analysisResults.clinical_interpretation as any)?.bd_response;
  if (bd?.has_post_bd) {
    if (bd.overall_significant) {
      const d = bd.fev1?.delta_l != null ? ` (Δ${(bd.fev1.delta_l * 1000).toFixed(0)} mL, ${bd.fev1.delta_pct_pred?.toFixed(1)}% pred)` : '';
      steps.push(`Bronchodilator response: significant${d} → reversible component present`);
    } else {
      steps.push('Bronchodilator response: not significant → fixed airflow limitation');
    }
  }
  return steps;
};

const QUICK_PHRASES = [
  'Spirometry within normal limits',
  'Suspected restrictive pattern — TLC recommended',
  'Obstructive ventilatory defect confirmed',
  'Significant bronchodilator response',
  'No significant bronchodilator response',
  'Correlate clinically',
  'Repeat spirometry recommended',
];

const criteriaLabels: Record<string, string> = {
  restrictive: 'Restrictive pattern',
  obstructive: 'Obstructive pattern',
  bronchodilator: 'Bronchodilator response',
  lungVolumes: 'Lung volumes',
  airTrapping: 'Air trapping',
  diffusion: 'Diffusion capacity (DLCO/KCO)',
  dlcoCorrection: 'DLCO correction for alveolar volume',
};

// ── Main component ────────────────────────────────────────────────
const EnhancedAnalysisResults: React.FC<Props> = ({ analysisResults, onCriteriaSelect }) => {
  const [logicOpen, setLogicOpen]   = useState(false);
  const [guideOpen, setGuideOpen]   = useState(false);
  const [physicianNotes, setPhysicianNotes] = useState('');
  const [copied, setCopied] = useState(false);

  if (!analysisResults) return null;

  const p  = analysisResults.patient;
  const m  = analysisResults.measured;
  const gl = analysisResults.gli;
  const mu = analysisResults.murray;
  const ei = (analysisResults as any).extraction_info;
  const ci = analysisResults.clinical_interpretation as any;
  const validationWarnings: string[] = (analysisResults as any).validation?.warnings ?? [];

  const ers2022      = ci?.ers2022;
  const traditional  = ci?.traditional;
  const bd           = ci?.bd_response;
  const ersPattern   = ers2022?.primary_pattern ?? '';
  const ersSeverity  = ers2022?.severity ?? '';
  const tradPattern  = traditional?.primary_pattern ?? '';
  const hasClinical  = !!ersPattern;
  const hasBD        = !!bd?.has_post_bd;

  const cfg          = sevConfig(ersPattern, ersSeverity);
  const steps        = deriveSteps(analysisResults);
  const action       = ersPattern ? nextAction(ersPattern, hasBD) : null;

  const tradIsNormal      = tradPattern.toLowerCase().includes('normal');
  const ersIsNormal       = ersPattern.toLowerCase().includes('normal') && !ersPattern.toLowerCase().includes('non');
  const ersIsObstruction  = ersPattern.toLowerCase().includes('obstruct') || ersPattern.toLowerCase().includes('copd');
  const tradIsObstruction = tradPattern.toLowerCase().includes('obstruct') || tradPattern.toLowerCase().includes('copd');
  const methodsAgree = hasClinical && (
    (ersIsNormal && tradIsNormal) ||
    (ersIsObstruction && tradIsObstruction) ||
    (!ersIsNormal && !tradIsNormal && !ersIsObstruction && !tradIsObstruction)
  );

  // ── Evidence table rows ──────────────────────────────────────
  const evidenceRows = [
    {
      name: 'FEV1', unit: 'L',
      measured: m?.FEV1,
      gliPred: gl?.FEV1?.pred, gliLLN: gl?.FEV1?.lln, gliPct: gl?.FEV1?.percent,
      murPred: mu?.FEV1?.pred, murLLN: mu?.FEV1?.lln, murPct: mu?.FEV1?.percent,
      zScore: ers2022?.fev1_z_score,
    },
    {
      name: 'FVC', unit: 'L',
      measured: m?.FVC,
      gliPred: gl?.FVC?.pred, gliLLN: gl?.FVC?.lln, gliPct: gl?.FVC?.percent,
      murPred: mu?.FVC?.pred, murLLN: mu?.FVC?.lln, murPct: mu?.FVC?.percent,
      zScore: ers2022?.fvc_z_score,
    },
    {
      name: 'FEV1/FVC', unit: '',
      measured: m?.ratio,
      gliPred: null, gliLLN: gl?.ratio?.lln, gliPct: null,
      murPred: null, murLLN: mu?.ratio?.lln, murPct: null,
      zScore: null,
    },
  ];

  // ── Note generation ───────────────────────────────────────────
  const generateNote = (criteria: Record<string, string>): string => {
    const today = new Date().toLocaleDateString('en-GB');
    const lines = [`Spirometry Report — ${today}`];
    const parts: string[] = [];
    if (p?.age)    parts.push(`Age: ${p.age} yr`);
    if (p?.sex)    parts.push(`Sex: ${p.sex}`);
    if (p?.height) parts.push(`Height: ${p.height} cm`);
    if (parts.length) lines.push(parts.join(' | '));
    lines.push('', 'Measured Values:');
    if (m?.FEV1 != null) {
      const pct = gl?.FEV1?.percent ?? mu?.FEV1?.percent;
      lines.push(`  FEV1:     ${fmt(m.FEV1)} L${pct != null ? ` (${pct}% pred)` : ''}`);
    }
    if (m?.FVC != null) {
      const pct = gl?.FVC?.percent ?? mu?.FVC?.percent;
      lines.push(`  FVC:      ${fmt(m.FVC)} L${pct != null ? ` (${pct}% pred)` : ''}`);
    }
    if (m?.ratio != null) lines.push(`  FEV1/FVC: ${fmt(m.ratio, 3)}`);
    if (ersPattern) {
      lines.push('', `Interpretation (ERS/ATS 2022): ${ersPattern}`);
      if (ersSeverity) lines.push(`Severity: ${ersSeverity}`);
    }
    if (tradPattern) lines.push(`Traditional (GOLD): ${tradPattern}`);
    if (action) lines.push('', `Recommendation: ${action.text}`);
    const sel = Object.entries(criteria).filter(([, v]) => v);
    if (sel.length) {
      lines.push('', 'Clinical Findings:');
      sel.forEach(([k, v]) => lines.push(`  ${criteriaLabels[k] ?? k}: ${v}`));
    }
    if (physicianNotes.trim()) lines.push('', 'Notes:', physicianNotes.trim());
    lines.push('', 'Based on: ERS/ATS 2022 | GLI 2012 Reference Equations');
    return lines.join('\n');
  };

  const handleCriteriaSelect = (criteria: Record<string, string>) => {
    setPhysicianNotes(generateNote(criteria));
    if (onCriteriaSelect) onCriteriaSelect(criteria);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(physicianNotes);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const insertPhrase = (phrase: string) => {
    setPhysicianNotes(prev => prev ? `${prev}\n${phrase}` : phrase);
  };

  const handleDownload = () => {
    const text = physicianNotes || generateNote({});
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `spirometry_report_${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // ── Render ────────────────────────────────────────────────────
  return (
    <div className="space-y-4">

      {/* ── 1. Validation Warnings ── */}
      {validationWarnings.length > 0 && (
        <div className="border-l-4 border-amber-400 bg-amber-50 rounded-xl px-5 py-4 space-y-2">
          <div className="flex items-center gap-2 text-base font-bold text-amber-800">
            <AlertTriangle className="w-5 h-5" /> Extraction Warnings — verify values before proceeding
          </div>
          {validationWarnings.map((w, i) => (
            <p key={i} className="text-sm text-amber-700 flex items-start gap-2 pl-1">
              <span className="shrink-0 mt-0.5">•</span><span>{w}</span>
            </p>
          ))}
        </div>
      )}

      {/* ── 2. Patient Context ── */}
      {(p?.age || p?.sex || p?.height) && (
        <div className="bg-slate-900 rounded-xl px-5 py-3 flex flex-wrap items-center gap-x-7 gap-y-1.5 shadow-md">
          <span className="flex items-center gap-1.5 text-xs font-bold text-slate-400 uppercase tracking-widest">
            <User className="w-3.5 h-3.5" /> Patient
          </span>
          {p?.age    && <span className="text-slate-400 text-xs">Age <span className="font-bold text-cyan-400 text-sm ml-1">{p.age}</span><span className="text-slate-600 text-xs ml-0.5">yr</span></span>}
          {p?.sex    && <span className="text-slate-400 text-xs">Sex <span className="font-bold text-cyan-400 text-sm ml-1">{p.sex}</span></span>}
          {p?.height && <span className="text-slate-400 text-xs">Ht <span className="font-bold text-cyan-400 text-sm ml-1">{p.height}</span><span className="text-slate-600 text-xs ml-0.5">cm</span></span>}
          <span className="w-px h-4 bg-slate-700 hidden sm:block" />
          {ei?.fev1_pre && <span className="text-slate-400 text-xs">FEV1 <span className="font-bold text-sky-400 text-sm ml-1">{ei.fev1_pre}</span><span className="text-slate-600 text-xs ml-0.5">L</span></span>}
          {ei?.fvc_pre  && <span className="text-slate-400 text-xs">FVC  <span className="font-bold text-sky-400 text-sm ml-1">{ei.fvc_pre}</span><span className="text-slate-600 text-xs ml-0.5">L</span></span>}
          {ei?.ratio_pre && (
            <span className="text-slate-400 text-xs">
              FEV1/FVC <span className="font-bold text-sky-400 text-sm ml-1">
                {Number(ei.ratio_pre) > 1 ? (ei.ratio_pre / 100).toFixed(2) : Number(ei.ratio_pre).toFixed(2)}
              </span>
            </span>
          )}
          <span className="ml-auto text-xs text-slate-600 italic">Verify before accepting results</span>
        </div>
      )}

      {/* ── 3. Clinical Interpretation Summary ── */}
      {hasClinical && (
        <div className={`border-l-4 ${cfg.border} bg-white rounded-r-xl border border-l-4 shadow-sm overflow-hidden`}>
          <div className="px-6 py-5">
            {/* Header label */}
            <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">
              Clinical Interpretation — ERS/ATS 2022
            </p>

            {/* Pattern + agreement badge */}
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-black text-slate-900 leading-tight">{ersPattern}</h2>
                {ersSeverity && ersSeverity !== 'Normal' && ersSeverity !== 'Unknown' && (
                  <span className={`inline-block mt-2 px-3 py-1 text-sm font-bold rounded-full border ${cfg.badge}`}>
                    {ersSeverity}
                  </span>
                )}
              </div>
              <div className="flex flex-col items-end gap-2 shrink-0">
                {methodsAgree ? (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-semibold rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <CheckCircle2 className="w-4 h-4" /> Methods agree
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-semibold rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                    <AlertCircle className="w-4 h-4" /> Methods disagree
                  </span>
                )}
                {tradPattern && (
                  <span className="text-xs text-slate-500">Traditional GOLD: <span className="font-semibold">{tradPattern}</span></span>
                )}
              </div>
            </div>

            {/* Summary sentence */}
            <p className="mt-3 text-sm text-slate-600 leading-relaxed">{summaryLine(ersPattern)}</p>

            {/* Z-scores */}
            {(ers2022?.fev1_z_score != null || ers2022?.fvc_z_score != null) && (
              <div className="flex flex-wrap gap-4 mt-3 pt-3 border-t border-slate-100">
                {ers2022?.fev1_z_score != null && (
                  <span className="text-sm text-slate-500">
                    FEV1 Z-score: <span className="font-bold text-slate-800">{Number(ers2022.fev1_z_score).toFixed(2)}</span>
                  </span>
                )}
                {ers2022?.fvc_z_score != null && (
                  <span className="text-sm text-slate-500">
                    FVC Z-score: <span className="font-bold text-slate-800">{Number(ers2022.fvc_z_score).toFixed(2)}</span>
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Restriction notice */}
          {(ersPattern.toLowerCase().includes('restrict') || ersPattern.toLowerCase().includes('non-specific')) && (
            <div className="border-t border-blue-100 bg-blue-50 px-6 py-3 flex items-center gap-2.5">
              <FlaskConical className="w-4 h-4 text-blue-600 shrink-0" />
              <p className="text-sm text-blue-800 font-medium">
                TLC measurement required — spirometry alone cannot confirm restriction.
              </p>
            </div>
          )}
        </div>
      )}

      {/* ── 4. Evidence Panel ── */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="px-5 py-3.5 border-b border-slate-100 flex items-center gap-2.5 bg-slate-50">
          <Activity className="w-4 h-4 text-slate-500" />
          <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">Evidence — Measured Values</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-100">
                <th className="px-5 py-3 text-left">Param</th>
                <th className="px-4 py-3 text-right">Measured</th>
                <th className="px-4 py-3 text-right">GLI Pred</th>
                <th className="px-4 py-3 text-right">GLI LLN</th>
                <th className="px-4 py-3 text-right">% Pred</th>
                <th className="px-4 py-3 text-right">Z-score</th>
                <th className="px-5 py-3 text-left">Range</th>
                <th className="px-4 py-3 text-left">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {evidenceRows.map(row => {
                const lln   = row.gliLLN ?? row.murLLN;
                const pct   = row.gliPct ?? row.murPct;
                const pred  = row.gliPred ?? row.murPred;
                const llnPct = pred && lln ? (lln / pred) * 100 : 80;
                const isAboveLLN = row.measured != null && lln != null ? row.measured >= lln : null;

                return (
                  <tr key={row.name} className="hover:bg-slate-50/60">
                    <td className="px-5 py-3.5 font-bold text-slate-900">{row.name}</td>
                    <td className="px-4 py-3.5 text-right font-bold text-blue-700 font-mono">
                      {fmt(row.measured)}{row.unit && <span className="text-blue-400 font-normal text-xs ml-0.5">{row.unit}</span>}
                    </td>
                    <td className="px-4 py-3.5 text-right text-slate-500 font-mono">{fmt(row.gliPred)}</td>
                    <td className="px-4 py-3.5 text-right text-slate-500 font-mono">{fmt(lln)}</td>
                    <td className={`px-4 py-3.5 text-right font-mono font-bold ${
                      pct == null ? 'text-slate-400' :
                      pct >= 100  ? 'text-emerald-700' :
                      pct >= (llnPct || 80) ? 'text-amber-700' : 'text-red-700'
                    }`}>
                      {pct != null ? `${pct}%` : '—'}
                    </td>
                    <td className="px-4 py-3.5 text-right font-mono text-slate-600">
                      {row.zScore != null ? Number(row.zScore).toFixed(2) : '—'}
                    </td>
                    <td className="px-5 py-3.5">
                      <MetricRangeBar percent={pct ?? undefined} llnPct={llnPct} />
                    </td>
                    <td className="px-4 py-3.5">
                      {isAboveLLN === null ? (
                        <span className="text-xs text-slate-400">—</span>
                      ) : isAboveLLN ? (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />Normal
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-red-700">
                          <span className="w-1.5 h-1.5 rounded-full bg-red-500" />Below LLN
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── 5. Bronchodilator Response ── */}
      {hasBD && (
        <div className={`border rounded-xl overflow-hidden shadow-sm ${bd.overall_significant ? 'border-emerald-200' : 'border-slate-200'}`}>
          <div className={`px-5 py-3 flex items-center gap-2.5 border-b ${bd.overall_significant ? 'bg-emerald-50 border-emerald-100' : 'bg-slate-50 border-slate-100'}`}>
            <Activity className={`w-4 h-4 ${bd.overall_significant ? 'text-emerald-600' : 'text-slate-400'}`} />
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">Bronchodilator Response</h3>
            {bd.overall_significant ? (
              <span className="ml-auto inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                <CheckCircle2 className="w-3.5 h-3.5" />Significant
              </span>
            ) : (
              <span className="ml-auto text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                Not significant
              </span>
            )}
          </div>
          <div className="bg-white px-5 py-4">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-slate-500 font-semibold border-b border-slate-100">
                  <th className="text-left pb-2">Param</th>
                  <th className="text-right pb-2">Pre-BD</th>
                  <th className="text-right pb-2">Post-BD</th>
                  <th className="text-right pb-2">Δ mL</th>
                  <th className="text-right pb-2">Δ % pred</th>
                  <th className="text-right pb-2">Criterion</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {bd.fev1?.pre != null && (
                  <tr>
                    <td className="py-2.5 font-bold text-slate-800">FEV1</td>
                    <td className="py-2.5 text-right font-mono text-slate-700">{bd.fev1.pre} L</td>
                    <td className="py-2.5 text-right font-mono text-slate-700">{bd.fev1.post} L</td>
                    <td className={`py-2.5 text-right font-mono ${bd.fev1.significant ? 'text-emerald-700 font-bold' : 'text-slate-600'}`}>
                      {bd.fev1.delta_l != null ? `${(bd.fev1.delta_l * 1000).toFixed(0)} mL` : '—'}
                    </td>
                    <td className={`py-2.5 text-right font-mono ${bd.fev1.significant ? 'text-emerald-700 font-bold' : 'text-slate-600'}`}>
                      {bd.fev1.delta_pct_pred != null ? `${bd.fev1.delta_pct_pred.toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-2.5 text-right">
                      {bd.fev1.significant
                        ? <span className="text-xs text-emerald-700 font-semibold">✓ ≥150 mL + ≥10%</span>
                        : <span className="text-xs text-slate-400">below threshold</span>}
                    </td>
                  </tr>
                )}
                {bd.fvc?.pre != null && (
                  <tr>
                    <td className="py-2.5 font-bold text-slate-800">FVC</td>
                    <td className="py-2.5 text-right font-mono text-slate-700">{bd.fvc.pre} L</td>
                    <td className="py-2.5 text-right font-mono text-slate-700">{bd.fvc.post} L</td>
                    <td className={`py-2.5 text-right font-mono ${bd.fvc.significant ? 'text-emerald-700 font-bold' : 'text-slate-600'}`}>
                      {bd.fvc.delta_l != null ? `${(bd.fvc.delta_l * 1000).toFixed(0)} mL` : '—'}
                    </td>
                    <td className={`py-2.5 text-right font-mono ${bd.fvc.significant ? 'text-emerald-700 font-bold' : 'text-slate-600'}`}>
                      {bd.fvc.delta_pct_pred != null ? `${bd.fvc.delta_pct_pred.toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-2.5 text-right">
                      {bd.fvc.significant
                        ? <span className="text-xs text-emerald-700 font-semibold">✓ ≥150 mL + ≥10%</span>
                        : <span className="text-xs text-slate-400">below threshold</span>}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
            {bd.interpretation && (
              <p className="mt-3 pt-3 border-t border-slate-100 text-sm text-slate-500 italic">{bd.interpretation}</p>
            )}
          </div>
        </div>
      )}

      {/* ── 6. Interpretation Logic (collapsible) ── */}
      {steps.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <button
            onClick={() => setLogicOpen(v => !v)}
            className="w-full px-5 py-3.5 flex items-center gap-2.5 text-left hover:bg-slate-50 transition-colors"
          >
            <Info className="w-4 h-4 text-slate-400 shrink-0" />
            <span className="text-sm font-bold text-slate-700 uppercase tracking-wider">How this result was derived</span>
            <span className="ml-auto">
              {logicOpen ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </span>
          </button>
          {logicOpen && (
            <div className="border-t border-slate-100 px-5 py-4 space-y-2.5">
              {steps.map((step, i) => (
                <div key={i} className="flex items-start gap-3">
                  <span className="shrink-0 w-5 h-5 rounded-full bg-slate-100 text-slate-600 text-xs font-bold flex items-center justify-center mt-0.5">
                    {i + 1}
                  </span>
                  <p className="text-sm text-slate-700 leading-snug">{step}</p>
                </div>
              ))}
              {ci?.age_bias_warning && (
                <div className="flex items-start gap-2 mt-3 bg-amber-50 border-l-4 border-amber-400 rounded px-3 py-2.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
                  <p className="text-xs text-amber-800">{ci.age_bias_warning}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── 7. Next Clinical Action ── */}
      {action && (
        <div className={`rounded-xl border shadow-sm overflow-hidden ${action.urgent ? 'border-blue-200' : 'border-slate-200'}`}>
          <div className={`px-5 py-3 flex items-center gap-2.5 border-b ${action.urgent ? 'bg-blue-50 border-blue-100' : 'bg-slate-50 border-slate-100'}`}>
            <ArrowRight className={`w-4 h-4 shrink-0 ${action.urgent ? 'text-blue-600' : 'text-slate-400'}`} />
            <h3 className={`text-sm font-bold uppercase tracking-wider ${action.urgent ? 'text-blue-800' : 'text-slate-700'}`}>
              Recommended Next Step
            </h3>
          </div>
          <div className="bg-white px-5 py-4 flex items-start justify-between gap-4">
            <p className={`text-sm leading-relaxed ${action.urgent ? 'text-blue-900 font-medium' : 'text-slate-700'}`}>{action.text}</p>
            <button
              onClick={() => insertPhrase(action.text)}
              className="shrink-0 text-xs px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 hover:bg-slate-200 font-semibold transition-colors"
              title="Insert into notes"
            >
              + Notes
            </button>
          </div>
        </div>
      )}

      {/* ── 8. Method Comparison ── */}
      {hasClinical && (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="px-5 py-3.5 border-b border-slate-100 bg-slate-50 flex items-center gap-2.5">
            <Shield className="w-4 h-4 text-slate-500" />
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">Method Comparison</h3>
            {!methodsAgree && (
              <span className="ml-auto inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                <AlertTriangle className="w-3.5 h-3.5" />Methods disagree
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-100">
            {/* ERS 2022 */}
            <div className="p-5">
              <div className="flex items-center gap-2 mb-3">
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-blue-600" />
                <span className="text-xs font-bold text-blue-700 uppercase tracking-wider">ERS/ATS 2022 (GLI)</span>
              </div>
              <p className="text-lg font-black text-slate-900">{ers2022?.primary_pattern ?? '—'}</p>
              {ers2022?.severity && <p className="text-sm text-slate-500 mt-0.5">Severity: {ers2022.severity}</p>}
              {ers2022?.clinical_notes?.length > 0 && (
                <ul className="mt-3 space-y-1.5">
                  {ers2022.clinical_notes.slice(0, 3).map((note: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-slate-600">
                      <span className="mt-1 w-1 h-1 rounded-full bg-blue-400 shrink-0" />
                      {note}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Traditional GOLD */}
            <div className="p-5">
              <div className="flex items-center gap-2 mb-3">
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-orange-500" />
                <span className="text-xs font-bold text-orange-700 uppercase tracking-wider">Traditional GOLD (Murray)</span>
              </div>
              <p className="text-lg font-black text-slate-900">{traditional?.primary_pattern ?? '—'}</p>
              {traditional?.severity && <p className="text-sm text-slate-500 mt-0.5">Severity: {traditional.severity}</p>}
              {traditional?.clinical_notes?.length > 0 && (
                <ul className="mt-3 space-y-1.5">
                  {traditional.clinical_notes.slice(0, 3).map((note: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-slate-600">
                      <span className="mt-1 w-1 h-1 rounded-full bg-orange-400 shrink-0" />
                      {note}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Metric comparison table */}
          <div className="border-t border-slate-100 overflow-x-auto">
            <table className="min-w-full text-xs">
              <thead>
                <tr className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider">
                  <th className="px-4 py-2.5 text-left">Param</th>
                  <th className="px-3 py-2.5 text-right">Measured</th>
                  <th className="px-3 py-2.5 text-right text-orange-600">Murray LLN</th>
                  <th className="px-3 py-2.5 text-right text-orange-600">Murray %</th>
                  <th className="px-3 py-2.5 text-right text-emerald-600">GLI LLN</th>
                  <th className="px-3 py-2.5 text-right text-emerald-600">GLI %</th>
                  <th className="px-4 py-2.5 text-left">Agreement</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50 bg-white">
                {evidenceRows.map((row) => {
                  const murrayNormal = row.measured != null && row.murLLN != null ? row.measured >= row.murLLN : null;
                  const gliNormal    = row.measured != null && row.gliLLN != null ? row.measured >= row.gliLLN : null;
                  const agree = murrayNormal !== null && gliNormal !== null ? murrayNormal === gliNormal : null;
                  return (
                    <tr key={row.name}>
                      <td className="px-4 py-2.5 font-bold text-slate-800">{row.name}</td>
                      <td className="px-3 py-2.5 text-right font-bold text-blue-700 font-mono">{fmt(row.measured)}</td>
                      <td className="px-3 py-2.5 text-right font-mono text-slate-600">{fmt(row.murLLN)}</td>
                      <td className={`px-3 py-2.5 text-right font-mono font-bold ${row.murPct == null ? 'text-slate-400' : row.murPct >= 80 ? 'text-emerald-700' : 'text-red-700'}`}>
                        {row.murPct != null ? `${row.murPct}%` : '—'}
                      </td>
                      <td className="px-3 py-2.5 text-right font-mono text-slate-600">{fmt(row.gliLLN)}</td>
                      <td className={`px-3 py-2.5 text-right font-mono font-bold ${row.gliPct == null ? 'text-slate-400' : row.gliPct >= 80 ? 'text-emerald-700' : 'text-red-700'}`}>
                        {row.gliPct != null ? `${row.gliPct}%` : '—'}
                      </td>
                      <td className="px-4 py-2.5">
                        {agree === null ? (
                          <span className="text-slate-400">N/A</span>
                        ) : agree ? (
                          <span className="font-semibold text-emerald-700">✓ Agree</span>
                        ) : (
                          <span className="font-semibold text-red-700">✗ Disagree</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── 9. Physician Notes ── */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="px-5 py-3.5 border-b border-slate-100 bg-slate-50 flex items-center gap-2.5">
          <FileText className="w-4 h-4 text-slate-500" />
          <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">Physician Notes</h3>
          <button
            onClick={handleCopy}
            disabled={!physicianNotes}
            className={`ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              copied ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
              : physicianNotes ? 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              : 'bg-slate-50 text-slate-300 cursor-not-allowed'
            }`}
          >
            {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>

        <div className="px-5 py-4 space-y-4">
          {/* Quick-insert chips */}
          <div>
            <p className="text-xs text-slate-400 font-semibold mb-2 flex items-center gap-1.5">
              <Stethoscope className="w-3.5 h-3.5" /> Quick insert
            </p>
            <div className="flex flex-wrap gap-2">
              {QUICK_PHRASES.map(phrase => (
                <button
                  key={phrase}
                  onClick={() => insertPhrase(phrase)}
                  className="text-xs px-3 py-1.5 rounded-full bg-slate-100 hover:bg-blue-100 hover:text-blue-800 text-slate-600 border border-slate-200 hover:border-blue-200 transition-colors font-medium"
                >
                  {phrase}
                </button>
              ))}
            </div>
          </div>

          {/* Diagnostic criteria dropdowns */}
          <div>
            <p className="text-xs text-slate-400 font-semibold mb-2 flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5" /> Select findings to populate note
            </p>
            <DiagnosticCriteriaButtons onCriteriaSelect={handleCriteriaSelect} inline={true} />
          </div>

          {/* Notes textarea */}
          <textarea
            value={physicianNotes}
            onChange={e => setPhysicianNotes(e.target.value)}
            placeholder="Select criteria above or use quick insert, or type directly..."
            className="w-full h-44 p-4 border border-slate-200 rounded-xl text-sm font-mono resize-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 focus:outline-none text-slate-700 placeholder-slate-400 bg-slate-50/50"
          />

          {/* Actions */}
          <div className="flex flex-wrap gap-2.5 pt-1">
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 text-sm font-semibold shadow-sm transition-colors"
            >
              <Download className="w-4 h-4" /> Download Report
            </button>
            <button className="flex items-center gap-2 px-4 py-2.5 bg-slate-700 text-white rounded-xl hover:bg-slate-800 text-sm font-semibold shadow-sm transition-colors">
              <Eye className="w-4 h-4" /> Add to Research DB
            </button>
          </div>
        </div>
      </div>

      {/* ── 10. Guideline Traceability ── */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <button
          onClick={() => setGuideOpen(v => !v)}
          className="w-full px-5 py-3.5 flex items-center gap-2.5 text-left hover:bg-slate-50 transition-colors"
        >
          <BookOpen className="w-4 h-4 text-slate-400 shrink-0" />
          <span className="text-sm font-bold text-slate-700 uppercase tracking-wider">Guideline Traceability</span>
          <span className="ml-auto">
            {guideOpen ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </span>
        </button>
        {guideOpen && (
          <div className="border-t border-slate-100 px-5 py-4 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-slate-600">
            <div>
              <p className="font-semibold text-slate-800 mb-1 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-blue-500" /> ERS/ATS 2022 Method
              </p>
              <ul className="space-y-0.5 text-xs text-slate-500">
                <li>• Graham BL et al. ERS/ATS Technical Standards 2019</li>
                <li>• Quanjer PH et al. GLI 2012 Reference Equations</li>
                <li>• 5th percentile (z-score −1.645) as LLN</li>
                <li>• Figure 8 algorithm for pattern classification</li>
              </ul>
            </div>
            <div>
              <p className="font-semibold text-slate-800 mb-1 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-orange-500" /> Traditional GOLD Method
              </p>
              <ul className="space-y-0.5 text-xs text-slate-500">
                <li>• Murray CJ et al. Traditional Reference Equations</li>
                <li>• Fixed threshold: FEV1/FVC &lt; 0.70</li>
                <li>• 80% predicted as LLN</li>
                <li>• GOLD severity staging by FEV1 % predicted</li>
              </ul>
            </div>
            <div className="sm:col-span-2 border-t border-slate-100 pt-3 mt-1">
              <p className="text-xs text-slate-400 italic">
                <strong>Ethnic equity note:</strong> GLI 2012 equations were derived primarily from European/Caucasian populations.
                For non-European patients, consider GLI 2021 equations with broader ethnic coverage where available.
              </p>
            </div>
          </div>
        )}
      </div>

    </div>
  );
};

export default EnhancedAnalysisResults;
