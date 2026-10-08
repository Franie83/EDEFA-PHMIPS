"""
Build the "Plan Engineering Intervention" workflow end-to-end.

Creates:
  src/components/interventions/InterventionModal.tsx   (new file)

Patches:
  src/services/api.ts
    - adds createIntervention method
  src/components/interventions/InterventionPlanning.tsx
    - adds "New Intervention" button + modal open state
  src/components/hazards/HazardDetailModal.tsx
    - rewires "Plan Engineering Intervention" to open the modal
  src/App.tsx
    - wires the modal, handler, and passes the selected hazard

Idempotent.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "src" / "services" / "api.ts"
INTERV = ROOT / "src" / "components" / "interventions" / "InterventionPlanning.tsx"
HAZMODAL = ROOT / "src" / "components" / "hazards" / "HazardDetailModal.tsx"
APP = ROOT / "src" / "App.tsx"
MODAL = ROOT / "src" / "components" / "interventions" / "InterventionModal.tsx"

for f in [API, INTERV, HAZMODAL, APP]:
    if not f.exists():
        raise SystemExit(f"Not found: {f}")

# ============================================================
# CREATE — InterventionModal.tsx
# ============================================================
print("=" * 60)
print("CREATE: InterventionModal.tsx")
print("=" * 60)

if MODAL.exists():
    print("  Already exists — skipping.")
else:
    MODAL.write_text('''import React, { useState, useEffect } from 'react';
import { X, Compass, Save } from 'lucide-react';
import { api } from '../../services/api.ts';
import { Hazard } from '../../types/index.ts';

interface InterventionModalProps {
  isOpen: boolean;
  onClose: () => void;
  hazard?: Hazard | null;
  onSuccess?: () => void;
  currentUser?: { role?: string; name?: string } | null;
}

export const InterventionModal: React.FC<InterventionModalProps> = ({
  isOpen,
  onClose,
  hazard,
  onSuccess,
  currentUser
}) => {
  const [form, setForm] = useState({
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
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  // Prefill from hazard when opening
  useEffect(() => {
    if (!hazard || !isOpen) return;
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
    setError('');
  }, [hazard, isOpen, currentUser]);

  if (!isOpen) return null;

  const set = (k: string) => (e: any) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!hazard) { setError('No hazard selected.'); return; }
    if (!form.estimated_cost_ngn || isNaN(parseFloat(form.estimated_cost_ngn))) {
      setError('Estimated cost is required and must be a number.');
      return;
    }
    setBusy(true);
    try {
      await api.recommendIntervention(hazard.id, {
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
      });
      onSuccess?.();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to create intervention');
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
            <Compass className="w-6 h-6 text-amber-300" />
            <div>
              <h2 className="text-base font-bold">Plan Engineering Intervention</h2>
              <p className="text-[11px] text-emerald-300">
                {hazard ? `For hazard ${hazard.id} — ${hazard.title}` : 'No hazard selected'}
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
              <input
                value={form.proposed_funding}
                onChange={set('proposed_funding')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              />
            </label>

            <label className="block">
              <span className="font-semibold text-slate-700">Responsible Department</span>
              <input
                value={form.responsible_department}
                onChange={set('responsible_department')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              />
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
                <option value="CRITICAL">CRITICAL</option>
                <option value="HIGH">HIGH</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="LOW">LOW</option>
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
            {busy ? 'Submitting…' : 'Submit for Approval'}
          </button>
        </div>
      </div>
    </div>
  );
};
''', encoding="utf-8")
    print(f"  Created {MODAL.name}")

# ============================================================
# PATCH 1 — api.ts — add createIntervention
# ============================================================
print()
print("=" * 60)
print("PATCH 1: api.ts — createIntervention")
print("=" * 60)

text = API.read_text(encoding="utf-8")

if "createIntervention:" in text:
    print("  Already present.")
else:
    anchor = "  // Approval flow — Stage 1: Intervention approvals"
    method = """  // Intervention creation from a hazard
  createIntervention: (hazard_id: string, data: any) =>
    request<{ success: boolean; intervention: Intervention; hazard: Hazard }>(`/hazards/${hazard_id}/intervention`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

"""
    if anchor in text:
        text = text.replace(anchor, method + anchor, 1)
        API.write_text(text, encoding="utf-8")
        print("  Added createIntervention")
    else:
        print("  WARNING: anchor not found in api.ts")

# ============================================================
# PATCH 2 — InterventionPlanning.tsx — New Intervention button + modal
# ============================================================
print()
print("=" * 60)
print("PATCH 2: InterventionPlanning.tsx")
print("=" * 60)

text = INTERV.read_text(encoding="utf-8")

# 2a: import modal + Plus icon
if "InterventionModal" not in text:
    if "from './InterventionModal.tsx'" not in text:
        old = "import { api } from '../../services/api.ts';"
        new = "import { api } from '../../services/api.ts';\nimport { InterventionModal } from './InterventionModal.tsx';"
        if old in text:
            text = text.replace(old, new, 1)
            print("  Imported InterventionModal")
        else:
            print("  WARNING: import anchor not found")

# 2b: add state for modal
if "isNewModalOpen" not in text:
    anchor = "const [approvalBusy, setApprovalBusy] = useState<string | null>(null);"
    if anchor in text:
        text = text.replace(
            anchor,
            anchor + "\n  const [isNewModalOpen, setIsNewModalOpen] = useState(false);",
            1,
        )
        print("  Added isNewModalOpen state")
    else:
        print("  WARNING: approvalBusy anchor not found")

# 2c: add "New Intervention" button in the header
if "Plan New Intervention" not in text:
    # Insert button in header next to the total cost
    old = """        <div className="flex items-center space-x-3 text-right">
          <div>
            <span className="text-[10px] text-slate-400 uppercase block font-semibold">Total Pipeline Budget</span>
            <span className="font-mono text-base font-black text-emerald-800">
              ₦{(totalCost / 1e9).toFixed(2)} Billion
            </span>
          </div>
        </div>"""
    new = """        <div className="flex items-center space-x-3">
          <div className="text-right">
            <span className="text-[10px] text-slate-400 uppercase block font-semibold">Total Pipeline Budget</span>
            <span className="font-mono text-base font-black text-emerald-800">
              ₦{(totalCost / 1e9).toFixed(2)} Billion
            </span>
          </div>
          <button
            onClick={() => setIsNewModalOpen(true)}
            className="px-3 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white inline-flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            Plan New Intervention
          </button>
        </div>"""
    if old in text:
        text = text.replace(old, new, 1)
        print("  Added 'Plan New Intervention' button")
    else:
        print("  WARNING: header anchor not found")

# 2d: render the modal at the end of the component
if "<InterventionModal" not in text:
    # Find the last closing `</div>` of the component root
    # Insert before the final `);\n};`
    closing = "\n    </div>\n  );\n};"
    modal_jsx = """
      <InterventionModal
        isOpen={isNewModalOpen}
        onClose={() => setIsNewModalOpen(false)}
        hazard={null}
        currentUser={currentUser}
        onSuccess={async () => { await onRefresh?.(); }}
      />
    </div>
  );
};"""
    if closing in text:
        text = text.replace(closing, modal_jsx, 1)
        print("  Rendered InterventionModal at end of component")
    else:
        print("  WARNING: closing tag anchor not found")

INTERV.write_text(text, encoding="utf-8")

# ============================================================
# PATCH 3 — HazardDetailModal.tsx — rewire Plan Intervention button
# ============================================================
print()
print("=" * 60)
print("PATCH 3: HazardDetailModal.tsx")
print("=" * 60)

text = HAZMODAL.read_text(encoding="utf-8")

if "onPlanIntervention" not in text:
    # Extend prop interface
    old = "  onEdit?: (hazard: Hazard) => void;"
    if old in text:
        text = text.replace(
            old,
            old + "\n  onPlanIntervention?: (hazard: Hazard) => void;",
            1,
        )
        print("  Added onPlanIntervention prop")
    else:
        print("  WARNING: props anchor not found")

    # Extend destructure
    old = "  onEdit,\n  onDelete,"
    if old in text:
        text = text.replace(
            old,
            "  onEdit,\n  onDelete,\n  onPlanIntervention,",
            1,
        )
        print("  Extended destructure")
    else:
        print("  WARNING: destructure anchor not found")

    # Rewire the button
    old = 'onClick={() => onInterventionClick(hazard)}'
    if old in text:
        text = text.replace(
            old,
            "onClick={() => onPlanIntervention ? onPlanIntervention(hazard) : onInterventionClick(hazard)}",
            1,
        )
        print("  Rewired 'Plan Engineering Intervention' button")
    else:
        print("  WARNING: button onClick anchor not found")

HAZMODAL.write_text(text, encoding="utf-8")

# ============================================================
# PATCH 4 — App.tsx — pass onPlanIntervention + handle modal
# ============================================================
print()
print("=" * 60)
print("PATCH 4: App.tsx")
print("=" * 60)

text = APP.read_text(encoding="utf-8")

# 4a: import modal
if "InterventionModal" not in text:
    old = "import { InterventionPlanning } from './components/interventions/InterventionPlanning.tsx';"
    if old in text:
        text = text.replace(
            old,
            old + "\nimport { InterventionModal } from './components/interventions/InterventionModal.tsx';",
            1,
        )
        print("  Imported InterventionModal")
    else:
        print("  WARNING: import anchor not found")

# 4b: add state
if "planInterventionFor" not in text:
    old = "const [editingHazard, setEditingHazard] = useState<Hazard | null>(null);"
    if old in text:
        text = text.replace(
            old,
            old + "\n  const [planInterventionFor, setPlanInterventionFor] = useState<Hazard | null>(null);",
            1,
        )
        print("  Added planInterventionFor state")
    else:
        print("  WARNING: editingHazard anchor not found")

# 4c: pass onPlanIntervention to HazardDetailModal
old = "onEdit={canEditFn(currentUser?.role) ? (h) => { setEditingHazard(h); setSelectedHazard(null); } : undefined}"
if old in text and "onPlanIntervention" not in text:
    text = text.replace(
        old,
        old + "\n        onPlanIntervention={(h) => { setPlanInterventionFor(h); setSelectedHazard(null); }}",
        1,
    )
    print("  Passed onPlanIntervention to HazardDetailModal")

# 4d: render the InterventionModal at the bottom of the app
if "<InterventionModal" not in text:
    # Find the FieldVisitForm block (last modal) and insert after it
    anchor = """      <FieldVisitForm
        isOpen={isVisitModalOpen}
        onClose={() => setIsVisitModalOpen(false)}
        onSubmit={handleLogVisit}
        projects={projects}
        sites={sites}
        defaultProject={visitDefaultProject}
      />"""
    new_block = anchor + """

      <InterventionModal
        isOpen={Boolean(planInterventionFor)}
        onClose={() => setPlanInterventionFor(null)}
        hazard={planInterventionFor}
        currentUser={currentUser}
        onSuccess={async () => { await loadData(); }}
      />"""
    if anchor in text:
        text = text.replace(anchor, new_block, 1)
        print("  Rendered InterventionModal at end of App")
    else:
        print("  WARNING: FieldVisitForm anchor not found")

APP.write_text(text, encoding="utf-8")

print()
print("=" * 60)
print("COMPLETE")
print("=" * 60)
print("""
Next steps:
  1. npx tsc --noEmit       (should be clean)
  2. Reload the browser
  3. Log in as inspector (Director)
  4. Open a hazard → click "Plan Engineering Intervention"
  5. Fill the form → submit
  6. The new intervention appears in Module 9 with status "Proposed"
  7. The hazard's status becomes "Intervention Recommended"
  8. As Director, approve → as Executive, approve
  9. As Director, create the project from the approved intervention
""")