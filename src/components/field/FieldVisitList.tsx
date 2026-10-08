import React, { useState } from 'react';
import { SiteVisit, Project } from '../../types/index.ts';
import {
  Search,
  MapPin,
  Calendar,
  User,
  ClipboardList,
  Filter,
  X,
  RotateCcw,
  Camera,
  Video,
  Pencil,
  Trash2,
} from 'lucide-react';

interface FieldVisitListProps {
  visits: SiteVisit[];
  projects: Project[];
  onOpenLogModal: () => void;
  evidenceList?: any[];
  onEditVisit?: (visit: SiteVisit) => void;
  onDeleteVisit?: (visit: SiteVisit) => Promise<void> | void;
  currentUser?: { role?: string; name?: string } | null;
}

export const FieldVisitList: React.FC<FieldVisitListProps> = ({
  visits = [],
  projects = [],
  onOpenLogModal,
  evidenceList = [],
  onEditVisit,
  onDeleteVisit,
  currentUser,
}) => {
  const canEditDelete =
    currentUser?.role === 'SUPER_ADMIN' || currentUser?.role === 'EXECUTIVE';

  const [searchTerm, setSearchTerm] = useState('');
  const [filterProject, setFilterProject] = useState<string>('ALL');
  const [filterStage, setFilterStage] = useState<string>('ALL');
  const [filterDateFrom, setFilterDateFrom] = useState<string>('');
  const [filterDateTo, setFilterDateTo] = useState<string>('');
  const [activeMedia, setActiveMedia] = useState<{ images: any[]; index: number } | null>(null);

  // Derive filter options from actual data so nothing is ever missing
  const projectOptions = Array.from(
    new Set((visits || []).map(v => v.project_id).filter(Boolean))
  ).sort();

  const stageOptions = Array.from(
    new Set((visits || []).map(v => v.stage).filter(Boolean) as string[])
  ).sort();

  // Wildcard search across all meaningful fields
  const matchesSearch = (v: any, q: string): boolean => {
    if (!q) return true;
    const lower = q.toLowerCase();
    const haystack = [
      v.id,
      v.project_id,
      v.site_id,
      v.officer_name,
      v.purpose,
      v.weather_conditions,
      v.activities_observed,
      v.work_completed,
      v.work_outstanding,
      v.materials_equipment,
      v.quality_observations,
      v.safety_observations,
      v.problems_challenges,
      v.recommendations,
      v.officer_comments,
      v.stage,
      v.visit_date,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return haystack.includes(lower);
  };

  const filteredVisits = (visits || []).filter(v => {
    if (filterProject !== 'ALL' && v.project_id !== filterProject) return false;
    if (filterStage !== 'ALL' && v.stage !== filterStage) return false;
    if (filterDateFrom && v.visit_date < filterDateFrom) return false;
    if (filterDateTo && v.visit_date > filterDateTo) return false;
    if (!matchesSearch(v, searchTerm)) return false;
    return true;
  });

  const resetFilters = () => {
    setSearchTerm('');
    setFilterProject('ALL');
    setFilterStage('ALL');
    setFilterDateFrom('');
    setFilterDateTo('');
  };

  const hasActiveFilters =
    searchTerm !== '' ||
    filterProject !== 'ALL' ||
    filterStage !== 'ALL' ||
    filterDateFrom !== '' ||
    filterDateTo !== '';

  const projectTitle = (projectId: string) => {
    const p = (projects || []).find(pr => pr.id === projectId);
    return p ? p.title : 'Unknown project';
  };

  const handleEditClick = (visit: SiteVisit, e: React.MouseEvent) => {
    e.stopPropagation();
    if (onEditVisit) onEditVisit(visit);
  };

  const handleDeleteClick = async (visit: SiteVisit, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!onDeleteVisit) return;
    const confirmed = window.confirm(
      `Delete visit ${visit.id}?\n\n${visit.purpose}\n\nThis cannot be undone and will be recorded in the audit log.`
    );
    if (!confirmed) return;
    await onDeleteVisit(visit);
  };

  // Group evidence by visit_id
  const evidenceByVisit = (evidenceList || []).reduce((acc: any, e: any) => {
    if (!e?.visit_id) return acc;
    if (!acc[e.visit_id]) acc[e.visit_id] = [];
    acc[e.visit_id].push(e);
    return acc;
  }, {});

  return (
    <div id="field-visit-list-module" className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">
              Physical Field Inspection Visits Register
            </h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              {visits.length} Logged Visits
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Module 5: Independent supervisory site visit records, quality observations,
            milestone audits, and field recommendations.
          </p>
        </div>
        <button
          onClick={onOpenLogModal}
          className="px-4 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white inline-flex items-center gap-1.5"
        >
          <ClipboardList className="w-4 h-4" />
          Log Inspection Visit
        </button>
      </div>

      {/* Filter bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            placeholder="Wildcard search — officer, purpose, project ID, observations, materials, recommendations…"
            className="w-full pl-9 pr-9 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 text-xs"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
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
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[180px]"
            >
              <option value="ALL">All Projects ({projectOptions.length})</option>
              {projectOptions.map(pid => (
                <option key={pid} value={pid}>
                  {pid} — {projectTitle(pid as string)}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Stage
            </span>
            <select
              value={filterStage}
              onChange={e => setFilterStage(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[150px]"
            >
              <option value="ALL">All Stages ({stageOptions.length})</option>
              {stageOptions.map(s => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              From Date
            </span>
            <input
              type="date"
              value={filterDateFrom}
              onChange={e => setFilterDateFrom(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600"
            />
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              To Date
            </span>
            <input
              type="date"
              value={filterDateTo}
              onChange={e => setFilterDateTo(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600"
            />
          </label>

          {hasActiveFilters && (
            <button
              onClick={resetFilters}
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
          Showing <strong className="text-slate-700">{filteredVisits.length}</strong> of{' '}
          <strong className="text-slate-700">{visits.length}</strong> visits
          {hasActiveFilters && (
            <span className="text-emerald-700 font-semibold">— filters active</span>
          )}
        </div>
      </div>

      {/* Visits grid */}
      <div className="space-y-3">
        {filteredVisits.length === 0 && (
          <div className="bg-white p-8 rounded-xl border border-dashed border-slate-300 text-center">
            <ClipboardList className="w-8 h-8 mx-auto text-slate-300 mb-2" />
            <p className="text-sm text-slate-500">
              {visits.length === 0
                ? 'No inspection visits logged yet. Click "Log Inspection Visit" to begin.'
                : 'No visits match the current filters.'}
            </p>
          </div>
        )}

        {filteredVisits.map(visit => (
          <div
            key={visit.id}
            id={`visit-row-${visit.id}`}
            className="relative bg-white rounded-xl border border-slate-200 p-4 shadow-xs hover:border-emerald-500 transition-colors space-y-3 text-xs"
          >
            {/* Edit / Delete icons — Super Admin + Executive only */}
            {canEditDelete && (
              <div
                className="absolute top-2 right-2 flex items-center gap-1 z-10"
                onClick={(e) => e.stopPropagation()}
              >
                <button
                  onClick={(e) => handleEditClick(visit, e)}
                  title="Edit visit"
                  className="p-1 rounded bg-white/90 hover:bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200 shadow-xs"
                >
                  <Pencil className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={(e) => handleDeleteClick(visit, e)}
                  title="Delete visit"
                  className="p-1 rounded bg-white/90 hover:bg-rose-100 text-rose-700 border border-slate-200 shadow-xs"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {/* Header row */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-2">
              <div className="pr-14">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                    {visit.id}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                    {visit.stage}
                  </span>
                  <span className="font-mono text-[11px] text-emerald-800 font-semibold">
                    {visit.project_id}
                  </span>
                </div>
                <h3 className="font-bold text-slate-900 text-sm mt-1">{visit.purpose}</h3>
                <p className="text-[11px] text-slate-500">
                  {projectTitle(visit.project_id)}
                </p>
              </div>

              <div className="text-right">
                <span className="text-[10px] text-slate-400 uppercase block">
                  Progress Verified
                </span>
                <span className="font-mono text-base font-black text-emerald-800">
                  {visit.progress_percentage}%
                </span>
              </div>
            </div>

            {/* Meta row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1 flex items-center gap-1.5">
                  <Calendar className="w-3 h-3" /> Date
                </div>
                <div className="text-slate-700">{visit.visit_date}</div>
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1 flex items-center gap-1.5">
                  <User className="w-3 h-3" /> Inspected by
                </div>
                <div className="text-slate-700">{visit.officer_name}</div>
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1 flex items-center gap-1.5">
                  <MapPin className="w-3 h-3" /> GPS
                </div>
                <div className="text-slate-700 font-mono text-[11px]">
                  {visit.gps_latitude?.toFixed(5)}, {visit.gps_longitude?.toFixed(5)}
                </div>
              </div>
            </div>

            {/* Field notes */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {visit.activities_observed && (
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                  <strong className="text-slate-900 block mb-1">Activities Observed:</strong>
                  <p>{visit.activities_observed}</p>
                </div>
              )}
              {visit.materials_equipment && (
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                  <strong className="text-slate-900 block mb-1">Materials & Equipment:</strong>
                  <p>{visit.materials_equipment}</p>
                </div>
              )}
              {visit.quality_observations && (
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                  <strong className="text-slate-900 block mb-1">
                    Quality & HSE Observations:
                  </strong>
                  <p>{visit.quality_observations}</p>
                </div>
              )}
              {visit.problems_challenges && (
                <div className="p-2.5 bg-amber-50 rounded-lg border border-amber-100">
                  <strong className="text-amber-900 block mb-1">
                    Challenges & Corrective Actions:
                  </strong>
                  <p>{visit.problems_challenges}</p>
                </div>
              )}
            </div>

            {visit.recommendations && (
              <div className="p-2.5 bg-blue-50 rounded-lg border border-blue-100">
                <strong className="text-blue-900 block mb-1">Recommendation:</strong>
                <p>{visit.recommendations}</p>
              </div>
            )}

            {visit.officer_comments && (
              <div className="text-[11px] text-slate-500 italic border-t border-slate-100 pt-2">
                Officer comment: "{visit.officer_comments}"
              </div>
            )}

            {/* Evidence thumbnail strip */}
            {evidenceByVisit[visit.id]?.length > 0 && (
              <div className="pt-2 border-t border-slate-100">
                <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mb-1.5 flex items-center gap-1">
                  <Camera className="w-3 h-3" /> Evidence ({evidenceByVisit[visit.id].length})
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {evidenceByVisit[visit.id].map((e: any, __idx: number) => (
                    <div
                      key={e.id}
                      onClick={() => setActiveMedia({ images: evidenceByVisit[visit.id], index: __idx })}
                      className="relative w-16 h-16 rounded-md overflow-hidden border border-slate-200 bg-slate-100 cursor-pointer group"
                      title={e.description || e.file_name}
                    >
                      {e.media_type === 'photo' ? (
                        <img
                          src={e.file_url}
                          alt={e.file_name}
                          className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                        />
                      ) : e.media_type === 'video' ? (
                        <div className="w-full h-full flex items-center justify-center bg-slate-900">
                          <Video className="w-5 h-5 text-amber-400" />
                        </div>
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-slate-200">
                          <Camera className="w-5 h-5 text-slate-500" />
                        </div>
                      )}
                      {e.stage_tag && (
                        <span
                          className={`absolute bottom-0 inset-x-0 text-center text-[8px] font-bold uppercase tracking-wider py-0.5 ${
                            e.stage_tag === 'before'
                              ? 'bg-rose-600/90 text-white'
                              : e.stage_tag === 'during'
                              ? 'bg-amber-600/90 text-white'
                              : e.stage_tag === 'after'
                              ? 'bg-emerald-600/90 text-white'
                              : 'bg-slate-700/90 text-white'
                          }`}
                        >
                          {e.stage_tag}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Multi-image evidence lightbox with prev/next */}
      {activeMedia && (() => {
        const images = activeMedia.images || [];
        const idx = activeMedia.index || 0;
        const current = images[idx];
        if (!current) return null;
        const goPrev = () => setActiveMedia({ images, index: (idx - 1 + images.length) % images.length });
        const goNext = () => setActiveMedia({ images, index: (idx + 1) % images.length });
        return (
          <div
            className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
            onClick={() => setActiveMedia(null)}
            onKeyDown={(e) => {
              if (e.key === 'Escape') setActiveMedia(null);
              else if (e.key === 'ArrowLeft') goPrev();
              else if (e.key === 'ArrowRight') goNext();
            }}
            tabIndex={0}
            ref={(el) => el && el.focus()}
          >
            <button
              onClick={(e) => { e.stopPropagation(); goPrev(); }}
              disabled={images.length <= 1}
              className="absolute left-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white disabled:opacity-30 disabled:cursor-not-allowed z-10"
              title="Previous (←)"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15 18l-6-6 6-6" /></svg>
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); goNext(); }}
              disabled={images.length <= 1}
              className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white disabled:opacity-30 disabled:cursor-not-allowed z-10"
              title="Next (→)"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18l6-6-6-6" /></svg>
            </button>

            <div
              className="max-w-4xl w-full relative"
              onClick={(e) => e.stopPropagation()}
            >
              {images.length > 1 && (
                <div className="absolute top-2 right-2 px-2.5 py-1 rounded-full bg-black/60 text-white text-[11px] font-semibold z-10">
                  {idx + 1} of {images.length}
                </div>
              )}
              {current.media_type === 'photo' ? (
                <img
                  src={current.file_url}
                  alt={current.file_name}
                  className="w-full max-h-[80vh] object-contain rounded-lg"
                />
              ) : (
                <video key={current.id} controls autoPlay className="w-full max-h-[80vh] rounded-lg">
                  <source src={current.file_url} type="video/mp4" />
                </video>
              )}
              <div className="mt-3 text-center text-xs text-slate-300">
                <div className="font-semibold">{current.description || current.file_name}</div>
                {current.stage_tag && (
                  <div className="text-[10px] uppercase tracking-wider mt-1 text-slate-400">
                    {current.stage_tag}
                  </div>
                )}
                <button
                  onClick={() => setActiveMedia(null)}
                  className="mt-3 px-4 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-xs"
                >
                  Close (Esc)
                </button>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
};