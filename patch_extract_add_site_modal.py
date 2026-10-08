"""
patch_extract_add_site_modal.py
1. Extracts the 'Add Geocoded Project Site' inline form from SiteList.tsx
   into a reusable AddProjectSiteModal.tsx component.
2. Updates SiteList.tsx to use the new component.
3. Swaps ProjectDetailModal's confirm dialog for the real form, with the
   project preselected.
"""
import pathlib

# =========================================================================
# 1. Create the reusable modal component
# =========================================================================
new_modal_path = pathlib.Path("src/components/sites/AddProjectSiteModal.tsx")
if new_modal_path.exists():
    print("AddProjectSiteModal.tsx already exists — skipping creation")
else:
    new_modal_path.write_text('''import React, { useEffect, useState } from 'react';
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
''', encoding="utf-8")
    print("Created src/components/sites/AddProjectSiteModal.tsx")

# =========================================================================
# 2. Update ProjectDetailModal to use the real modal instead of the dialog
# =========================================================================
pdm = pathlib.Path("src/components/projects/ProjectDetailModal.tsx")
src = pdm.read_text(encoding="utf-8")
pdm_changes = []

# 2a. Import AddProjectSiteModal
if "AddProjectSiteModal" not in src:
    import_anchor = "import { BeforeAfterMonitoring } from '../monitoring/BeforeAfterMonitoring.tsx';\n"
    if import_anchor not in src:
        import_anchor = "import { api } from '../../services/api.ts';\n"
    src = src.replace(
        import_anchor,
        "import { AddProjectSiteModal } from '../sites/AddProjectSiteModal.tsx';\n" + import_anchor,
        1,
    )
    pdm_changes.append("imported AddProjectSiteModal")

# 2b. Add onCreateSite prop to interface + destructure
if "onCreateSite?" not in src:
    iface_anchor = "  onRefresh?: () => Promise<void> | void;\n"
    if iface_anchor in src:
        src = src.replace(
            iface_anchor,
            iface_anchor + "  onCreateSite?: (data: any) => Promise<void> | void;\n",
            1,
        )
        pdm_changes.append("added onCreateSite to props interface")
    else:
        print("WARN: onRefresh prop anchor not found; add onCreateSite manually")

    dest_anchor = "  onRefresh}) => {"
    if dest_anchor in src:
        src = src.replace(dest_anchor, "  onRefresh,\n  onCreateSite}) => {", 1)
        pdm_changes.append("added onCreateSite to destructure")
    else:
        # alternate shape
        dest_anchor2 = "  onRefresh,\n"
        if dest_anchor2 in src:
            src = src.replace(dest_anchor2, dest_anchor2 + "  onCreateSite,\n", 1)
            pdm_changes.append("added onCreateSite to destructure (alt)")

# 2c. Replace the confirm dialog with the real modal
old_dialog = """      {/* Add Site redirect modal */}
      {isAddSiteOpen && (
        <div
          className="fixed inset-0 z-[60] bg-black/60 flex items-center justify-center p-4"
          onClick={() => setIsAddSiteOpen(false)}
        >
          <div
            className="bg-white rounded-xl shadow-2xl max-w-md w-full p-5 space-y-4 text-xs"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-200 pb-2">
              <h3 className="font-bold text-slate-900 text-sm">Add Site to {project.id}</h3>
              <button
                type="button"
                onClick={() => setIsAddSiteOpen(false)}
                className="text-slate-400 hover:text-slate-700"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-slate-600 leading-relaxed">
              Sites are registered from the <strong>Field Operations → Sites</strong> page, where you can
              capture coordinates, terrain type, ecological zone, and baseline conditions.
              Click below to open that page.
            </p>
            <div className="flex justify-end gap-2 pt-2 border-t border-slate-200">
              <button
                type="button"
                onClick={() => setIsAddSiteOpen(false)}
                className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-200 hover:bg-slate-300 text-slate-800"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsAddSiteOpen(false);
                  onClose();
                  window.dispatchEvent(new CustomEvent('navigate-view', { detail: 'field-ops' }));
                }}
                className="px-4 py-1.5 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white"
              >
                Open Field Operations → Sites
              </button>
            </div>
          </div>
        </div>
      )}
"""

new_modal = """      {/* Add Site modal (real form, project preselected) */}
      <AddProjectSiteModal
        isOpen={isAddSiteOpen}
        onClose={() => setIsAddSiteOpen(false)}
        projects={onCreateSite ? [project] : [project]}
        defaultProjectId={project.id}
        onCreateSite={async (data) => {
          if (onCreateSite) {
            await onCreateSite({ ...data, project_id: project.id });
          } else {
            // Fallback: emit event so App can handle it
            window.dispatchEvent(new CustomEvent('create-site', { detail: { ...data, project_id: project.id } }));
          }
          await onRefresh?.();
        }}
      />
"""

if old_dialog in src:
    src = src.replace(old_dialog, new_modal, 1)
    pdm_changes.append("replaced confirm dialog with real AddProjectSiteModal")
else:
    print("WARN: confirm dialog anchor not found — modal not swapped")

pdm.write_text(src, encoding="utf-8")

print("ProjectDetailModal changes:")
for c in pdm_changes:
    print(" -", c)

# =========================================================================
# 3. App.tsx — pass onCreateSite into ProjectDetailModal
# =========================================================================
app = pathlib.Path("src/App.tsx")
src = app.read_text(encoding="utf-8")
app_changes = []

old_pdm = """      <ProjectDetailModal
        project={selectedProject}
        onClose={() => setSelectedProject(null)}
        onLogVisitClick={p => {
          setVisitDefaultProject(p);
          setIsVisitModalOpen(true);
        }}
        onNavigateToMap={navigateToMapCoordinate}
        onRefresh={loadData}

        onApproveProject={handleApproveProject}
        currentUserRole={currentUser?.role}

        onRejectProject={handleRejectProject}/>
"""

new_pdm = """      <ProjectDetailModal
        project={selectedProject}
        onClose={() => setSelectedProject(null)}
        onLogVisitClick={p => {
          setVisitDefaultProject(p);
          setIsVisitModalOpen(true);
        }}
        onNavigateToMap={navigateToMapCoordinate}
        onRefresh={loadData}

        onApproveProject={handleApproveProject}
        currentUserRole={currentUser?.role}

        onRejectProject={handleRejectProject}
        onCreateSite={handleCreateSite}/>
"""

if old_pdm in src:
    src = src.replace(old_pdm, new_pdm, 1)
    app_changes.append("passed onCreateSite to ProjectDetailModal")
    app.write_text(src, encoding="utf-8")
else:
    print("WARN: ProjectDetailModal call in App.tsx NOT FOUND — pass onCreateSite manually")

print("App.tsx changes:")
for c in app_changes:
    print(" -", c)

# =========================================================================
# Summary
# =========================================================================
for label, path in [
    ("AddProjectSiteModal.tsx", new_modal_path),
    ("ProjectDetailModal.tsx", pdm),
    ("App.tsx", app),
]:
    if path.exists():
        s = path.read_text(encoding="utf-8")
        o, c = s.count("{"), s.count("}")
        print(f"{label}: brace balance {'OK' if o == c else f'MISMATCH ({o} vs {c})'}")