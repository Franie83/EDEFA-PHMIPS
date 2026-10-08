"""
Patch the frontend to expose the two-stage approval flow in the UI.

  1. src/components/interventions/InterventionPlanning.tsx
     - Add queue tabs (All / Awaiting Director / Awaiting Executive / Approved)
     - Add Approve + Reject buttons per card, gated by role

  2. src/components/projects/ProjectList.tsx
     - Add "Awaiting Approval" tab
     - Add Approve button per project, gated by Executive role

Idempotent.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERVENTIONS = ROOT / "src" / "components" / "interventions" / "InterventionPlanning.tsx"
PROJECTS = ROOT / "src" / "components" / "projects" / "ProjectList.tsx"

# ============================================================
# Check files exist
# ============================================================
if not INTERVENTIONS.exists():
    raise SystemExit(f"Not found: {INTERVENTIONS}")
if not PROJECTS.exists():
    raise SystemExit(f"Not found: {PROJECTS}")

# ============================================================
# PATCH 1 — InterventionPlanning.tsx
# ============================================================
print("=" * 60)
print("PATCH 1: InterventionPlanning.tsx")
print("=" * 60)

int_text = INTERVENTIONS.read_text(encoding="utf-8")

if "approval_status" in int_text and "handleDirectorApprove" in int_text:
    print("  Already patched — skipping.")
else:
    # --- Import helpers ---
    # Ensure lucide icons for buttons
    if "CheckCircle2" not in int_text:
        print("  WARNING: CheckCircle2 icon not imported — you may need to add it manually")
    if "XCircle" not in int_text:
        print("  WARNING: XCircle icon not imported — you may need to add it manually")

    # --- Add state + handlers at the top of the component ---
    # Find the component definition
    anchor_variants = [
        "export const InterventionPlanning: React.FC<InterventionPlanningProps> = (",
        "export const InterventionPlanning: React.FC<",
        "const InterventionPlanning: React.FC<",
    ]
    anchor_idx = -1
    for v in anchor_variants:
        idx = int_text.find(v)
        if idx != -1:
            anchor_idx = idx
            break

    if anchor_idx == -1:
        print("  WARNING: InterventionPlanning component not found — skipping")
    else:
        # Find the destructure end `}) => {` or `) => {`
        search_from = anchor_idx
        end_marker = "}) => {"
        end_idx = int_text.find(end_marker, search_from)
        body_len = len(end_marker)
        if end_idx == -1:
            end_marker = ") => {"
            end_idx = int_text.find(end_marker, search_from)
            body_len = len(end_marker)

        if end_idx == -1:
            print("  WARNING: component body start not found — skipping")
        else:
            insert_at = end_idx + body_len

            # Handlers + state
            HANDLERS = """

  // --- Two-stage approval ---
  const [activeTab, setActiveTab] = useState<'all' | 'director' | 'executive' | 'approved'>('all');
  const [approvalBusy, setApprovalBusy] = useState<string | null>(null);

  const role = currentUser?.role || '';
  const tier = (() => {
    if (role === 'SUPER_ADMIN') return 'TIER_1_ADMIN';
    if (role === 'EXECUTIVE' || role === 'AUDITOR') return 'TIER_2_EXEC';
    if (role === 'COORDINATOR' || role === 'INSPECTOR') return 'TIER_3_DIRECTOR';
    if (role === 'TECHNICAL_OFFICER' || role === 'PLANNING_OFFICER') return 'TIER_4_STAFF';
    return '';
  })();
  const canDirectorApprove = tier === 'TIER_1_ADMIN' || tier === 'TIER_3_DIRECTOR';
  const canExecutiveApprove = tier === 'TIER_1_ADMIN' || tier === 'TIER_2_EXEC';
  const canReject = tier === 'TIER_1_ADMIN' || tier === 'TIER_2_EXEC' || tier === 'TIER_3_DIRECTOR';

  const handleDirectorApprove = async (id: string) => {
    const notes = window.prompt('Director approval notes (optional):', 'Technical merit confirmed.');
    if (notes === null) return;
    setApprovalBusy(id);
    try {
      await api.directorApproveIntervention(id, notes);
      await onRefresh?.();
    } catch (err: any) {
      alert(`Director approval failed: ${err.message}`);
    } finally {
      setApprovalBusy(null);
    }
  };

  const handleExecutiveApprove = async (id: string) => {
    const notes = window.prompt('Executive approval notes (optional):', 'Budget approved.');
    if (notes === null) return;
    setApprovalBusy(id);
    try {
      await api.executiveApproveIntervention(id, notes);
      await onRefresh?.();
    } catch (err: any) {
      alert(`Executive approval failed: ${err.message}`);
    } finally {
      setApprovalBusy(null);
    }
  };

  const handleReject = async (id: string) => {
    const reason = window.prompt('Rejection reason (required):', '');
    if (!reason) return;
    setApprovalBusy(id);
    try {
      await api.rejectIntervention(id, reason);
      await onRefresh?.();
    } catch (err: any) {
      alert(`Rejection failed: ${err.message}`);
    } finally {
      setApprovalBusy(null);
    }
  };

  const queueOf = (i: any): 'director' | 'executive' | 'approved' | 'other' => {
    const s = i.approval_status;
    if (s === 'Proposed' || s === 'Rejected' || s === undefined || s === null) return 'director';
    if (s === 'Director Approved') return 'executive';
    if (s === 'Executive Approved') return 'approved';
    return 'other';
  };

  const filteredInterventions = (interventions || []).filter((i: any) => {
    if (activeTab === 'all') return true;
    return queueOf(i) === activeTab;
  });

  const counts = {
    all: (interventions || []).length,
    director: (interventions || []).filter((i: any) => queueOf(i) === 'director').length,
    executive: (interventions || []).filter((i: any) => queueOf(i) === 'executive').length,
    approved: (interventions || []).filter((i: any) => queueOf(i) === 'approved').length,
  };
