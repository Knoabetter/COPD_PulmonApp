import { useState } from 'react';
import { Activity, BarChart3, Home, ChevronRight } from 'lucide-react';
import ClinicalAnalysisModule from './Clinical_Module/ClinicalAnalysisModule';
import ResearchModule from './ResearchModule';
import { t } from '../translations';

interface DashboardProps {
  username: string;
  onLogout: () => void;
}

function Dashboard({ username }: DashboardProps) {
  const [activeModule, setActiveModule] = useState<'home' | 'clinical' | 'research'>('home');

  const renderContent = () => {
    switch (activeModule) {
      case 'clinical':  return <ClinicalAnalysisModule />;
      case 'research':  return <ResearchModule />;
      default: return <HomePage onNavigate={setActiveModule} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* ── Navigation bar ── */}
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-14">
            {/* Logo + breadcrumb */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveModule('home')}
                className="flex items-center gap-2 text-slate-900 hover:text-blue-600 transition-colors"
              >
                <span className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center shrink-0">
                  <Home className="w-3.5 h-3.5 text-white" />
                </span>
                <span className="font-bold text-base tracking-tight">{t.appTitle}</span>
              </button>

              {activeModule !== 'home' && (
                <div className="flex items-center gap-1.5 ms-2 text-sm">
                  <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
                  <span className="text-slate-500 font-medium">
                    {activeModule === 'clinical' ? t.breadcrumbSpirometry : t.breadcrumbResearch}
                  </span>
                </div>
              )}
            </div>

            {/* User */}
            <div className="flex items-center gap-3">
              {activeModule !== 'home' && (
                <button
                  onClick={() => setActiveModule('home')}
                  className="text-xs text-slate-500 hover:text-blue-600 font-medium transition-colors"
                >
                  {t.homeNavButton}
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* ── Main content ── */}
      <main>{renderContent()}</main>
    </div>
  );
}

// ── Home page ─────────────────────────────────────────────────────
function HomePage({ onNavigate }: { onNavigate: (m: 'clinical' | 'research') => void }) {
  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      {/* Institution header */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-50 border border-blue-100 rounded-full text-blue-700 text-xs font-semibold mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
          {t.institutionBadge}
        </div>

        <div className="flex justify-center mb-5">
          <img
            src="/images/tasmd_logo.jpeg"
            alt={t.institutionName}
            className="w-20 h-20 object-contain rounded-xl"
          />
        </div>

        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
          {t.appTitle}
        </h1>
        <p className="mt-2 text-slate-500 text-sm max-w-md mx-auto">
          {t.homePageSubtitle}
        </p>
      </div>

      {/* Module cards */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Clinical Analysis */}
        <ModuleCard
          icon={<Activity className="w-5 h-5 text-blue-600" />}
          iconBg="bg-blue-50 border border-blue-100"
          title={t.clinicalTitle}
          description={t.clinicalDesc}
          capabilities={[t.clinicalCap1, t.clinicalCap2, t.clinicalCap3, t.clinicalCap4]}
          actionLabel={t.clinicalButton}
          actionColor="bg-blue-600 hover:bg-blue-700"
          onClick={() => onNavigate('clinical')}
        />

        {/* Research */}
        <ModuleCard
          icon={<BarChart3 className="w-5 h-5 text-violet-600" />}
          iconBg="bg-violet-50 border border-violet-100"
          title={t.researchTitle}
          description={t.researchDesc}
          capabilities={[t.researchCap1, t.researchCap2, t.researchCap3, t.researchCap4]}
          actionLabel={t.researchButton}
          actionColor="bg-violet-600 hover:bg-violet-700"
          onClick={() => onNavigate('research')}
        />
      </div>

      {/* Footer note */}
      <p className="text-center text-xs text-slate-400 mt-10">
        {t.disclaimerText}
      </p>
    </div>
  );
}

// ── Module card ───────────────────────────────────────────────────
interface ModuleCardProps {
  icon: React.ReactNode;
  iconBg: string;
  title: string;
  description: string;
  capabilities: string[];
  actionLabel: string;
  actionColor: string;
  onClick: () => void;
}

function ModuleCard({ icon, iconBg, title, description, capabilities, actionLabel, actionColor, onClick }: ModuleCardProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-7 flex flex-col">
      <div className="flex items-start gap-4 mb-4">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${iconBg}`}>
          {icon}
        </div>
        <div>
          <h2 className="text-lg font-bold text-slate-900">{title}</h2>
          <p className="text-sm text-slate-500 mt-1 leading-relaxed">{description}</p>
        </div>
      </div>

      <ul className="space-y-1.5 mb-6 flex-1">
        {capabilities.map((cap, i) => (
          <li key={i} className="flex items-center gap-2 text-sm text-slate-600">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-300 shrink-0" />
            {cap}
          </li>
        ))}
      </ul>

      <button
        onClick={onClick}
        className={`w-full py-3 px-4 rounded-xl text-white font-semibold text-sm transition-colors flex items-center justify-center gap-2 ${actionColor}`}
      >
        {actionLabel}
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
}

export default Dashboard;
