import React, { useEffect, useState } from 'react';
import { Site, Project } from '../../types/index.ts';

interface AddProjectSiteModalProps {
  isOpen: boolean;
  onClose: () => void;
  projects: Project[];
  defaultProjectId?: string;
  onCreateSite: (data: Partial<Site>) => Promise<void> | void;
}

export const AddProjectSiteModal: React.FC<AddProjectSiteModalProps> = ({
  isOpen,
  onClose,
  projects = [],
  defaultProjectId,
  onCreateSite,
}) => {
  const [formData, setFormData] = useState<any>({
    name: '',
    project_id: defaultProjectId || projects?.[0]?.id || '',
    state: 'Edo',
    lga: 'Egor',
    community: 'Uwelu',
    latitude: 6.3582,
    longitude: 5.5891,
    terrain_type: 'Deep Ravine / Sandy Soil',
    ecological_zone: 'Rainforest / Guinea Savannah ecotone',
    baseline_condition: 'Active headward gully scarp cutting into road easement',
    assigned_inspector: 'Engr. Chinwe Okoro',
  });

  // Reset form when the modal reopens (especially the default project).
  useEffect(() => {
    if (isOpen) {
      setFormData((prev: any) => ({
        ...prev,
        project_id: defaultProjectId || prev.project_id || projects?.[0]?.id || '',
      }));
    }
  }, [isOpen, defaultProjectId, projects]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onCreateSite(formData);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[70] bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3">
      <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-5 border border-slate-200 text-xs">
        <h3 className="text-sm font-bold text-slate-900 mb-3">Add Geocoded Project Site</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block font-semibold mb-1">Site Name *</label>
            <input
              required
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Nkpor-Obosi Gully Scarp Section B"
              className="w-full px-2.5 py-1.5 rounded border border-slate-300 focus:border-emerald-600 outline-none"
            />
          </div>

          <div>
            <label className="block font-semibold mb-1">Parent Project</label>
            <select
              value={formData.project_id}
              onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
              className="w-full px-2.5 py-1.5 rounded border border-slate-300 focus:border-emerald-600 outline-none"
            >
              <option value="">— Select —</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.id} — {p.title}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold mb-1">State</label>
              <input
                type="text"
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                className="w-full px-2.5 py-1.5 rounded border border-slate-300 focus:border-emerald-600 outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold mb-1">LGA</label>
              <input
                type="text"
                value={formData.lga}
                onChange={(e) => setFormData({ ...formData, lga: e.target.value })}
                className="w-full px-2.5 py-1.5 rounded border border-slate-300 focus:border-emerald-600 outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold mb-1">Latitude</label>
              <input
                type="number"
                step="0.000001"
                value={formData.latitude}
                onChange={(e) => setFormData({ ...formData, latitude: parseFloat(e.target.value) })}
                className="w-full px-2.5 py-1.5 rounded border border-slate-300 focus:border-emerald-600 outline-none font-mono"
              />
            </div>
            <div>
              <label className="block font-semibold mb-1">Longitude</label>
              <input
                type="number"
                step="0.000001"
                value={formData.longitude}
                onChange={(e) => setFormData({ ...formData, longitude: parseFloat(e.target.value) })}
                className="w-full px-2.5 py-1.5 rounded border border-slate-300 focus:border-emerald-600 outline-none font-mono"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold mb-1">Baseline Environmental Condition</label>
            <textarea
              rows={3}
              value={formData.baseline_condition}
              onChange={(e) => setFormData({ ...formData, baseline_condition: e.target.value })}
              className="w-full px-2.5 py-1.5 rounded border border-slate-300 focus:border-emerald-600 outline-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold"
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
  );
};