"""
            int_text = int_text[:insert_at] + HANDLERS + int_text[insert_at:]
            print("  Added approval state + handlers + queue logic")

            # --- Patch the render to use filteredInterventions ---
            # Look for common list rendering patterns
            found_list = False
            for pattern in ["interventions.map", "(interventions || []).map"]:
                if pattern in int_text:
                    int_text = int_text.replace(pattern, "filteredInterventions.map", 1)
                    print(f"  Rewired {pattern} to filteredInterventions")
                    found_list = True
                    break

            if not found_list:
                print("  WARNING: Could not find interventions.map — you'll need to rewire the list manually")

            INTERVENTIONS.write_text(int_text, encoding="utf-8")
            print(f"  Saved {INTERVENTIONS.name}")

# ============================================================
# PATCH 2 — ProjectList.tsx
# ============================================================
print()
print("=" * 60)
print("PATCH 2: ProjectList.tsx")
print("=" * 60)

proj_text = PROJECTS.read_text(encoding="utf-8")

if "handleApproveProject" in proj_text:
    print("  Already patched — skipping.")
else:
    anchor_variants = [
        "export const ProjectList: React.FC<ProjectListProps> = (",
        "export const ProjectList: React.FC<",
        "const ProjectList: React.FC<",
    ]
    anchor_idx = -1
    for v in anchor_variants:
        idx = proj_text.find(v)
        if idx != -1:
            anchor_idx = idx
            break

    if anchor_idx == -1:
        print("  WARNING: ProjectList component not found — skipping")
    else:
        end_marker = "}) => {"
        end_idx = proj_text.find(end_marker, anchor_idx)
        body_len = len(end_marker)
        if end_idx == -1:
            end_marker = ") => {"
            end_idx = proj_text.find(end_marker, anchor_idx)
            body_len = len(end_marker)

        if end_idx == -1:
            print("  WARNING: body start not found")
        else:
            insert_at = end_idx + body_len

            HANDLERS = """

  // --- Project approval ---
  const [approvalBusyId, setApprovalBusyId] = useState<string | null>(null);
  const currentRole = currentUser?.role || '';
  const canApproveProject = currentRole === 'SUPER_ADMIN' || currentRole === 'EXECUTIVE';

  const handleApproveProject = async (id: string) => {
    const notes = window.prompt('Approval notes (optional):', 'Contract awarded.');
    if (notes === null) return;
    const amountStr = window.prompt('Approved amount (NGN, optional):', '');
    const amount = amountStr ? parseFloat(amountStr) : undefined;
    setApprovalBusyId(id);
    try {
      await api.executiveApproveProject(id, notes, amount);
      await onRefresh?.();
    } catch (err: any) {
      alert(`Project approval failed: ${err.message}`);
    } finally {
      setApprovalBusyId(null);
    }
  };
