"""
Add "Reject Project" with comment + auto-reset on edit.

Backend:
  - POST /api/projects/:id/reject  (T1 + T2 only, requires comment)

Frontend:
  - api.rejectProject()
  - ProjectDetailModal shows "✗ Reject" button when status is Pending Approval
  - Rejection prompts for a required comment
  - If a rejected project is edited, its status auto-resets to Pending Approval
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
APP_PY = ROOT / "backend" / "app.py"
API_TS = ROOT / "src" / "services" / "api.ts"
MODAL = ROOT / "src" / "components" / "projects" / "ProjectDetailModal.tsx"
APP = ROOT / "src" / "App.tsx"

for f in [APP_PY, API_TS, MODAL, APP]:
    if not f.exists():
        raise SystemExit(f"Not found: {f}")

# ============================================================
# 1. Backend — reject endpoint + auto-reset on edit
# ============================================================
print("=" * 60)
print("PATCH 1: backend/app.py")
print("=" * 60)

text = APP_PY.read_text(encoding="utf-8")

if "/api/projects/<id>/reject" in text:
    print("  Reject endpoint already present.")
else:
    anchor = '''@app.post("/api/projects/<id>/executive-approve")'''
    new_endpoint = '''@app.post("/api/projects/<id>/reject")
@require_exec_approve()
def exec_reject_project(id):
    """Executive rejects a project with a required comment.
    Status becomes 'Rejected'. On next edit, it auto-resets to 'Pending Approval'."""
    r = one("projects", id)
    if not r:
        return jsonify({"error": "Project not found"}), 404
    d = request.get_json(silent=True) or {}
    reason = (d.get("rejection_reason") or "").strip()
    if not reason:
        return jsonify({"error": "rejection_reason is required"}), 400
    p = dict(r.data)
    if p.get("status") != "Pending Approval":
        return jsonify({
            "error": "Only projects in Pending Approval status can be rejected",
            "current_status": p.get("status"),
        }), 400
    u = user()
    p["status"] = "Rejected"
    p["rejection"] = {
        "rejected_by": u.get("name"),
        "rejected_by_id": u.get("id"),
        "rejected_at": now(),
        "rejection_reason": reason,
    }
    # Remove any prior approval so the record is clean
    p.pop("approval", None)
    r.data = p
    audit("EXECUTIVE_REJECT_PROJECT", "PROJECT", id, old=None, new=p,
          details=f"Rejected by {u.get('name')}: {reason}")
    notify(f"Project {id} rejected",
           f"{id} was rejected by Executive {u.get('name')}: {reason}. "
           f"Please revise and resubmit.",
           "PROJECT", f"/projects/{id}", priority="HIGH")
    db.session.commit()
    return jsonify({"success": True, "project": p})


@app.post("/api/projects/<id>/executive-approve")'''

    if anchor not in text:
        raise SystemExit("executive-approve anchor not found in app.py")
    text = text.replace(anchor, new_endpoint, 1)
    print("  Added POST /api/projects/<id>/reject")

# Auto-reset status on edit
if "EDIT_PROJECT" in text and "if p.get(\"status\") == \"Rejected\"" not in text:
    # Modify project_update to reset status
    old_update = '''@app.put("/api/projects/<id>")
@require_edit()
def project_update(id):
 r=one("projects",id)
 if not r:return jsonify({"error":"Project not found"}),404
 d=request.get_json(silent=True) or {};old=dict(r.data)
 immutable={"id","created_at"}
 new={**old,**{k:v for k,v in d.items() if k not in immutable}}
 r.data=new
 audit("EDIT_PROJECT","PROJECT",id,old=old,new=new,details=f"Edited project {id} — {new.get('title','')}")
 db.session.commit();return jsonify(new)'''

    new_update = '''@app.put("/api/projects/<id>")
@require_edit()
def project_update(id):
 r=one("projects",id)
 if not r:return jsonify({"error":"Project not found"}),404
 d=request.get_json(silent=True) or {};old=dict(r.data)
 immutable={"id","created_at"}
 new={**old,**{k:v for k,v in d.items() if k not in immutable}}
 # If the project was rejected and is being edited, reset to Pending Approval
 if old.get("status") == "Rejected":
     new["status"] = "Pending Approval"
     new.pop("rejection", None)
 r.data=new
 audit("EDIT_PROJECT","PROJECT",id,old=old,new=new,details=f"Edited project {id} — {new.get('title','')}")
 db.session.commit();return jsonify(new)'''

    if old_update in text:
        text = text.replace(old_update, new_update, 1)
        print("  Auto-reset Rejected → Pending Approval on edit")
    else:
        print("  WARNING: could not find project_update in expected form")

APP_PY.write_text(text, encoding="utf-8")

# ============================================================
# 2. api.ts — rejectProject
# ============================================================
print()
print("=" * 60)
print("PATCH 2: src/services/api.ts")
print("=" * 60)

text = API_TS.read_text(encoding="utf-8")

if "rejectProject:" in text:
    print("  rejectProject already present.")
else:
    anchor = "  executiveApproveProject: (id: string, notes?: string, approved_amount_ngn?: number) =>"
    new_method = """  rejectProject: (id: string, rejection_reason: string) =>
    request<{ success: boolean; project: Project }>(`/projects/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ rejection_reason })
    }),
  executiveApproveProject: (id: string, notes?: string, approved_amount_ngn?: number) =>"""

    if anchor not in text:
        raise SystemExit("executiveApproveProject anchor not found in api.ts")
    text = text.replace(anchor, new_method, 1)
    API_TS.write_text(text, encoding="utf-8")
    print("  Added api.rejectProject")

# ============================================================
# 3. ProjectDetailModal.tsx — Reject button
# ============================================================
print()
print("=" * 60)
print("PATCH 3: ProjectDetailModal.tsx")
print("=" * 60)

text = MODAL.read_text(encoding="utf-8")

if "onRejectProject" in text:
    print("  Already patched.")
else:
    # 3a — add XCircle icon if missing
    if "XCircle" not in text.split("from 'lucide-react'")[0]:
        m = re.search(r"import\s*\{([^}]+)\}\s*from\s*'lucide-react'", text)
        if m:
            existing = m.group(1).strip().rstrip(",")
            new_import = "import {\n  " + existing + ",\n  XCircle\n} from 'lucide-react'"
            text = text[:m.start()] + new_import + text[m.end():]
            print("  Added XCircle icon")

    # 3b — extend prop interface
    m = re.search(r"interface ProjectDetailModalProps\s*\{([^}]*)\}", text)
    if m and "onRejectProject" not in m.group(1):
        new_props = m.group(0).rstrip("}") + "  onRejectProject?: (project: Project) => void;\n}"
        text = text[:m.start()] + new_props + text[m.end():]
        print("  Extended prop interface")

    # 3c — extend destructure
    m = re.search(r"export\s+const\s+ProjectDetailModal[^=]*=\s*\(\s*\{([^}]*)\}", text)
    if m and "onRejectProject" not in m.group(1):
        new_destr = m.group(1).rstrip().rstrip(",") + ",\n  onRejectProject"
        text = text[:m.start(1)] + new_destr + text[m.end(1):]
        print("  Extended destructure")

    # 3d — add canRejectProject next to canApproveProject
    if "const canRejectProject" not in text:
        anchor = "typeof onApproveProject === 'function';"
        if anchor in text:
            new_can = anchor + """

  const canRejectProject =
    (currentUserRole === 'SUPER_ADMIN' || currentUserRole === 'EXECUTIVE') &&
    project.status === 'Pending Approval' &&
    typeof onRejectProject === 'function';"""
            text = text.replace(anchor, new_can, 1)
            print("  Added canRejectProject")

    # 3e — insert Reject button before Approve button
    approve_btn = re.search(r"\{canApproveProject && \([\s\S]*?\)\}", text)
    if approve_btn:
        reject_jsx = """{canRejectProject && (
              <button
                onClick={() => onRejectProject?.(project)}
                className="px-4 py-1.5 rounded-lg text-xs font-bold bg-rose-700 hover:bg-rose-800 text-white inline-flex items-center gap-1.5"
              >
                <XCircle className="w-4 h-4" />
                Reject
              </button>
            )}
            """
        text = text[:approve_btn.start()] + reject_jsx + text[approve_btn.start():]
        print("  Inserted Reject button")
    else:
        print("  WARNING: could not find Approve button to anchor Reject")

    # 3f — show rejection banner if rejected
    if "project.status === 'Rejected'" not in text:
        anchor2 = "if (!project) return null;"
        if anchor2 in text:
            # Insert banner in JSX after the top-level header
            header_marker = "Project Supervising Officer"  # heuristic: find a place near the top
            # Actually, insert near the "Approved by" banner if it exists, else near the beginning
            if "Approved</strong> by" in text:
                banner_anchor = "Approved</strong> by"
                idx = text.find(banner_anchor)
                # Find the end of the containing div
                end = text.find(")}", idx)
                if end != -1:
                    insert_at = end + 2
                    banner = """

          {project.status === 'Rejected' && (project as any).rejection?.rejection_reason && (
            <div className="mx-6 mt-3 p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs">
              <strong className="text-rose-900">✗ Rejected</strong> by{' '}
              <strong>{(project as any).rejection.rejected_by}</strong> on{' '}
              {new Date((project as any).rejection.rejected_at).toLocaleString()}
              <div className="mt-1 text-rose-800 italic">"{(project as any).rejection.rejection_reason}"</div>
              <div className="mt-1 text-[11px] text-slate-600">
                Edit this project to resubmit for approval.
              </div>
            </div>
          )}"""
                    text = text[:insert_at] + banner + text[insert_at:]
                    print("  Added rejection info banner")
            else:
                print("  WARNING: no approval banner anchor for rejection banner")

    MODAL.write_text(text, encoding="utf-8")

# ============================================================
# 4. App.tsx — handleRejectProject handler + wiring
# ============================================================
print()
print("=" * 60)
print("PATCH 4: src/App.tsx")
print("=" * 60)

text = APP.read_text(encoding="utf-8")

if "handleRejectProject" not in text:
    anchor = "const handleApproveProject = async"
    if anchor in text:
        handler = """const handleRejectProject = async (project: Project) => {
    const reason = window.prompt(
      'Rejection reason (required — the Director will see this):',
      ''
    );
    if (reason === null) return;
    if (!reason.trim()) {
      alert('A rejection reason is required.');
      return;
    }
    try {
      await api.rejectProject(project.id, reason);
      await loadData();
      setSelectedProject(null);
    } catch (err: any) {
      alert(`Project rejection failed: ${err.message}`);
    }
  };

  """
        text = text.replace(anchor, handler + anchor, 1)
        print("  Added handleRejectProject handler")

# Wire onRejectProject into ProjectDetailModal
idx = text.find("<ProjectDetailModal")
if idx != -1:
    end_idx = text.find("/>", idx)
    if end_idx != -1:
        block = text[idx:end_idx]
        if "onRejectProject" not in block:
            insert = "\n        onRejectProject={handleRejectProject}"
            text = text[:end_idx] + insert + text[end_idx:]
            print("  Wired onRejectProject into ProjectDetailModal")

APP.write_text(text, encoding="utf-8")

print()
print("=" * 60)
print("COMPLETE")
print("=" * 60)
print("""
Next:
  1. npx tsc --noEmit
  2. .\\restart-backend.ps1
  3. Hard refresh browser (Ctrl+Shift+R)
  4. Log in as executive, open PRJ-2026-007
  5. Should see [ ✓ Approve Project ] [ ✗ Reject ] [ Close ]

Test rejection flow:
  1. Click Reject → prompt for reason → enter "Contractor not licensed in Edo State"
  2. Status becomes Rejected, banner shows in modal
  3. Log in as inspector, edit the project, save → status resets to Pending Approval
  4. Log back as executive → approve → status Active
""")