import React, { useState } from 'react';
import { Evidence, Project, Hazard } from '../../types/index.ts';
import {
  Camera,
  Video,
  FileText,
  Search,
  Download,
  Filter,
  Eye,
  MapPin,
  Calendar,
  X,
  Play,
  RotateCcw,
  Layers,
  Building2
} from 'lucide-react';

interface EvidenceRepositoryProps {
  evidenceList: Evidence[];
  projects: Project[];
  hazards: Hazard[];
  onUploadClick: () => void;
}

export const EvidenceRepository: React.FC<EvidenceRepositoryProps> = ({
  evidenceList = [],
  projects = [],
  hazards = [],
  onUploadClick
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [mediaFilter, setMediaFilter] = useState<string>('ALL');
  const [stageFilter, setStageFilter] = useState<string>('ALL');
  const [projectFilter, setProjectFilter] = useState<string>('ALL');
  const [activeMedia, setActiveMedia] = useState<Evidence | null>(null);

  // Extended filter state
  const [entityFilter, setEntityFilter] = useState<'ALL' | 'HAZARD' | 'PROJECT' | 'SITE' | 'VISIT'>('ALL');
  const [uploaderFilter, setUploaderFilter] = useState<string>('ALL');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');

  // Derive filter options from actual data
  const mediaOptions = Array.from(
    new Set((evidenceList || []).map(e => e.media_type).filter(Boolean) as string[])
  ).sort();

  const stageOptions = Array.from(
    new Set((evidenceList || []).map(e => e.stage_tag).filter(Boolean) as string[])
  ).sort();

  const uploaderOptions = Array.from(
    new Set((evidenceList || []).map(e => e.uploader_name).filter(Boolean) as string[])
  ).sort();

  // Count evidence per project (for dropdown annotations)
  const countEvidenceForProject = (projectId: string): number =>
    (evidenceList || []).filter(e => e.project_id === projectId).length;

  // Classify what entity an evidence file is linked to
  const linkedEntity = (e: any): { type: 'HAZARD' | 'PROJECT' | 'SITE' | 'VISIT' | 'NONE'; id: string } => {
    if (e.hazard_id) return { type: 'HAZARD', id: e.hazard_id };
    if (e.project_id) return { type: 'PROJECT', id: e.project_id };
    if (e.site_id) return { type: 'SITE', id: e.site_id };
    if (e.visit_id) return { type: 'VISIT', id: e.visit_id };
    return { type: 'NONE', id: '' };
  };

  // Human-readable file size
  const formatBytes = (bytes: number): string => {
    if (!bytes || bytes <= 0) return '—';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Wildcard search across all fields
  const matchesSearch = (e: any, q: string): boolean => {
    if (!q) return true;
    const lower = q.toLowerCase();
    const haystack = [
      e.id,
      e.file_name,
      e.file_type,
      e.media_type,
      e.stage_tag,
      e.description,
      e.uploader_name,
      e.uploader_id,
      e.hazard_id,
      e.project_id,
      e.site_id,
      e.visit_id,
      e.upload_date,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return haystack.includes(lower);
  };

  const filteredEvidence = (evidenceList || []).filter(e => {
    if (mediaFilter !== 'ALL' && e.media_type !== mediaFilter) return false;
    if (stageFilter !== 'ALL' && e.stage_tag !== stageFilter) return false;
    if (projectFilter !== 'ALL' && e.project_id !== projectFilter) return false;
    if (entityFilter !== 'ALL') {
      const linked = linkedEntity(e);
      if (linked.type !== entityFilter) return false;
    }
    if (uploaderFilter !== 'ALL' && e.uploader_name !== uploaderFilter) return false;
    if (dateFrom && e.upload_date && e.upload_date < dateFrom) return false;
    if (dateTo && e.upload_date && e.upload_date > (dateTo + 'T23:59:59')) return false;
    if (!matchesSearch(e, searchTerm)) return false;
    return true;
  });

  const resetEvidenceFilters = () => {
    setSearchTerm('');
    setMediaFilter('ALL');
    setStageFilter('ALL');
    setProjectFilter('ALL');
    setEntityFilter('ALL');
    setUploaderFilter('ALL');
    setDateFrom('');
    setDateTo('');
  };

  const evidenceHasActiveFilters =
    searchTerm !== '' ||
    mediaFilter !== 'ALL' ||
    stageFilter !== 'ALL' ||
    projectFilter !== 'ALL' ||
    entityFilter !== 'ALL' ||
    uploaderFilter !== 'ALL' ||
    dateFrom !== '' ||
    dateTo !== '';

  return (
    <div id="evidence-repository-module" className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">State Evidence & Multimedia Repository</h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              {evidenceList.length} Files
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Module 7: Tamper-evident repository of field photos, drone videos, site visit proofs, and technical documents.
          </p>
        </div>

        <button
          onClick={onUploadClick}
          className="px-3.5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white inline-flex items-center transition-colors shadow-xs"
        >
          <Camera className="w-4 h-4 mr-1.5" />
          Upload Evidence
        </button>
      </div>

      {/* Evidence filter bar */}
      <div
        id="evidence-filter-bar"
        className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3"
      >
        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            placeholder="Wildcard search — file name, description, uploader, IDs, dates, stage…"
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

        {/* Dropdowns */}
        <div className="flex flex-wrap items-end gap-3 text-xs">
          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Media
            </span>
            <select
              value={mediaFilter}
              onChange={e => setMediaFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[150px]"
            >
              <option value="ALL">All Types ({mediaOptions.length})</option>
              {mediaOptions.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Stage
            </span>
            <select
              value={stageFilter}
              onChange={e => setStageFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[150px]"
            >
              <option value="ALL">All Stages ({stageOptions.length})</option>
              {stageOptions.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Project
            </span>
            <select
              value={projectFilter}
              onChange={e => setProjectFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[260px]"
            >
              <option value="ALL">All Projects ({projects.length})</option>
              {projects.map(p => {
                const count = countEvidenceForProject(p.id);
                const label = `${p.id} — ${p.title.slice(0, 42)}${p.title.length > 42 ? '…' : ''} (${count})`;
                return (
                  <option key={p.id} value={p.id}>{label}</option>
                );
              })}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Related Entity
            </span>
            <select
              value={entityFilter}
              onChange={e => setEntityFilter(e.target.value as any)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[160px]"
            >
              <option value="ALL">All Entities</option>
              <option value="HAZARD">Hazard-linked</option>
              <option value="PROJECT">Project-linked</option>
              <option value="SITE">Site-linked</option>
              <option value="VISIT">Visit-linked</option>
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Uploader
            </span>
            <select
              value={uploaderFilter}
              onChange={e => setUploaderFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[180px]"
            >
              <option value="ALL">All Uploaders ({uploaderOptions.length})</option>
              {uploaderOptions.map(u => (
                <option key={u} value={u}>{u}</option>
              ))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              From Date
            </span>
            <input
              type="date"
              value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600"
            />
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              To Date
            </span>
            <input
              type="date"
              value={dateTo}
              onChange={e => setDateTo(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600"
            />
          </label>

          {evidenceHasActiveFilters && (
            <button
              onClick={resetEvidenceFilters}
              className="px-3 py-2 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 inline-flex items-center gap-1.5 h-[38px]"
              title="Reset all filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Filters
            </button>
          )}
        </div>

        {/* Result count */}
        <div className="text-[11px] text-slate-500 border-t border-slate-100 pt-2 flex items-center gap-2">
          <Filter className="w-3.5 h-3.5" />
          Showing <strong className="text-slate-700">{filteredEvidence.length}</strong> of{' '}
          <strong className="text-slate-700">{evidenceList.length}</strong> files
          {evidenceHasActiveFilters && (
            <span className="text-emerald-700 font-semibold">— filters active</span>
          )}
        </div>
      </div>

      {/* Grid of Evidence Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
        {filteredEvidence.map(item => (
          <div
            key={item.id}
            id={`evidence-card-${item.id}`}
            onClick={() => setActiveMedia(item)}
            className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden cursor-pointer hover:border-emerald-500 hover:shadow-md transition-all flex flex-col justify-between group"
          >
            {/* Thumbnail */}
            <div className="relative h-36 bg-slate-900 overflow-hidden">
              {item.media_type === 'photo' ? (
                <img
                  src={item.file_url}
                  alt={item.file_name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              ) : item.media_type === 'video' ? (
                <div className="w-full h-full flex flex-col items-center justify-center text-white">
                  <Play className="w-10 h-10 text-amber-400 fill-amber-400 mb-1" />
                  <span className="text-[10px] font-semibold text-slate-300">Video Recording</span>
                </div>
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-white">
                  <FileText className="w-10 h-10 text-emerald-400 mb-1" />
                  <span className="text-[10px] font-semibold text-slate-300">Document</span>
                </div>
              )}

              {item.stage_tag && (
                <span
                  className={`absolute top-2 left-2 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${
                    item.stage_tag === 'before'
                      ? 'bg-rose-900/90 text-white'
                      : item.stage_tag === 'during'
                      ? 'bg-amber-900/90 text-white'
                      : 'bg-emerald-900/90 text-white'
                  }`}
                >
                  {item.stage_tag}
                </span>
              )}
            </div>

            {/* Info */}
            <div className="p-2.5 text-xs flex-1 flex flex-col justify-between">
              <div>
                <h4 className="font-semibold text-slate-900 line-clamp-1" title={item.file_name}>
                  {item.file_name}
                </h4>
                <p className="text-[11px] text-slate-500 line-clamp-2 mt-0.5 leading-tight">
                  {item.description}
                </p>
              </div>

              <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span>{(item.file_size / 1024).toFixed(0)} KB</span>
                <span>{item.upload_date}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Lightbox Modal */}
      {activeMedia && (
        <div
          onClick={() => setActiveMedia(null)}
          className="fixed inset-0 z-50 bg-black/85 flex items-center justify-center p-4"
        >
          <div
            onClick={e => e.stopPropagation()}
            className="bg-slate-900 rounded-xl max-w-3xl w-full p-4 text-white space-y-3"
          >
            <div className="flex items-center justify-between border-b border-slate-700 pb-2">
              <div>
                <h3 className="font-bold text-sm">{activeMedia.file_name}</h3>
                <p className="text-xs text-slate-400">{activeMedia.description}</p>
              </div>
              <button
                onClick={() => setActiveMedia(null)}
                className="p-1 rounded bg-slate-800 text-slate-300 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="max-h-[68vh] flex items-center justify-center bg-black/50 rounded-lg overflow-hidden">
              {activeMedia.media_type === 'photo' ? (
                <img
                  src={activeMedia.file_url}
                  alt={activeMedia.file_name}
                  className="max-h-[64vh] w-auto object-contain"
                />
              ) : activeMedia.media_type === 'video' ? (
                <video controls autoPlay className="max-h-[64vh] w-full">
                  <source src={activeMedia.file_url} type="video/mp4" />
                  Your browser does not support HTML5 video.
                </video>
              ) : (
                <div className="p-12 text-center text-slate-400">
                  <FileText className="w-16 h-16 mx-auto mb-2 text-emerald-400" />
                  <p className="text-sm font-semibold text-white">{activeMedia.file_name}</p>
                  <p className="text-xs mt-1">Official Technical Document / Survey Report</p>
                </div>
              )}
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
              <span>Uploaded by {activeMedia.uploader_name} on {activeMedia.upload_date}</span>
              {activeMedia.gps_latitude && (
                <span className="font-mono text-[11px]">
                  GPS: {activeMedia.gps_latitude.toFixed(5)}, {activeMedia.gps_longitude?.toFixed(5)}
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};