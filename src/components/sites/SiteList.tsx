import React, { useState } from 'react';
import { Site, Project } from '../../types/index.ts';
import { MapPin, Plus, Search, ExternalLink, Compass, Pencil, Trash2 } from 'lucide-react';
import { DirectionsLink } from '../common/DirectionsLink.tsx';

interface SiteListProps {
  sites: Site[];
  projects: Project[];
  onCreateSite: (data: Partial<Site>) => Promise<void>;
  onNavigateToMap: (lat: number, lng: number) => void;
  onEditSite?: (site: Site) => void;
  onDeleteSite?: (site: Site) => Promise<void> | void;
  currentUser?: { role?: string; name?: string } | null;
}

export const SiteList: React.FC<SiteListProps> = ({
  sites = [],
  projects = [],
  onCreateSite,
  onNavigateToMap,
  onEditSite,
  onDeleteSite,
  currentUser
}) => {
  const canEditDelete =
    currentUser?.role === 'SUPER_ADMIN' || currentUser?.role === 'EXECUTIVE';

  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    project_id: projects?.[0]?.id || '',
    state: 'Edo',
    lga: 'Egor',
    community: 'Uwelu',
    latitude: 6.3582,
    longitude: 5.5891,
    terrain_type: 'Deep Ravine / Sandy Soil',
    ecological_zone: 'Rainforest / Guinea Savannah ecotone',
    baseline_condition: 'Active headward gully scarp cutting into road easement',
    assigned_inspector: 'Engr. Chinwe Okoro'
  });

  const filtered = (sites || []).filter(s => {
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      return (
        s.name.toLowerCase().includes(q) ||
        s.community.toLowerCase().includes(q) ||
        s.lga.toLowerCase().includes(q) ||
        s.state.toLowerCase().includes(q) ||
        s.assigned_inspector.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onCreateSite(formData);
    setIsModalOpen(false);
  };

  const handleEditClick = (site: Site, e: React.MouseEvent) => {
    e.stopPropagation();
    if (onEditSite) onEditSite(site);
  };

  const handleDeleteClick = async (site: Site, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!onDeleteSite) return;
    const confirmed = window.confirm(
      `Delete site ${site.id}?\n\n"${site.name}" (${site.community}, ${site.lga})\n\nThis cannot be undone and will be recorded in the audit log.`
    );
    if (!confirmed) return;
    await onDeleteSite(site);
  };

  return (
    <div id="sites-management-module" className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">Project Sites & Baselines</h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              {sites.length} Geocoded Sites
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Module 4: Specific physical coordinates, ecological terrains, and baseline environmental conditions.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="px-3.5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white inline-flex items-center transition-colors"
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Add Project Site
        </button>
      </div>

      {/* Search */}
      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs text-xs">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search site by name, community, inspector, state..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white text-xs"
          />
        </div>
      </div>

      {/* Grid of Sites */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(site => (
          <div
            key={site.id}
            id={`site-card-${site.id}`}
            className="relative bg-white rounded-xl border border-slate-200 shadow-xs p-4 flex flex-col justify-between hover:border-emerald-500 transition-colors"
          >
            {/* Edit / Delete icons — Super Admin + Executive only */}
            {canEditDelete && (
              <div
                className="absolute top-2 right-2 flex items-center gap-1 z-10"
                onClick={(e) => e.stopPropagation()}
              >
                <button
                  onClick={(e) => handleEditClick(site, e)}
                  title="Edit site"
                  className="p-1 rounded bg-white/90 hover:bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200 shadow-xs"
                >
                  <Pencil className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={(e) => handleDeleteClick(site, e)}
                  title="Delete site"
                  className="p-1 rounded bg-white/90 hover:bg-rose-100 text-rose-700 border border-slate-200 shadow-xs"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            <div>
              <div className="flex items-center justify-between pr-14">
                <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                  {site.id}
                </span>
                <span className="text-[11px] font-bold text-emerald-800">{site.state}</span>
              </div>

              <h3 className="font-bold text-slate-900 text-sm mt-2">{site.name}</h3>
              <p className="text-xs text-slate-600 mt-0.5 flex items-center">
                <MapPin className="w-3.5 h-3.5 mr-1 text-emerald-600 shrink-0" />
                {site.community}, {site.lga}
              </p>

              <div className="mt-3 space-y-1 text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                <div><strong>Terrain:</strong> {site.terrain_type}</div>
                <div><strong>Ecological Zone:</strong> {site.ecological_zone}</div>
                <div><strong>Inspector:</strong> {site.assigned_inspector}</div>
                <div className="text-[11px] text-slate-500 pt-1">
                  <strong>Baseline:</strong> {site.baseline_condition}
                </div>
              </div>
            </div>

            <div className="mt-4 pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="font-mono text-[10px] text-slate-400">
                {site.latitude.toFixed(4)}, {site.longitude.toFixed(4)}
              </span>
              <div className="flex items-center gap-2">
                <button
                onClick={() => onNavigateToMap(site.latitude, site.longitude)}
                className="text-emerald-700 hover:text-emerald-950 font-semibold inline-flex items-center"
              >
                <ExternalLink className="w-3.5 h-3.5 mr-1" />
                View On Map
              </button>
                <DirectionsLink
                  lat={site.latitude}
                  lng={site.longitude}
                  label="Directions"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Add Site Modal (unchanged) */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-5 border border-slate-200 text-xs">
            <h3 className="text-sm font-bold text-slate-900 mb-3">Add Geocoded Project Site</h3>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="block font-semibold mb-1">Site Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Nkpor-Obosi Gully Scarp Section B"
                  value={formData.name}
                  onChange={e => setFormData({ ...formData, name: e.target.value })}
                  className="w-full p-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">Parent Project</label>
                <select
                  value={formData.project_id}
                  onChange={e => setFormData({ ...formData, project_id: e.target.value })}
                  className="w-full p-2 border rounded-lg bg-white"
                >
                  {projects.map(p => (
                    <option key={p.id} value={p.id}>{p.id} - {p.title}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold mb-1">State</label>
                  <input
                    type="text"
                    value={formData.state}
                    onChange={e => setFormData({ ...formData, state: e.target.value })}
                    className="w-full p-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1">LGA</label>
                  <input
                    type="text"
                    value={formData.lga}
                    onChange={e => setFormData({ ...formData, lga: e.target.value })}
                    className="w-full p-2 border rounded-lg"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold mb-1">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={formData.latitude}
                    onChange={e => setFormData({ ...formData, latitude: parseFloat(e.target.value) || 0 })}
                    className="w-full p-2 border rounded-lg font-mono"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={formData.longitude}
                    onChange={e => setFormData({ ...formData, longitude: parseFloat(e.target.value) || 0 })}
                    className="w-full p-2 border rounded-lg font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold mb-1">Baseline Environmental Condition</label>
                <textarea
                  rows={2}
                  value={formData.baseline_condition}
                  onChange={e => setFormData({ ...formData, baseline_condition: e.target.value })}
                  className="w-full p-2 border rounded-lg"
                />
              </div>

              <div className="pt-3 border-t flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-emerald-700 text-white font-bold"
                >
                  Save Site
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};