"""
Add "Approve Project" button to ProjectDetailModal.tsx and wire it
through App.tsx.

Visible only when:
  - Current user role is EXECUTIVE, SUPER_ADMIN, or AUDITOR (read-only)
  - Project status === 'Pending Approval'

T1/T3 can create; T1/T2 can approve.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DETAIL = ROOT / "src" / "components" / "projects" / "ProjectDetailModal.tsx"
APP = ROOT / "src" / "App.tsx"

if not DETAIL.exists():
    raise SystemExit(f"Not found: {DETAIL}")
if not APP.exists():
    raise SystemExit(f"Not found: {APP}")

# ============================================================
# 1. PATCH ProjectDetailModal.tsx
# ============================================================
print("=" * 60)
print("PATCH 1: ProjectDetailModal.tsx")
print("=" * 60)

detail_text = DETAIL.read_text(encoding="utf-8")

if "onApproveProject" in detail_text:
    print("  Already patched — skipping.")
else:
    # 1a — add CheckCircle2 and XCircle icons to imports if not present
    icons_to_check = ["CheckCircle2", "XCircle"]
    for icon in icons_to_check:
        if icon not in detail_text.split("from 'lucide-react'")[0]:
            # Add it inside the lucide-react import block
            m = re.search(r"import\s*\{([^}]+)\}\s*from\s*'lucide-react'", detail_text)
            if m:
                existing = m.group(1).strip()
                if existing.endswith(","):
                    new_block = "import {\n  " + existing + "\n  " + icon + "\n} from 'lucide-react'"
                else:
                    new_block = "import {\n  " + existing + ",\n  " + icon + "\n} from 'lucide-react'"
                detail_text = detail_text[:m.start()] + new_block + detail_text[m.end():]
                print(f"  Added {icon} icon")
                break

    # 1b — extend prop interface
    old_props = re.search(r"interface ProjectDetailModalProps\s*\{([^}]*)\}", detail_text)
    if old_props:
        props_body = old_props.group(1)
        if "onApproveProject" not in props_body:
            new_props = old_props.group(0).rstrip("}") + "  onApproveProject?: (project: Project) => void;\n  currentUserRole?: string;\n}"
            detail_text = detail_text[:old_props.start()] + new_props + detail_text[old_props.end():]
            print("  Extended prop interface")
    else:
        print("  WARNING: could not find ProjectDetailModalProps")

    # 1c — extend destructure
    m = re.search(r"export\s+const\s+ProjectDetailModal[^=]*=\s*\(\s*\{([^}]*)\}", detail_text)
    if m:
        destructure = m.group(1)
        if "onApproveProject" not in destructure:
            new_destructure = destructure.rstrip().rstrip(",") + ",\n  onApproveProject,\n  currentUserRole"
            detail_text = detail_text[:m.start(1)] + new_destructure + detail_text[m.end(1):]
            print("  Extended destructure")
    else:
        print("  WARNING: could not find ProjectDetailModal destructure")

    # 1d — compute canApprove inside the component body
    # Find the line "if (!project) return null;" and insert canApprove before it
    anchor = "if (!project) return null;"
    if anchor in detail_text:
        can_approve = """const canApproveProject =
    (currentUserRole === 'SUPER_ADMIN' || currentUserRole === 'EXECUTIVE') &&
    project.status === 'Pending Approval' &&
    typeof onApproveProject === 'function';

  """
        detail_text = detail_text.replace(anchor, can_approve + anchor, 1)
        print("  Added canApproveProject computation")

    # 1e — add Approve button near the footer (before "Close")
    # We look for the close button pattern
    close_btn = re.search(
        r"<button\s+onClick=\{onClose\}\s+className=\"[^\"]*\"[^>]*>\s*Close\s*</button>",
        detail_text,
    )
    if not close_btn:
        # looser pattern: any onClick={onClose} with "Close" text after
        close_btn = re.search(r"<button[^>]*onClick=\{onClose\}[^>]*>\s*Close\s*</button>", detail_text)

    if close_btn:
        approve_jsx = """{canApproveProject && (
              <button
                onClick={() => onApproveProject?.(project)}
                className="px-4 py-1.5 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center gap-1.5"
              >
                <CheckCircle2 className="w-4 h-4" />
                Approve Project
              </button>
            )}
            """
        detail_text = detail_text[:close_btn.start()] + approve_jsx + detail_text[close_btn.start():]
        print("  Added Approve Project button")
    else:
        print("  WARNING: could not find Close button to anchor the Approve button")

    # 1f — show approval info if already approved
    anchor2 = "if (!project) return null;"
    if anchor2 in detail_text and "Project Approval" not in detail_text:
        # Insert an approval banner in the JSX - find the top-level container
        # We'll add a small block right after the header
        # Look for a comment like "{/* Header */}" or similar marker
        header_markers = ["{/* Header */}", "{/* Header*/}", "Project Detail"]
        inserted = False
        for marker in header_markers:
            idx = detail_text.find(marker)
            if idx != -1:
                # Look for the closing of the header block — insert approval info after
                # we just find the first "</div>" after the marker
                end = detail_text.find("</div>", idx)
                if end != -1:
                    insert_point = end + len("</div>")
                    approval_info = """

          {project.status === 'Active' && (project as any).approval?.approved_by && (
            <div className="mx-6 mt-3 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs">
              <strong className="text-emerald-900">✓ Approved</strong> by{' '}
              <strong>{(project as any).approval.approved_by}</strong> on{' '}
              {new Date((project as any).approval.approved_at).toLocaleString()}
              {(project as any).approval.approved_amount_ngn && (
                <> — Approved amount: ₦{((project as any).approval.approved_amount_ngn / 1e6).toFixed(1)}M</>
              )}
            </div>
          )}"""
                    detail_text = detail_text[:insert_point] + approval_info + detail_text[insert_point:]
                    inserted = True
                    print("  Added approval info banner")
                    break
        if not inserted:
            print("  WARNING: could not insert approval info banner")

    DETAIL.write_text(detail_text, encoding="utf-8")
    print(f"  Saved {DETAIL.name}")

# ============================================================
# 2. PATCH App.tsx
# ============================================================
print()
print("=" * 60)
print("PATCH 2: App.tsx")
print("=" * 60)

app_text = APP.read_text(encoding="utf-8")

# 2a — add handler if not present
if "handleApproveProject" not in app_text:
    anchor = "const handleEditHazard = async"
    if anchor in app_text:
        handler = """const handleApproveProject = async (project: Project) => {
    const notes = window.prompt('Approval notes (optional):', 'Approved.');
    if (notes === null) return;
    const amountStr = window.prompt(
      'Approved amount (NGN, optional — press Cancel to use the registered amount):',
      String(project.approved_amount_ngn || '')
    );
    const amount = amountStr ? parseFloat(amountStr) : undefined;
    try {
      await api.executiveApproveProject(project.id, notes, amount);
      await loadData();
      setSelectedProject(null);
    } catch (err: any) {
      alert(`Project approval failed: ${err.message}`);
    }
  };

  """
        app_text = app_text.replace(anchor, handler + anchor, 1)
        print("  Added handleApproveProject handler")
    else:
        print("  WARNING: could not find anchor to insert handler")

# 2b — pass onApproveProject and currentUserRole to ProjectDetailModal
old_render = "<ProjectDetailModal"
idx = app_text.find(old_render)
if idx == -1:
    print("  WARNING: ProjectDetailModal render not found in App.tsx")
else:
    # Find the closing `/>` of that JSX
    end_idx = app_text.find("/>", idx)
    if end_idx == -1:
        print("  WARNING: closing /> of ProjectDetailModal not found")
    else:
        block = app_text[idx:end_idx]
        if "onApproveProject" not in block:
            # Insert props before `/>`
            insert_props = """
        onApproveProject={handleApproveProject}
        currentUserRole={currentUser?.role}"""
            app_text = app_text[:end_idx] + insert_props + "\n      " + app_text[end_idx:]
            print("  Wired onApproveProject + currentUserRole into ProjectDetailModal")

APP.write_text(app_text, encoding="utf-8")
print(f"  Saved {APP.name}")

print()
print("=" * 60)
print("COMPLETE")
print("=" * 60)
print("""
Next:
  1. npx tsc --noEmit
  2. .\\restart-backend.ps1
  3. Hard refresh browser (Ctrl+Shift+R)
  4. Log in as executive
  5. Open PRJ-2026-007
  6. Should see "Approve Project" button
  7. Click → prompts for notes + amount → status becomes Active
""")