import React, { useState, useMemo } from 'react';
import { AlertTriangle, Compass, CheckSquare } from 'lucide-react';
import { HazardList } from './HazardList.tsx';
import { InterventionPlanning } from '../interventions/InterventionPlanning.tsx';
import { VerificationWorkspace } from '../verification/VerificationWorkspace.tsx';
import { Hazard, Intervention, Project } from '../../types/index.ts';

type Tab = 'hazards' | 'interventions' | 'verification';

interface Props {
  // Hazard list props
  hazards: Hazard[];
  statesAndLgas: Record<string, string[]>;
  categories: string[];
  onSelectHazard: (h: Hazard) => void;
  onNewReportClick: () => void;
  onVerifyHazard: (h: Hazard) => void;

  // Intervention planning props
  interventions: Intervention[];
  projects: Project[];
  onUpdateIntervention: (id: string, data: Partial<Intervention>) => Promise<void>;
  currentUser: any;
  onRefresh: () => Promise<void> | void;
  referenceData: any;

  // Verification tab props
  onVerify?: (hazardId: string, isValid: boolean, notes: string, requestInspection: boolean) => Promise<any>;
  onAssess?: (hazardId: string, assessmentData: any) => Promise<any>;
  onRecommendIntervention?: (hazardId: string, interventionData: any) => Promise<any>;

  // Optional initial tab + optional preselected hazard for the verification queue
  initialTab?: Tab;
  initialHazardId?: string;

  // Intervention edit/delete (forwarded to InterventionPlanning)
  onEditIntervention?: (iv: Intervention) => void;
  onDeleteIntervention?: (iv: Intervention) => Promise<void> | void;
}

export const HazardReportsTabs: React.FC<Props> = ({
  hazards,
  statesAndLgas,
  categories,
  onSelectHazard,
  onNewReportClick,
  onVerifyHazard,
  interventions,
  projects,
  onUpdateIntervention,
  currentUser,
  onRefresh,
  referenceData,
  onVerify,
  onAssess,
  onRecommendIntervention,
  initialTab = 'hazards',
  initialHazardId,
  onEditIntervention,
  onDeleteIntervention,
}) => {
  const [tab, setTab] = useState<Tab>(initialTab);

  // Which hazard the user explicitly asked to verify (from a register row)
  const [verificationHazardId, setVerificationHazardId] = useState<string | undefined>(undefined);

  // 1) De-dupe by id, keeping whichever object carries more fields
  //    (detail records win over lean list records).
  const uniqueHazards = useMemo(() => {
    const map = new Map<string, Hazard>();
    for (const h of hazards) {
      const existing = map.get(h.id);
      if (!existing) {
        map.set(h.id, h);
      } else if (Object.keys(h).length > Object.keys(existing).length) {
        map.set(h.id, h);
      }
    }
    return Array.from(map.values());
  }, [hazards]);

  // 2) Hazards still inside the verification pipeline
  //    (not yet fully approved / intervention registered).
  const verificationQueue = useMemo(
    () =>
      uniqueHazards.filter((h: any) => {
        if (h.recommended_intervention || h.intervention) return false;
        if (h.status === 'Intervention Approved') return false;
        return true;
      }),
    [uniqueHazards]
  );

  // 3) Badge: count only hazards still awaiting verification.
  const pendingVerifications = verificationQueue.filter(
    (h: any) =>
      h.status === 'Submitted' ||
      h.status === 'Pending Verification' ||
      h.status === 'Under Review' ||
      !h.verified_by
  ).length;

  const tabs: { id: Tab; label: string; icon: React.ReactNode; count: number }[] = [
    { id: 'hazards', label: 'Hazard Reports', icon: <AlertTriangle className="w-4 h-4" />, count: uniqueHazards.length },
    { id: 'interventions', label: 'Interventions', icon: <Compass className="w-4 h-4" />, count: interventions.length },
    { id: 'verification', label: 'Verification & Assessment', icon: <CheckSquare className="w-4 h-4" />, count: pendingVerifications },
  ];

  return (
    <div className="space-y-4">
      {/* Tab bar */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="flex border-b border-slate-100 bg-slate-50/50">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t.id
                  ? 'border-emerald-600 text-emerald-800 bg-white'
                  : 'border-transparent text-slate-500 hover:text-slate-800 hover:bg-white/60'
              }`}
            >
              {t.icon}
              {t.label}
              <span
                className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${
                  tab === t.id
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-slate-200 text-slate-600'
                }`}
              >
                {t.count}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Active tab content */}
      {tab === 'hazards' && (
        <HazardList
          hazards={uniqueHazards}
          statesAndLgas={statesAndLgas}
          categories={categories}
          onSelectHazard={onSelectHazard}
          onNewReportClick={onNewReportClick}
          onVerifyHazard={(h) => {
            // Switch to the verification tab AND preselect that hazard.
            setVerificationHazardId(h.id);
            setTab('verification');
            // Fire the parent's callback if provided (for audit / telemetry).
            onVerifyHazard?.(h);
          }}
        />
      )}

      {tab === 'interventions' && (
        <InterventionPlanning
          interventions={interventions}
          hazards={uniqueHazards}
          projects={projects}
          onUpdateIntervention={onUpdateIntervention}
          currentUser={currentUser}
          onRefresh={onRefresh}
          referenceData={referenceData}
          hideHeader
          onEditIntervention={onEditIntervention}
          onDeleteIntervention={onDeleteIntervention}
        />
      )}

      {tab === 'verification' && (
        <VerificationWorkspace
          hazards={verificationQueue}
          referenceData={referenceData}
          onVerify={onVerify}
          onAssess={onAssess}
          onRecommendIntervention={onRecommendIntervention}
          onSelectHazard={onSelectHazard}
          initialHazardId={verificationHazardId ?? initialHazardId}
        />
      )}
    </div>
  );
};