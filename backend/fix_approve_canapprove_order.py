"""
Move the canApproveProject computation to AFTER the null check.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "projects" / "ProjectDetailModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

BROKEN = """const canApproveProject =
    (currentUserRole === 'SUPER_ADMIN' || currentUserRole === 'EXECUTIVE') &&
    project.status === 'Pending Approval' &&
    typeof onApproveProject === 'function';

  if (!project) return null;"""

FIXED = """if (!project) return null;

  const canApproveProject =
    (currentUserRole === 'SUPER_ADMIN' || currentUserRole === 'EXECUTIVE') &&
    project.status === 'Pending Approval' &&
    typeof onApproveProject === 'function';"""

if FIXED in text:
    print("Already fixed — skipping.")
    raise SystemExit(0)

if BROKEN not in text:
    # try looser match: find canApproveProject block and null check nearby
    print("Exact block not found — trying looser match")
    # Find where canApproveProject is defined
    idx = text.find("const canApproveProject")
    if idx == -1:
        raise SystemExit("Could not find canApproveProject definition")
    # Find the null check
    null_idx = text.find("if (!project) return null;")
    if null_idx == -1:
        raise SystemExit("Could not find null check")
    # Find end of canApproveProject block (ends with `;` after the function check)
    end_idx = text.find(";", text.find("typeof onApproveProject", idx))
    if end_idx == -1:
        raise SystemExit("Could not find end of canApproveProject block")
    end_idx += 1  # include the semicolon
    # Extract the block
    can_block = text[idx:end_idx]
    # Remove it from its current position
    text = text[:idx] + text[end_idx:]
    # Find the null check again (position shifted)
    null_idx = text.find("if (!project) return null;")
    insert_at = null_idx + len("if (!project) return null;")
    text = text[:insert_at] + "\n\n  " + can_block + text[insert_at:]
    print("Moved canApproveProject below the null check")
else:
    text = text.replace(BROKEN, FIXED, 1)
    print("Moved canApproveProject below the null check (exact match)")

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")