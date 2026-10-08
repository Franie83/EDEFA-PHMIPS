import React, { useState, useEffect } from 'react';
import { Project, ProjectStatus, Intervention } from '../../types/index.ts';
import { X, FolderGit2, Save, Send, Link2, Pencil } from 'lucide-react';
import { api } from '../../services/api.ts';
import { ManageContractorsModal } from './ManageContractorsModal.tsx';
import { Contractor } from '../../types/index.ts';

interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<Project>) => Promise<void>;
  statesAndLgas: Record<string, string[]>;
  categories: string[];
  prefillInterventionId?: string;
  referenceData?: any;
  /** When provided, the modal opens in EDIT mode and prefills all fields. */
  existingProject?: Project | null;
}

export const ProjectModal: React.FC<ProjectModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories,
  prefillInterventionId,
  referenceData,
  existingProject = null
}) => {
  const isEdit = Boolean(existingProject);

  const [formData, setFormData] = useState({
    intervention_id: '',
    title: '',
    category: categories[0] || 'Gully Erosion Remediation',
    description: '',
    state: Object.keys(statesAndLgas)[0] || 'Anambra',
    lga: '',
    ward: '',
    community: '',
    site_name: '',
    latitude: 6.2209,
    longitude: 7.0722,
    funding_source: 'Federal Ecological Fund (EPO)',
    approved_amount_ngn: 450000000,
    contract_amount_ngn: 420000000,
    contractor: '',
    implementing_agency: 'Ecological Project Office (EPO)',
    start_date: new Date().toISOString().split('T')[0],
    expected_completion_date: '2026-12-31',
    planned_percentage: 10,
    actual_percentage: 0,
    status: 'Pending Approval' as ProjectStatus,
    remarks: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Executive-Approved interventions available for project registration
  const [approvedInterventions, setApprovedInterventions] = useState<Intervention[]>([]);
  const [interventionsLoading, setInterventionsLoading] = useState(false);

  const [contractorList, setContractorList] = useState<Contractor[]>([]);
  const [contractorsLoading, setContractorsLoading] = useState(false);
  const [showManageContractors, setShowManageContractors] = useState(false);

  const availableLgas = statesAndLgas[formData.state] || [];

  // -- Edit mode: prefill everything from existingProject and skip LGA auto-fix --
  useEffect(() => {
    if (!isOpen || !existingProject) return;
    setFormData({
      intervention_id: (existingProject as any).intervention_id || '',
      title: existingProject.title || '',
      category: existingProject.category || categories[0] || 'Gully Erosion Remediation',
      description: (existingProject as any).description || '',
      state: existingProject.state || Object.keys(statesAndLgas)[0] || 'Anambra',
      lga: existingProject.lga || '',
      ward: (existingProject as any).ward || '',
      community: existingProject.community || '',
      site_name: (existingProject as any).site_name || '',
      latitude: Number((existingProject as any).latitude ?? 6.2209),
      longitude: Number((existingProject as any).longitude ?? 7.0722),
      funding_source: (existingProject as any).funding_source || 'Federal Ecological Fund (EPO)',
      approved_amount_ngn: Number((existingProject as any).approved_amount_ngn ?? 0),
      contract_amount_ngn: Number((existingProject as any).contract_amount_ngn ?? 0),
      contractor: (existingProject as any).contractor || '',
      implementing_agency: (existingProject as any).implementing_agency || 'Ecological Project Office (EPO)',
      start_date: (existingProject as any).start_date || new Date().toISOString().split('T')[0],
      expected_completion_date: (existingProject as any).expected_completion_date || '2026-12-31',
      planned_percentage: Number((existingProject as any).planned_percentage ?? 10),
      actual_percentage: Number((existingProject as any).actual_percentage ?? 0),
      status: (existingProject.status as ProjectStatus) || 'Pending Approval',
      remarks: (existingProject as any).remarks || ''
    });
  }, [isOpen, existingProject]);

  useEffect(() => {
    // Skip auto-fix of LGA when we are editing a project — keep whatever was saved.
    if (isEdit) return;
    if (availableLgas.length > 0 && !availableLgas.includes(formData.lga)) {
      setFormData(prev => ({ ...prev, lga: availableLgas[0] }));
    }
  }, [formData.state, availableLgas, isEdit]);

  // Fetch active contractors when the modal opens
  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    setContractorsLoading(true);
    (async () => {
      try {
        const list = await api.getContractors();
        if (!cancelled) setContractorList(list || []);
      } catch (err) {
        console.error('Failed to load contractors:', err);
      } finally {
        if (!cancelled) setContractorsLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [isOpen]);

  // Fetch Executive-Approved interventions when the modal opens (create mode only)
  useEffect(() => {
    if (!isOpen) return;
    if (isEdit) return;
    let cancelled = false;
    setInterventionsLoading(true);
    (async () => {
      try {
        const all = await api.getInterventions();
        const approved = (all || []).filter((i: any) =>
          i.approval_status === 'Executive Approved' &&
          !i.project_id
        );
        if (!cancelled) setApprovedInterventions(approved);
      } catch (err) {
        console.error('Failed to load approved interventions:', err);
      } finally {
        if (!cancelled) setInterventionsLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [isOpen, isEdit]);

  // Prefill from an externally supplied intervention (e.g. from Intervention Planning "Create Project" button)
  useEffect(() => {
    if (!isOpen) return;
    if (isEdit) return;
    if (!prefillInterventionId) return;
    if (approvedInterventions.length === 0) return;
    const iv = approvedInterventions.find(i => i.id === prefillInterventionId);
    if (!iv) return;
    if (formData.intervention_id === prefillInterventionId) return;
    setFormData(prev => ({
      ...prev,
      intervention_id: prefillInterventionId,
      title: prev.title || `Project for ${iv.title}`,
      description: prev.description || iv.technical_description || iv.estimated_scope || '',
      approved_amount_ngn: iv.estimated_cost_ngn || prev.approved_amount_ngn,
      contract_amount_ngn: iv.estimated_cost_ngn
        ? Math.round(iv.estimated_cost_ngn * 0.95)
        : prev.contract_amount_ngn,
    }));
  }, [isOpen, prefillInterventionId, approvedInterventions, isEdit]);

  // Auto-fill project fields when an intervention is selected
  const handleInterventionSelect = (interventionId: string) => {
    if (!interventionId) {
      setFormData(prev => ({ ...prev, intervention_id: '' }));
      return;
    }
    const iv = approvedInterventions.find(i => i.id === interventionId);
    if (!iv) return;
    setFormData(prev => ({
      ...prev,
      intervention_id: interventionId,
      title: prev.title || `Project for ${iv.title}`,
      description: prev.description || iv.technical_description || iv.estimated_scope || '',
      approved_amount_ngn: iv.estimated_cost_ngn || prev.approved_amount_ngn,
      contract_amount_ngn: iv.estimated_cost_ngn
        ? Math.round(iv.estimated_cost_ngn * 0.95)
        : prev.contract_amount_ngn,
    }));
  };

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isEdit && !formData.intervention_id) {
      alert('Please select an approved intervention. Projects must be created from an Executive-Approved intervention.');
      return;
    }
    if (!formData.title || !formData.contractor || !formData.community) {
      alert('Please fill out the project title, contractor, and community location.');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      onClose();
    } catch (err: any) {
      alert(err.message || (isEdit ? 'Error updating project' : 'Error creating project'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
    <div id="project-create-modal" className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200 text-xs">
        {/* Header */}
        <div className="px-6 py-4 bg-emerald-950 text-white flex items-center justify-between border-b border-emerald-900">
          <div className="flex items-center space-x-2">
            {isEdit ? (
              <Pencil className="w-5 h-5 text-amber-400" />
            ) : (
              <FolderGit2 className="w-5 h-5 text-amber-400" />
            )}
            <div>
              <h2 className="text-base font-bold text-white">
                {isEdit ? `Edit Project ${existingProject?.id}` : 'Create New Ecological Project'}
              </h2>
              <p className="text-xs text-emerald-300">
                {isEdit
                  ? 'Update project details. Changes are recorded in the audit log.'
                  : 'Register approved engineering intervention in the national register'}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-md text-emerald-300 hover:text-white hover:bg-emerald-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4 text-slate-700">
          {/* Approved Intervention Selector — only in CREATE mode */}
          {!isEdit && (
            <div className="p-3 rounded-lg bg-amber-50 border border-amber-200">
              <label className="block">
                <span className="font-bold text-amber-900 flex items-center gap-1.5">
                  <Link2 className="w-4 h-4" />
                  Approved Intervention * (required)
                </span>
                <select
                  required
                  value={formData.intervention_id}
                  onChange={e => handleInterventionSelect(e.target.value)}
                  disabled={interventionsLoading}
                  className="mt-2 w-full px-3 py-2 rounded-lg border border-amber-300 bg-white outline-none focus:border-emerald-600"
                >
                  <option value="">
                    {interventionsLoading
                      ? 'Loading approved interventions…'
                      : approvedInterventions.length === 0
                      ? '— No Executive-Approved interventions available —'
                      : '— Select an Executive-Approved intervention —'}
                  </option>
                  {approvedInterventions.map(iv => (
                    <option key={iv.id} value={iv.id}>
                      {iv.id} — {iv.title} (₦{((iv.estimated_cost_ngn || 0) / 1e6).toFixed(1)}M)
                    </option>
                  ))}
                </select>
                {approvedInterventions.length === 0 && !interventionsLoading && (
                  <p className="text-[11px] text-amber-700 mt-1">
                    No approved interventions available. Ask a Director to propose an intervention,
                    then have Executive approve it before creating a project.
                  </p>
                )}
              </label>
            </div>
          )}

          {/* Edit mode: show the linked intervention as read-only */}
          {isEdit && formData.intervention_id && (
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
              <span className="font-bold text-slate-700 flex items-center gap-1.5">
                <Link2 className="w-4 h-4" />
                Linked Intervention
              </span>
              <p className="mt-1 font-mono text-slate-600 text-[11px]">{formData.intervention_id}</p>
              <p className="text-[11px] text-slate-500 mt-0.5">
                The linked intervention cannot be changed after project creation.
              </p>
            </div>
          )}

          <div>
            <label className="block font-semibold mb-1 text-slate-800">Project Title *</label>
            <input
              type="text"
              required
              placeholder="e.g., Construction of Stormwater Drainage and Ravine Stabilization Works at..."
              value={formData.title}
              onChange={e => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-1 focus:ring-emerald-600"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block font-semibold mb-1 text-slate-800">Ecological Category</label>
              <select
                value={formData.category}
                onChange={e => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
              >
                {categories.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Project Status</label>
              <select
                value={formData.status}
                onChange={e => setFormData({ ...formData, status: e.target.value as ProjectStatus })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
              >
                <option value="Active">Active</option>
                <option value="Procurement">Procurement</option>
                <option value="Approved">Approved</option>
                <option value="Proposed">Proposed</option>
                <option value="Delayed">Delayed</option>
                <option value="Completed">Completed</option>
                <option value="Suspended">Suspended</option>
                <option value="Rejected">Rejected</option>
                <option value="Pending Approval">Pending Approval</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Funding Source</label>
              <select
                value={formData.funding_source}
                onChange={e => setFormData({ ...formData, funding_source: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
              >
                {(referenceData?.funding_sources || [formData.funding_source]).map((fs: string) => (
                  <option key={fs} value={fs}>{fs}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Implementing Agency</label>
              <select
                value={formData.implementing_agency}
                onChange={e => setFormData({ ...formData, implementing_agency: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
              >
                {(referenceData?.implementing_agencies || [formData.implementing_agency]).map((a: string) => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block font-semibold mb-1 text-slate-800">Approved Budget (NGN)</label>
              <input
                type="number"
                value={formData.approved_amount_ngn}
                onChange={e => setFormData({ ...formData, approved_amount_ngn: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 font-mono"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Contract Value (NGN) *</label>
              <input
                type="number"
                required
                value={formData.contract_amount_ngn}
                onChange={e => setFormData({ ...formData, contract_amount_ngn: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 font-mono"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Contractor Name *</label>
              <select
                value={formData.contractor}
                onChange={e => setFormData({ ...formData, contractor: e.target.value })}
                disabled={contractorsLoading}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              >
                <option value="">
                  {contractorsLoading ? 'Loading contractors…' : '— Select a registered contractor —'}
                </option>
                {contractorList.map(c => (
                  <option key={c.id} value={c.name}>
                    {c.name} ({c.registration_no || c.id})
                  </option>
                ))}
              </select>

              <button
                type="button"
                onClick={() => setShowManageContractors(true)}
                className="mt-2 inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 hover:text-emerald-900"
              >
                ⚙️ Manage Contractors
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            <div>
              <label className="block font-semibold mb-1 text-slate-800">State *</label>
              <select
                value={formData.state}
                onChange={e => setFormData({ ...formData, state: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
              >
                {Object.keys(statesAndLgas).map(st => (
                  <option key={st} value={st}>{st}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">LGA *</label>
              <select
                value={formData.lga}
                onChange={e => setFormData({ ...formData, lga: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
              >
                {availableLgas.map(l => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Community *</label>
              <input
                type="text"
                required
                value={formData.community}
                onChange={e => setFormData({ ...formData, community: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Site Name / Section</label>
              <input
                type="text"
                value={formData.site_name}
                onChange={e => setFormData({ ...formData, site_name: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            <div>
              <label className="block font-semibold mb-1 text-slate-800">Latitude</label>
              <input
                type="number"
                step="0.000001"
                value={formData.latitude}
                onChange={e => setFormData({ ...formData, latitude: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 font-mono"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Longitude</label>
              <input
                type="number"
                step="0.000001"
                value={formData.longitude}
                onChange={e => setFormData({ ...formData, longitude: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 font-mono"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Start Date</label>
              <input
                type="date"
                value={formData.start_date}
                onChange={e => setFormData({ ...formData, start_date: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Expected End Date</label>
              <input
                type="date"
                value={formData.expected_completion_date}
                onChange={e => setFormData({ ...formData, expected_completion_date: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300"
              />
            </div>
          </div>

          {/* Progress fields — only in EDIT mode */}
          {isEdit && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold mb-1 text-slate-800">Planned Progress (%)</label>
                <input
                  type="number"
                  min={0}
                  max={100}
                  value={formData.planned_percentage}
                  onChange={e => setFormData({ ...formData, planned_percentage: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 font-mono"
                />
              </div>
              <div>
                <label className="block font-semibold mb-1 text-slate-800">Actual Progress (%)</label>
                <input
                  type="number"
                  min={0}
                  max={100}
                  value={formData.actual_percentage}
                  onChange={e => setFormData({ ...formData, actual_percentage: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 font-mono"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block font-semibold mb-1 text-slate-800">Civil Engineering Scope & Description *</label>
            <textarea
              rows={3}
              required
              placeholder="Describe concrete drains, stone pitching, retaining walls, gabions, culverts, re-vegetation..."
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-300"
            />
          </div>

          <div className="pt-4 border-t border-slate-200 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white font-bold inline-flex items-center"
            >
              {isEdit ? <Save className="w-4 h-4 mr-1.5" /> : <Send className="w-4 h-4 mr-1.5" />}
              {isSubmitting
                ? (isEdit ? 'Saving...' : 'Registering...')
                : (isEdit ? 'Save Changes' : 'Register Project')}
            </button>
          </div>
        </form>
      </div>
    </div>
      <ManageContractorsModal
        isOpen={showManageContractors}
        onClose={() => setShowManageContractors(false)}
        onChanged={async () => {
          try {
            const list = await api.getContractors();
            setContractorList(list || []);
          } catch (err) {
            console.error('Failed to refresh contractors:', err);
          }
        }}
      />
    </>
  );
};