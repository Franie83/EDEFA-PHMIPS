"""
Only show "Log Inspection Visit" for Active or Delayed projects.
Show an informational hint when it's hidden.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "projects" / "ProjectDetailModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "canLogVisit" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# 1. Add the canLogVisit computation next to canApproveProject
anchor = "typeof onRejectProject === 'function';"
if anchor in text:
    addition = anchor + """

  const canLogVisit =
    project.status === 'Active' ||
    project.status === 'Delayed';"""
    text = text.replace(anchor, addition, 1)
    print("  Added canLogVisit computation")
else:
    # Fallback
    anchor = "typeof onApproveProject === 'function';"
    if anchor in text:
        addition = anchor + """

  const canLogVisit =
    project.status === 'Active' ||
    project.status === 'Delayed';"""
        text = text.replace(anchor, addition, 1)
        print("  Added canLogVisit (via alt anchor)")
    else:
        raise SystemExit("Could not find canApproveProject anchor")

# 2. Find the "Log Inspection Visit" button and wrap it in the canLogVisit condition
# The button text is "Log Inspection Visit"
idx = text.find("Log Inspection Visit")
if idx == -1:
    raise SystemExit("Could not find 'Log Inspection Visit' button")

# Find the enclosing <button ...>
# Walk backwards from idx to find '<button'
button_start = text.rfind("<button", 0, idx)
if button_start == -1:
    raise SystemExit("Could not find <button for Log Inspection Visit")

# Find the closing </button>
button_end = text.find("</button>", idx)
if button_end == -1:
    raise SystemExit("Could not find </button> for Log Inspection Visit")
button_end += len("</button>")

# The full button block
button_block = text[button_start:button_end]

# Check if it's already wrapped
before = text[max(0, button_start - 100):button_start]
if "canLogVisit" in before:
    print("  Already wrapped — skipping")
else:
    # Wrap the button with {canLogVisit && (...)}
    wrapped = "{canLogVisit && (\n              " + button_block + "\n            )}"

    # Add the informational hint after the wrapped button
    hint = """

            {!canLogVisit && (
              <div className="text-[11px] text-slate-500 italic px-2 py-1 rounded bg-slate-50 border border-slate-200 inline-block">
                ℹ️ Field inspection visits can only be logged on <strong>Active</strong> or <strong>Delayed</strong> projects.
                This project is currently <strong>{project.status}</strong>.
              </div>
            )}"""

    replacement = wrapped + hint
    text = text[:button_start] + replacement + text[button_end:]
    print("  Wrapped Log Inspection Visit in canLogVisit + added hint")

TARGET.write_text(text, encoding="utf-8")
print(f"\nPatched {TARGET.name}")