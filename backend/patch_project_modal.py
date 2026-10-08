"""
Patch ProjectModal.tsx to add an approved-intervention selector.

When opened as Director (to register a project from an approved intervention):
  - Shows a dropdown of Executive-Approved interventions
  - Selecting one auto-fills title, category, budget, community
  - Submits with `intervention_id` so the backend can validate

Also changes the default project status from "Active" to "Pending Approval"
so the Executive approval step becomes meaningful.

Idempotent.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "projects" / "ProjectModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "approvedInterventions" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# ============================================================
# 1. Update imports to include api + Intervention type
# ============================================================
old_imports = """import React, { useState, useEffect } from 'react';
import { Project, ProjectStatus } from '../../types/index.ts';
import { X, FolderGit2, Save, Send } from 'lucide-react';"""

new_imports = """import React, { useState, useEffect } from 'react';
import { Project, ProjectStatus, Intervention } from '../../types/index.ts';
import { X, FolderGit2, Save, Send, Link2 } from 'lucide-react';
import { api } from '../../services/api.ts';"""

if old_imports in text:
    text = text.replace(old_imports, new_imports, 1)
    print("  Updated imports")
else:
    print("  WARNING: import block not found in expected form")

# ============================================================
# 2. Add intervention_id to form state + change default status
# ============================================================
old_state = """  const [formData, setFormData] = useState({
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
    status: 'Active' as ProjectStatus,
    remarks: ''
  });"""

new_state = """  const [formData, setFormData] = useState({
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

  // Executive-Approved interventions available for project registration
  const [approvedInterventions, setApprovedInterventions] = useState<Intervention[]>([]);
  const [interventionsLoading, setInterventionsLoading] = useState(false);"""

if old_state in text:
    text = text.replace(old_state, new_state, 1)
    print("  Updated form state (added intervention_id, changed default status)")
else:
    print("  WARNING: form state block not found in expected form")

# ============================================================
# 3. Add useEffect to fetch approved interventions when modal opens
# ============================================================
anchor = """  useEffect(() => {
    if (availableLgas.length > 0 && !availableLgas.includes(formData.lga)) {
      setFormData(prev => ({ ...prev, lga: availableLgas[0] }));
    }
  }, [formData.state, availableLgas]);"""

new_effect = anchor + """

  // Fetch Executive-Approved interventions when the modal opens
  useEffect(() => {
    if (!isOpen) return;
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
  }, [isOpen]);

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
  };"""

if anchor in text:
    text = text.replace(anchor, new_effect, 1)
    print("  Added intervention fetch + auto-fill logic")
else:
    print("  WARNING: useEffect anchor not found")

# ============================================================
# 4. Require intervention_id in the submit validation
# ============================================================
old_validate = """    if (!formData.title || !formData.contractor || !formData.community) {
      alert('Please fill out the project title, contractor, and community location.');
      return;
    }"""

new_validate = """    if (!formData.intervention_id) {
      alert('Please select an approved intervention. Projects must be created from an Executive-Approved intervention.');
      return;
    }
    if (!formData.title || !formData.contractor || !formData.community) {
      alert('Please fill out the project title, contractor, and community location.');
      return;
    }"""

if old_validate in text:
    text = text.replace(old_validate, new_validate, 1)
    print("  Added intervention_id validation")
else:
    print("  WARNING: validation block not found")

# ============================================================
# 5. Insert the intervention dropdown in the form
# ============================================================
# Find the first form field (Project Title) and insert before it
old_field_anchor = """        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4 text-slate-700">"""

new_form_open = """        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4 text-slate-700">
          {/* Approved Intervention Selector */}
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
"""

if old_field_anchor in text:
    text = text.replace(old_field_anchor, new_form_open, 1)
    print("  Inserted intervention dropdown at top of form")
else:
    print("  WARNING: form open anchor not found")

TARGET.write_text(text, encoding="utf-8")
print()
print(f"Patched {TARGET.name}")