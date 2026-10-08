import React, { useState, useEffect } from 'react';
import { X, Compass, Save, Pencil } from 'lucide-react';
import { api } from '../../services/api.ts';
import { Hazard, Intervention } from '../../types/index.ts';

interface InterventionModalProps {
  isOpen: boolean;
  onClose: () => void;
  hazard?: Hazard | null;
  onSuccess?: () => void;
  currentUser?: { role?: string; name?: string } | null;
  referenceData?: any;
  /** When provided, the modal opens in EDIT mode and PATCHes instead of POSTs. */
  existingIntervention?: Intervention | null;
}

const EMPTY_FORM = {
  title: '',
  technical_description: '',
  estimated_scope: 'Remedial ecological engineering',
  estimated_cost_ngn: '',
  proposed_funding: 'Federal Ecological Fund Direct Allocation',
  responsible_department: 'Engineering Directorate',
  responsible_officer: '',
  proposed_start_date: new Date().toISOString().split('T')[0],
  proposed_completion_date: '',
  expected_outcome: 'Stabilize and prevent loss of lives and properties',
  priority: 'MEDIUM',
};

export const InterventionModal: React.FC<InterventionModalProps> = ({
  isOpen,
  onClose,
  hazard,
  onSuccess,
  currentUser,
  referenceData,
  existingIntervention = null
}) => {
  const isEdit = Boolean(existingIntervention);

  const [form, setForm] = useState({ ...EMPTY_FORM });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  // Prefill — either from an existing intervention (edit) or from the hazard (create)
  useEffect(() => {
    if (!isOpen) return;
    setError('');

    if (existingIntervention) {
      setForm({
        title: existingIntervention.title || '',
        technical_description: (existingIntervention as any).technical_description || '',
        estimated_scope: (existingIntervention as any).estimated_scope || 'Remedial ecological engineering',
        estimated_cost_ngn: String(existingIntervention.estimated_cost_ngn ?? ''),
        proposed_funding: (existingIntervention as any).proposed_funding || 'Federal Ecological Fund Direct Allocation',
        responsible_department: (existingIntervention as any).responsible_department || 'Engineering Directorate',
        responsible_officer: (existingIntervention as any).responsible_officer || currentUser?.name || '',
        proposed_start_date: (existingIntervention as any).proposed_start_date || new Date().toISOString().split('T')[0],
        proposed_completion_date: (existingIntervention as any).proposed_completion_date || '',
        expected_outcome: (existingIntervention as any).expected_outcome || 'Stabilize and prevent loss of lives and properties',
        priority: existingIntervention.priority || 'MEDIUM',
      });
      return;
    }

    if (!hazard) return;
    setForm({
      title: `Intervention for ${hazard.title}`,
      technical_description: (hazard as any).assessment?.technical_findings || hazard.description || '',
      estimated_scope: 'Remedial ecological engineering',
      estimated_cost_ngn: '',
      proposed_funding: 'Federal Ecological Fund Direct Allocation',
      responsible_department: 'Engineering Directorate',
      responsible_officer: currentUser?.name || '',
      proposed_start_date: new Date().toISOString().split('T')[0],
      proposed_completion_date: '',
      expected_outcome: 'Stabilize and prevent loss of lives and properties',
      priority: (hazard.severity as any) || 'MEDIUM',
    });
  }, [hazard, isOpen, currentUser, existingIntervention]);

  if (!isOpen) return null;

  const set = (k: string) => (e: any) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!isEdit && !hazard) {
      setError('No hazard selected.');
      return;
    }
    if (!form.estimated_cost_ngn || isNaN(parseFloat(form.estimated_cost_ngn))) {
      setError('Estimated cost is required and must be a number.');
      return;
    }

    setBusy(true);
    try {
      const payload = {
        title: form.title,
        technical_description: form.technical_description,
        estimated_scope: form.estimated_scope,
        estimated_cost_ngn: parseFloat(form.estimated_cost_ngn),
        proposed_funding: form.proposed_funding,
        responsible_department: form.responsible_department,
        responsible_officer: form.responsible_officer,
        proposed_start_date: form.proposed_start_date,
        proposed_completion_date: form.proposed_completion_date,
        expected_outcome: form.expected_outcome,
        priority: form.priority,
      };

      if (isEdit && existingIntervention) {
        await api.updateIntervention(existingIntervention.id, payload);
      } else {
        await api.recommendIntervention(hazard!.id, payload);
      }

      onSuccess?.();
      onClose();
    } catch (err: any) {
      setError(err.message || (isEdit ? 'Failed to update intervention' : 'Failed to create intervention'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200">
        {/* Header */}
        <div className="px-6 py-4 bg-emerald-950 text-white flex items-center justify-between border-b border-emerald-900">
          <div className="flex items-center space-x-3">
            {isEdit ? (
              <Pencil className="w-6 h-6 text-amber-300" />
            ) : (
              <Compass className="w-6 h-6 text-amber-300" />
            )}
            <div>
              <h2 className="text-base font-bold">
                {isEdit ? `Edit Intervention ${existingIntervention?.id}` : 'Plan Engineering Intervention'}
              </h2>
              <p className="text-[11px] text-emerald-300">
                {isEdit
                  ? `Editing: ${existingIntervention?.title || ''}`
                  : hazard
                  ? `For hazard ${hazard.id} — ${hazard.title}`
                  : 'No hazard selected'}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={submit} className="flex-1 overflow-y-auto p-6 space-y-4 text-xs">
          {error && (
            <div className="rounded-lg bg-rose-50 border border-rose-200 text-rose-800 p-3">{error}</div>
          )}

          {isEdit && existingIntervention?.project_id && (
            <div className="rounded-lg bg-amber-50 border border-amber-200 text-amber-800 p-3">
              <strong>Note:</strong> This intervention is linked to project{' '}
              <span className="font-mono">{existingIntervention.project_id}</span>. Editing
              financial or scope fields will not automatically update the linked project.
            </div>
          )}

          <label className="block">
            <span className="font-semibold text-slate-700">Intervention Title *</span>
            <input
              required
              value={form.title}
              onChange={set('title')}
              className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
            />
          </label>

          <label className="block">
            <span className="font-semibold text-slate-700">Technical Description</span>
            <textarea
              value={form.technical_description}
              onChange={set('technical_description')}
              rows={3}
              className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 resize-y"
            />
          </label>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="block">
              <span className="font-semibold text-slate-700">Estimated Scope</span>
              <input
                value={form.estimated_scope}
                onChange={set('estimated_scope')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              />
            </label>

            <label className="block">
              <span className="font-semibold text-slate-700">Estimated Cost (NGN) *</span>
              <input
                required
                type="number"
                value={form.estimated_cost_ngn}
                onChange={set('estimated_cost_ngn')}
                placeholder="e.g. 850000000"
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 font-mono"
              />
            </label>

            <label className="block">
              <span className="font-semibold text-slate-700">Proposed Funding Source</span>
              <select
                value={form.proposed_funding}
                onChange={set('proposed_funding')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 bg-white"
              >
                {(referenceData?.funding_sources || [form.proposed_funding]).map((fs: string) => (
                  <option key={fs} value={fs}>{fs}</option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="font-semibold text-slate-700">Responsible Department</span>
              <select
                value={form.responsible_department}
                onChange={set('responsible_department')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 bg-white"
              >
                {(referenceData?.departments || [form.responsible_department]).map((d: string) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="font-semibold text-slate-700">Responsible Officer</span>
              <input
                value={form.responsible_officer}
                onChange={set('responsible_officer')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              />
            </label>

            <label className="block">
              <span className="font-semibold text-slate-700">Priority</span>
              <select
                value={form.priority}
                onChange={set('priority')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              >
                {(referenceData?.priorities || ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']).map((pr: string) => (
                  <option key={pr} value={pr}>{pr}</option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="font-semibold text-slate-700">Proposed Start Date</span>
              <input
                type="date"
                value={form.proposed_start_date}
                onChange={set('proposed_start_date')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              />
            </label>

            <label className="block">
              <span className="font-semibold text-slate-700">Proposed Completion Date</span>
              <input
                type="date"
                value={form.proposed_completion_date}
                onChange={set('proposed_completion_date')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              />
            </label>
          </div>

          <label className="block">
            <span className="font-semibold text-slate-700">Expected Outcome</span>
            <textarea
              value={form.expected_outcome}
              onChange={set('expected_outcome')}
              rows={2}
              className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 resize-y"
            />
          </label>
        </form>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-200 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700"
          >
            Cancel
          </button>
          <button
            onClick={submit}
            disabled={busy}
            className="px-5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white disabled:opacity-50 inline-flex items-center gap-1.5"
          >
            <Save className="w-4 h-4" />
            {busy
              ? (isEdit ? 'Saving…' : 'Submitting…')
              : (isEdit ? 'Save Changes' : 'Submit for Approval')}
          </button>
        </div>
      </div>
    </div>
  );
};