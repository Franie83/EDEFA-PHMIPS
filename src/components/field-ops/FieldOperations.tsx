import React, { useState, useEffect } from 'react';
import { MapPin, ClipboardList, Eye } from 'lucide-react';
import { SiteList } from '../sites/SiteList.tsx';
import { FieldVisitList } from '../field/FieldVisitList.tsx';
import { BeforeAfterMonitoring } from '../monitoring/BeforeAfterMonitoring.tsx';

type Tab = 'sites' | 'inspections' | 'monitoring';

interface Props {
  initialTab?: Tab;
  // Sites props
  sites: any[];
  projects: any[];
  onCreateSite: (site: any) => Promise<void> | void;
  onNavigateToMap: (lat: number, lng: number) => void;
  onEditSite?: (site: any) => void;
  onDeleteSite?: (site: any) => Promise<void> | void;
  onEditVisit?: (visit: any) => void;
  onDeleteVisit?: (visit: any) => Promise<void> | void;
  currentUser?: { role?: string; name?: string } | null;
  // Inspections props
  visits: any[];
  onOpenLogModal: () => void;
  // Monitoring props
  evidenceList: any[];
}

export const FieldOperations: React.FC<Props> = ({
  initialTab = 'sites',
  sites,
  projects,
  onCreateSite,
  onNavigateToMap,
  onEditSite,
  onDeleteSite,
  onEditVisit,
  onDeleteVisit,
  currentUser,
  visits,
  onOpenLogModal,
  evidenceList,
}) => {
  const [tab, setTab] = useState<Tab>(initialTab);

  // If App.tsx changes the deep-link while we're mounted, follow it
  useEffect(() => {
    setTab(initialTab);
  }, [initialTab]);

  const tabs: { id: Tab; label: string; icon: React.ReactNode; count?: number }[] = [
    { id: 'sites', label: 'Sites', icon: <MapPin className="w-4 h-4" />, count: sites.length },
    { id: 'inspections', label: 'Inspections', icon: <ClipboardList className="w-4 h-4" />, count: visits.length },
    { id: 'monitoring', label: 'Monitoring', icon: <Eye className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-4">
      {/* Header + tabs */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100">
          <h2 className="text-lg font-bold text-slate-900">Field Operations</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Project sites, physical inspection visits, and before/after monitoring evidence.
          </p>
        </div>
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
              {typeof t.count === 'number' && t.count > 0 && (
                <span
                  className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${
                    tab === t.id
                      ? 'bg-emerald-100 text-emerald-800'
                      : 'bg-slate-200 text-slate-600'
                  }`}
                >
                  {t.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Active tab content */}
      <div>
        {tab === 'sites' && (
          <SiteList
            sites={sites}
            projects={projects}
            onCreateSite={onCreateSite}
            onNavigateToMap={onNavigateToMap}
            onEditSite={onEditSite}
            onDeleteSite={onDeleteSite}
            currentUser={currentUser}
          />
        )}

        {tab === 'inspections' && (
          <FieldVisitList
            visits={visits}
            projects={projects}
            onOpenLogModal={onOpenLogModal}
            evidenceList={evidenceList}
            onEditVisit={onEditVisit}
            onDeleteVisit={onDeleteVisit}
            currentUser={currentUser}
          />
        )}

        {tab === 'monitoring' && (
          <BeforeAfterMonitoring
            projects={projects}
            evidenceList={evidenceList}
          />
        )}
      </div>
    </div>
  );
};