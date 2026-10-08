"""
Repair the mangled header block in HazardDetailModal.tsx.
The previous migration inserted the Edit/Delete buttons but left the original
close-button block truncated. This script replaces the entire broken section
with a correctly balanced header.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "hazards" / "HazardDetailModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

# The exact broken block currently in the file:
BROKEN = """          <div className="flex items-center space-x-1.5">
            {userCanEdit && onEdit && (
              <button
                onClick={() => onEdit(hazard)}
                title="Edit this hazard (Super Admin / Executive only)"
                className="p-1.5 rounded-lg bg-emerald-800/60 hover:bg-emerald-700 text-emerald-100 transition-colors inline-flex items-center space-x-1"
              >
                <Pencil className="w-4 h-4" />
                <span className="hidden sm:inline text-[11px] font-semibold">Edit</span>
              </button>
            )}
            {userCanDelete && onDelete && (
              <button
                onClick={handleDeleteClick}
                title="Delete this hazard (Super Admin / Executive only)"
                className="p-1.5 rounded-lg bg-rose-900/60 hover:bg-rose-800 text-rose-100 transition-colors inline-flex items-center space-x-1"
              >
                <Trash2 className="w-4 h-4" />
                <span className="hidden sm:inline text-[11px] font-semibold">Delete</span>
              </button>
            )}
            <button
              onClick={onClose}
            className="p-1 rounded-md text-emerald-300 hover:text-white hover:bg-emerald-800 transition-colors"
          >"""

FIXED = """          <div className="flex items-center space-x-1.5">
            {userCanEdit && onEdit && (
              <button
                onClick={() => onEdit(hazard)}
                title="Edit this hazard (Super Admin / Executive only)"
                className="p-1.5 rounded-lg bg-emerald-800/60 hover:bg-emerald-700 text-emerald-100 transition-colors inline-flex items-center space-x-1"
              >
                <Pencil className="w-4 h-4" />
                <span className="hidden sm:inline text-[11px] font-semibold">Edit</span>
              </button>
            )}
            {userCanDelete && onDelete && (
              <button
                onClick={handleDeleteClick}
                title="Delete this hazard (Super Admin / Executive only)"
                className="p-1.5 rounded-lg bg-rose-900/60 hover:bg-rose-800 text-rose-100 transition-colors inline-flex items-center space-x-1"
              >
                <Trash2 className="w-4 h-4" />
                <span className="hidden sm:inline text-[11px] font-semibold">Delete</span>
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1 rounded-md text-emerald-300 hover:text-white hover:bg-emerald-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>"""

if FIXED in text:
    print("Already fixed — skipping.")
    raise SystemExit(0)

if BROKEN not in text:
    raise SystemExit(
        "Broken block not found in expected form. Paste the current "
        "header section so we can adapt the fix."
    )

text = text.replace(BROKEN, FIXED, 1)
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  - Closed the close button's <button> tag")
print("  - Added <X className=\"w-4 h-4\" /> inside the button")
print("  - Closed the flex wrapper <div>")
print("  - Closed the header <div>")