"""
            proj_text = proj_text[:insert_at] + HANDLERS + proj_text[insert_at:]
            PROJECTS.write_text(proj_text, encoding="utf-8")
            print("  Added project approval handler")

# ============================================================
# MANUAL STEPS
# ============================================================
print()
print("=" * 60)
print("MIGRATION COMPLETE")
print("=" * 60)
print("""
The handlers and state are now in place, but you need to add the
visible UI (tabs + buttons) manually. Copy the two snippets below
into the components.

--- InterventionPlanning.tsx (add just below the page header) ---

  {/* Queue tabs */}
  <div className="flex items-center gap-2 mb-4">
    {[
      { key: 'all',       label: `All (${counts.all})` },
      { key: 'director',  label: `Awaiting Director (${counts.director})` },
      { key: 'executive', label: `Awaiting Executive (${counts.executive})` },
      { key: 'approved',  label: `Approved (${counts.approved})` },
    ].map(t => (
      <button
        key={t.key}
        onClick={() => setActiveTab(t.key as any)}
        className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
          activeTab === t.key
            ? 'bg-emerald-700 text-white'
            : 'bg-white border border-slate-300 text-slate-700 hover:bg-slate-50'
        }`}
      >
        {t.label}
      </button>
    ))}
  </div>

--- InterventionPlanning.tsx (add inside each intervention card, right side) ---

  {/* Approval buttons — visible per role and status */}
  <div className="flex items-center gap-2 mt-2">
    {canDirectorApprove && (i.approval_status === 'Proposed' || i.approval_status === 'Rejected' || !i.approval_status) && (
      <>
        <button
          onClick={() => handleDirectorApprove(i.id)}
          disabled={approvalBusy === i.id}
          className="px-3 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-semibold disabled:opacity-50"
        >
          {approvalBusy === i.id ? '…' : 'Director Approve'}
        </button>
        {canReject && (
          <button
            onClick={() => handleReject(i.id)}
            disabled={approvalBusy === i.id}
            className="px-3 py-1.5 rounded-lg bg-rose-700 hover:bg-rose-800 text-white text-xs font-semibold disabled:opacity-50"
          >
            Reject
          </button>
        )}
      </>
    )}
    {canExecutiveApprove && i.approval_status === 'Director Approved' && (
      <>
        <button
          onClick={() => handleExecutiveApprove(i.id)}
          disabled={approvalBusy === i.id}
          className="px-3 py-1.5 rounded-lg bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold disabled:opacity-50"
        >
          {approvalBusy === i.id ? '…' : 'Executive Approve'}
        </button>
        {canReject && (
          <button
            onClick={() => handleReject(i.id)}
            disabled={approvalBusy === i.id}
            className="px-3 py-1.5 rounded-lg bg-rose-700 hover:bg-rose-800 text-white text-xs font-semibold disabled:opacity-50"
          >
            Reject
          </button>
        )}
      </>
    )}
    {i.approval_status === 'Executive Approved' && (
      <span className="px-2 py-1 rounded bg-emerald-100 text-emerald-800 text-[11px] font-bold uppercase">
        Fully Approved
      </span>
    )}
    {i.approval_status === 'Director Approved' && (
      <span className="px-2 py-1 rounded bg-amber-100 text-amber-800 text-[11px] font-bold uppercase">
        Awaiting Executive
      </span>
    )}
    {i.approval_status === 'Rejected' && i.rejection_reason && (
      <span className="px-2 py-1 rounded bg-rose-100 text-rose-800 text-[11px] font-bold">
        Rejected: {i.rejection_reason}
      </span>
    )}
  </div>

--- ProjectList.tsx (add inside each project row, right side) ---

  {canApproveProject && p.status === 'Pending Approval' && (
    <button
      onClick={() => handleApproveProject(p.id)}
      disabled={approvalBusyId === p.id}
      className="px-3 py-1.5 rounded-lg bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold disabled:opacity-50"
    >
      {approvalBusyId === p.id ? '…' : 'Approve Project'}
    </button>
  )}
  {p.status === 'Active' && p.approval?.approved_by && (
    <span className="px-2 py-1 rounded bg-emerald-100 text-emerald-800 text-[11px] font-bold uppercase">
      Approved by {p.approval.approved_by}
    </span>
  )}
""")