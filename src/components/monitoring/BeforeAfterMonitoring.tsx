import React, { useState, useEffect, useMemo } from 'react';
import { Project, Evidence, Intervention } from '../../types/index.ts';
import { api } from '../../services/api.ts';
import {
  Eye,
  Sliders,
  Calendar,
  Layers,
  Camera,
  ChevronRight,
  ArrowRightLeft,
  Maximize2,
  Search,
  X,
  Filter,
  RotateCcw
} from 'lucide-react';

interface BeforeAfterMonitoringProps {
  projects: Project[];
  evidenceList?: Evidence[];
  compact?: boolean;
  /** Optional — if the parent already has interventions loaded, pass them
   *  to avoid an extra fetch. Otherwise the component fetches them itself. */
  interventions?: Intervention[];
}

export const BeforeAfterMonitoring: React.FC<BeforeAfterMonitoringProps> = ({
  projects = [],
  evidenceList = [],
  compact = false,
  interventions: interventionsProp
}) => {
  const [selectedProjectId, setSelectedProjectId] = useState<string>(projects[0]?.id || '');
  const [sliderPosition, setSliderPosition] = useState<number>(50);
  const [comparisonMode, setComparisonMode] = useState<'slider' | 'side-by-side'>('slider');

  // --- Filter state ---
  const [monitorSearch, setMonitorSearch] = useState('');
  const [monitorEvidenceFilter, setMonitorEvidenceFilter] = useState<
    'ALL' | 'COMPLETE' | 'MISSING_AFTER' | 'MISSING_BEFORE' | 'NO_EVIDENCE'
  >('ALL');
  const [monitorSort, setMonitorSort] = useState<'id' | 'evidence_count' | 'name'>('id');
  const [filterProject, setFilterProject] = useState<string>('ALL');

  // --- Self-fetch evidence + interventions if not provided ---
  const [selfEvidence, setSelfEvidence] = useState<Evidence[] | null>(null);
  const [selfInterventions, setSelfInterventions] = useState<Intervention[] | null>(null);

  useEffect(() => {
    // Only self-fetch if the parent didn't pass a non-empty evidence list
    if (evidenceList && evidenceList.length > 0) {
      setSelfEvidence(null);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const all = await api.getEvidence();
        if (!cancelled) setSelfEvidence((all || []) as any);
      } catch (err) {
        console.warn('[BeforeAfterMonitoring] evidence fetch failed', err);
      }
    })();
    return () => { cancelled = true; };
  }, [evidenceList]);

  useEffect(() => {
    if (interventionsProp && interventionsProp.length > 0) {
      setSelfInterventions(null);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const all = await api.getInterventions();
        if (!cancelled) setSelfInterventions((all || []) as any);
      } catch (err) {
        console.warn('[BeforeAfterMonitoring] interventions fetch failed', err);
      }
    })();
    return () => { cancelled = true; };
  }, [interventionsProp]);

  const effectiveEvidence = useMemo(
    () => (evidenceList && evidenceList.length > 0 ? evidenceList : selfEvidence || []),
    [evidenceList, selfEvidence]
  );

  const effectiveInterventions = useMemo(
    () =>
      (interventionsProp && interventionsProp.length > 0
        ? interventionsProp
        : selfInterventions || []) as any[],
    [interventionsProp, selfInterventions]
  );

  // --- Build a fast lookup: project.id -> set of hazard_ids and visit_ids ---
  const projectLinkMap = useMemo(() => {
    const map = new Map<string, { hazardIds: Set<string>; visitIds: Set<string> }>();
    for (const p of projects || []) {
      const hazardIds = new Set<string>();
      const visitIds = new Set<string>();

      // Direct hazard links
      const directHazard = (p as any).hazard_id || (p as any).linked_hazard_id;
      if (directHazard) hazardIds.add(directHazard);

      // Linked hazards array
      for (const h of (p as any).linked_hazards || []) {
        if (h?.id) hazardIds.add(h.id);
      }

      // Trace intervention_id -> intervention.hazard_id
      const interventionId = (p as any).intervention_id;
      if (interventionId) {
        const iv = effectiveInterventions.find((x: any) => x.id === interventionId);
        if (iv?.hazard_id) hazardIds.add(iv.hazard_id);
      }

      // Site visits under this project
      for (const v of (p as any).site_visits || []) {
        if (v?.id) visitIds.add(v.id);
      }

      map.set(p.id, { hazardIds, visitIds });
    }
    return map;
  }, [projects, effectiveInterventions]);

  // --- Evidence resolver: given a project, return all linked evidence ---
  const evidenceForProject = (projectId: string): Evidence[] => {
    const links = projectLinkMap.get(projectId);
    if (!links) return [];
    const { hazardIds, visitIds } = links;

    return (effectiveEvidence || []).filter((e: any) => {
      if (e.project_id && e.project_id === projectId) return true;
      if (e.hazard_id && hazardIds.has(e.hazard_id)) return true;
      if (e.visit_id && visitIds.has(e.visit_id)) return true;
      return false;
    });
  };

  const selectedProject = (projects || []).find(p => p.id === selectedProjectId) || (projects || [])[0];

  const projectEvidence = selectedProject ? evidenceForProject(selectedProject.id) : [];

  const beforeItems = (projectEvidence || []).filter((e: any) => e.stage_tag === 'before');
  const duringItems = (projectEvidence || []).filter((e: any) => e.stage_tag === 'during');
  const afterItems = (projectEvidence || []).filter((e: any) => e.stage_tag === 'after' || e.stage_tag === 'evidence');

  const countByStage = (projectId: string) => {
    const ev = evidenceForProject(projectId);
    return {
      before: ev.filter((e: any) => e.stage_tag === 'before').length,
      during: ev.filter((e: any) => e.stage_tag === 'during').length,
      after: ev.filter((e: any) => e.stage_tag === 'after' || e.stage_tag === 'evidence').length,
      total: ev.length,
    };
  };

  const classifyProject = (projectId: string): 'COMPLETE' | 'MISSING_AFTER' | 'MISSING_BEFORE' | 'NO_EVIDENCE' => {
    const c = countByStage(projectId);
    if (c.total === 0) return 'NO_EVIDENCE';
    if (c.before > 0 && c.after > 0) return 'COMPLETE';
    if (c.before > 0 && c.after === 0) return 'MISSING_AFTER';
    if (c.before === 0 && c.after > 0) return 'MISSING_BEFORE';
    return 'NO_EVIDENCE';
  };

  const matchesMonitorSearch = (p: any, q: string): boolean => {
    if (!q) return true;
    const lower = q.toLowerCase();
    const haystack = [
      p.id,
      p.title,
      p.community,
      p.lga,
      p.state,
      p.contractor,
      p.category,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return haystack.includes(lower);
  };

  const filteredProjects = (projects || [])
    .filter(p => {
      if (filterProject !== 'ALL' && p.id !== filterProject) return false;
      if (!matchesMonitorSearch(p, monitorSearch)) return false;
      if (monitorEvidenceFilter !== 'ALL') {
        if (classifyProject(p.id) !== monitorEvidenceFilter) return false;
      }
      return true;
    })
    .sort((a, b) => {
      if (monitorSort === 'evidence_count') {
        return countByStage(b.id).total - countByStage(a.id).total;
      }
      if (monitorSort === 'name') {
        return (a.title || '').localeCompare(b.title || '');
      }
      return a.id.localeCompare(b.id);
    });

  React.useEffect(() => {
    if (filterProject !== 'ALL') {
      setSelectedProjectId(filterProject);
    }
  }, [filterProject]);

  // If the selected project isn't in the current project list, snap to the first one
  React.useEffect(() => {
    if (!projects.some(p => p.id === selectedProjectId)) {
      setSelectedProjectId(projects[0]?.id || '');
    }
  }, [projects, selectedProjectId]);

  const resetMonitorFilters = () => {
    setMonitorSearch('');
    setMonitorEvidenceFilter('ALL');
    setMonitorSort('id');
    setFilterProject('ALL');
  };

  const monitorHasActiveFilters =
    monitorSearch !== '' ||
    monitorEvidenceFilter !== 'ALL' ||
    monitorSort !== 'id' ||
    filterProject !== 'ALL';

  // Fallback sample images only used if the project truly has no evidence
  const defaultBefore = beforeItems[0]?.file_url || '';
  const defaultAfter = afterItems[0]?.file_url || duringItems[0]?.file_url || '';

  const hasBefore = Boolean(defaultBefore);
  const hasAfter = Boolean(defaultAfter);

  return (
    <div id="monitoring-module" className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">Before & After Ecological Monitoring</h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              Visual Transformation
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Module 6: Longitudinal chronological photographic audit comparing pre-intervention degradation against post-civil works remediation.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <button
            onClick={() => setComparisonMode('slider')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
              comparisonMode === 'slider' ? 'bg-emerald-800 text-white' : 'bg-slate-100 text-slate-700'
            }`}
          >
            Interactive Split Slider
          </button>
          <button
            onClick={() => setComparisonMode('side-by-side')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
              comparisonMode === 'side-by-side' ? 'bg-emerald-800 text-white' : 'bg-slate-100 text-slate-700'
            }`}
          >
            Chronological Gallery
          </button>
        </div>
      </div>

      {/* Monitoring filter bar */}
      <div
        id="monitor-filter-bar"
        className={`${compact ? 'hidden' : ''} bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3`}
      >
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={monitorSearch}
            onChange={e => setMonitorSearch(e.target.value)}
            placeholder="Wildcard search — project ID, title, community, LGA, contractor, category…"
            className="w-full pl-9 pr-9 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 text-xs"
          />
          {monitorSearch && (
            <button
              onClick={() => setMonitorSearch('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded hover:bg-slate-100 text-slate-400"
              title="Clear search"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <div className="flex flex-wrap items-end gap-3 text-xs">
          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Project
            </span>
            <select
              value={filterProject}
              onChange={e => setFilterProject(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[240px]"
            >
              <option value="ALL">All Projects ({projects.length})</option>
              {projects.map(p => {
                const c = countByStage(p.id);
                return (
                  <option key={p.id} value={p.id}>
                    {p.id} — {p.title.slice(0, 40)}{p.title.length > 40 ? '…' : ''} ({c.total})
                  </option>
                );
              })}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Evidence Status
            </span>
            <select
              value={monitorEvidenceFilter}
              onChange={e => setMonitorEvidenceFilter(e.target.value as any)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[200px]"
            >
              <option value="ALL">All Statuses</option>
              <option value="COMPLETE">✓ Complete (before + after)</option>
              <option value="MISSING_AFTER">⚠ Missing After</option>
              <option value="MISSING_BEFORE">⚠ Missing Before</option>
              <option value="NO_EVIDENCE">○ No Evidence</option>
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Sort By
            </span>
            <select
              value={monitorSort}
              onChange={e => setMonitorSort(e.target.value as any)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[180px]"
            >
              <option value="id">Project ID</option>
              <option value="evidence_count">Evidence Count (high to low)</option>
              <option value="name">Project Name (A–Z)</option>
            </select>
          </label>

          {monitorHasActiveFilters && (
            <button
              onClick={resetMonitorFilters}
              className="px-3 py-2 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 inline-flex items-center gap-1.5 h-[38px]"
              title="Reset all filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Filters
            </button>
          )}
        </div>

        <div className="text-[11px] text-slate-500 border-t border-slate-100 pt-2 flex items-center gap-2">
          <Filter className="w-3.5 h-3.5" />
          Showing <strong className="text-slate-700">{filteredProjects.length}</strong> of{' '}
          <strong className="text-slate-700">{projects.length}</strong> projects
          {monitorHasActiveFilters && (
            <span className="text-emerald-700 font-semibold">— filters active</span>
          )}
        </div>
      </div>

      {/* Project Selector Bar */}
      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center gap-3 text-xs">
        <span className="font-bold text-slate-700 uppercase tracking-wider text-[11px]">
          Select Project:
        </span>
        <select
          value={selectedProjectId}
          onChange={e => setSelectedProjectId(e.target.value)}
          className="flex-1 min-w-[300px] py-2 px-3 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 bg-slate-50/50 focus:bg-white"
        >
          {(filteredProjects || []).map(p => {
            const c = countByStage(p.id);
            const cls = classifyProject(p.id);
            const icon = cls === 'COMPLETE' ? '✓' : cls === 'NO_EVIDENCE' ? '○' : '⚠';
            const label =
              cls === 'COMPLETE' ? 'Complete' :
              cls === 'NO_EVIDENCE' ? 'No evidence' :
              cls === 'MISSING_AFTER' ? 'Missing after' :
              'Missing before';
            return (
              <option key={p.id} value={p.id}>
                {icon} {p.id} — {p.title} — {c.before}B/{c.during}D/{c.after}A ({label})
              </option>
            );
          })}
        </select>
        {filteredProjects.length === 0 && (
          <span className="text-[11px] text-slate-500 italic">
            No projects match the current filters.
          </span>
        )}
      </div>

      {/* Empty-state banner if the selected project has no evidence */}
      {selectedProject && projectEvidence.length === 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-900">
          <strong className="block mb-1">No evidence attached to this project yet.</strong>
          <p>
            Evidence is linked to this project when a field inspector logs a visit with photos, or
            when the project's linked hazard receives evidence.
          </p>
        </div>
      )}

      {/* Interactive Split Slider View */}
      {comparisonMode === 'slider' ? (
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-rose-100 text-rose-800">
                BEFORE (Baseline Gully Degradation)
              </span>
              <ArrowRightLeft className="w-4 h-4 text-slate-400" />
              <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-emerald-100 text-emerald-800">
                AFTER (Stabilized & Remediated)
              </span>
            </div>
            <span className="text-xs text-slate-500 font-mono">
              Drag horizontal slider below to wipe
            </span>
          </div>

          <div className="relative w-full h-[450px] rounded-xl overflow-hidden shadow-inner select-none border border-slate-300 bg-slate-100">
            {hasAfter ? (
              <img
                src={defaultAfter}
                alt="Remediated condition"
                className="absolute inset-0 w-full h-full object-cover"
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-xs">
                No AFTER photo available
              </div>
            )}
            <div className="absolute top-4 right-4 bg-emerald-950/80 backdrop-blur-xs text-white px-3 py-1 rounded-md text-xs font-bold shadow-md">
              AFTER (Civil Works Completed)
            </div>

            {hasBefore && (
              <div
                className="absolute inset-y-0 left-0 overflow-hidden"
                style={{ width: `${sliderPosition}%` }}
              >
                <img
                  src={defaultBefore}
                  alt="Baseline condition"
                  className="absolute inset-0 w-full h-full object-cover max-w-none"
                  style={{ width: '100%', minWidth: '100%', height: '100%' }}
                />
                <div className="absolute top-4 left-4 bg-rose-950/80 backdrop-blur-xs text-white px-3 py-1 rounded-md text-xs font-bold shadow-md">
                  BEFORE (Pre-Intervention Hazard)
                </div>
              </div>
            )}

            {hasBefore && hasAfter && (
              <div
                className="absolute inset-y-0 w-1 bg-white shadow-2xl cursor-ew-resize flex items-center justify-center"
                style={{ left: `${sliderPosition}%` }}
              >
                <div className="w-7 h-7 rounded-full bg-emerald-950 text-white flex items-center justify-center border-2 border-white shadow-lg text-xs font-bold">
                  ↔
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-4">
            <span className="text-xs font-bold text-slate-700">Wipe Control:</span>
            <input
              type="range"
              min="0"
              max="100"
              value={sliderPosition}
              onChange={e => setSliderPosition(parseInt(e.target.value))}
              className="flex-1 accent-emerald-700 cursor-ew-resize"
            />
            <span className="font-mono text-xs font-bold text-slate-800">{sliderPosition}%</span>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl border border-rose-200 p-4 shadow-xs space-y-3">
            <div className="flex items-center justify-between border-b border-rose-100 pb-2">
              <span className="font-bold text-xs uppercase text-rose-800">
                1. Before (Baseline Hazard)
              </span>
              <span className="text-[10px] text-slate-500 font-mono">Stage 1</span>
            </div>
            <div className="h-60 rounded-lg overflow-hidden bg-slate-100 border border-slate-200 flex items-center justify-center">
              {beforeItems[0]?.file_url ? (
                <img src={beforeItems[0].file_url} alt="Before" className="h-full w-full object-cover" />
              ) : (
                <span className="text-xs text-slate-400">No before photo</span>
              )}
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Baseline condition recorded before engineering intervention. {beforeItems.length} photo(s).
            </p>
          </div>

          <div className="bg-white rounded-xl border border-amber-200 p-4 shadow-xs space-y-3">
            <div className="flex items-center justify-between border-b border-amber-100 pb-2">
              <span className="font-bold text-xs uppercase text-amber-800">
                2. During (Civil Works)
              </span>
              <span className="text-[10px] text-slate-500 font-mono">Stage 2</span>
            </div>
            <div className="h-60 rounded-lg overflow-hidden bg-slate-100 border border-slate-200 flex items-center justify-center">
              {duringItems[0]?.file_url ? (
                <img src={duringItems[0].file_url} alt="During" className="h-full w-full object-cover" />
              ) : (
                <span className="text-xs text-slate-400">No during photo</span>
              )}
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Construction phase evidence. {duringItems.length} photo(s).
            </p>
          </div>

          <div className="bg-white rounded-xl border border-emerald-200 p-4 shadow-xs space-y-3">
            <div className="flex items-center justify-between border-b border-emerald-100 pb-2">
              <span className="font-bold text-xs uppercase text-emerald-800">
                3. After (Remediated Site)
              </span>
              <span className="text-[10px] text-slate-500 font-mono">Stage 3</span>
            </div>
            <div className="h-60 rounded-lg overflow-hidden bg-slate-100 border border-slate-200 flex items-center justify-center">
              {afterItems[0]?.file_url ? (
                <img src={afterItems[0].file_url} alt="After" className="h-full w-full object-cover" />
              ) : (
                <span className="text-xs text-slate-400">No after photo</span>
              )}
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Post-intervention verification. {afterItems.length} photo(s).
            </p>
          </div>
        </div>
      )}
    </div>
  );
};