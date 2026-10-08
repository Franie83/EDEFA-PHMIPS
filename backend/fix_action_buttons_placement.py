"""
Move the Edit/Delete buttons outside the Completed-only conditional block
so they render on every card.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

BROKEN = """                {item.status === 'Completed' && (
                  <button
                    onClick={() => onUpdateAction(item.id, { status: 'Verified', verified_by: 'Engr. Director Audits' })}
                    className="px-3 py-1 rounded text-xs font-semibold bg-blue-700 hover:bg-blue-800 text-white"
                  >
                    Verify & Close
                  </button>

                <button
                  onClick={() => openEditModal(item)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 inline-flex items-center gap-1.5"
                  title="Edit this action"
                >
                  <Pencil className="w-3.5 h-3.5" />
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteAction(item)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-100 hover:bg-rose-200 text-rose-800 inline-flex items-center gap-1.5"
                  title="Delete this action"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Delete
                </button>
                )}
              </div>"""

FIXED = """                {item.status === 'Completed' && (
                  <button
                    onClick={() => onUpdateAction(item.id, { status: 'Verified', verified_by: 'Engr. Director Audits' })}
                    className="px-3 py-1 rounded text-xs font-semibold bg-blue-700 hover:bg-blue-800 text-white"
                  >
                    Verify & Close
                  </button>
                )}
                <button
                  onClick={() => openEditModal(item)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 inline-flex items-center gap-1.5"
                  title="Edit this action"
                >
                  <Pencil className="w-3.5 h-3.5" />
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteAction(item)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-100 hover:bg-rose-200 text-rose-800 inline-flex items-center gap-1.5"
                  title="Delete this action"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Delete
                </button>
              </div>"""

if FIXED in text:
    print("Already fixed — skipping.")
    raise SystemExit(0)

if BROKEN not in text:
    raise SystemExit(
        "Broken block not found in exact form. Paste the current lines 465–510 and I'll adapt."
    )

text = text.replace(BROKEN, FIXED, 1)
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Moved Edit + Delete buttons outside the Completed-only conditional")