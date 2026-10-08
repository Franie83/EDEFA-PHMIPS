"""
Add Edit and Delete buttons to each action card, plus an edit modal.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "isEditModalOpen" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# ============================================================
# 1. Extend lucide imports
# ============================================================
needed_icons = ["Pencil", "Trash2", "Save"]
m = re.search(r"import\s*\{([^}]+)\}\s*from\s*'lucide-react'", text)
if m:
    existing = m.group(1)
    missing = [ic for ic in needed_icons if ic not in existing]
    if missing:
        new_import = "import {\n  " + existing.strip().rstrip(",") + ",\n  " + ",\n  ".join(missing) + "\n} from 'lucide-react'"
        text = text[:m.start()] + new_import + text[m.end():]
        print(f"  Added icons: {missing}")

# ============================================================
# 2. Add edit state + handlers after isModalOpen
# ============================================================
anchor = "const [isModalOpen, setIsModalOpen] = useState(false);"
if anchor not in text:
    raise SystemExit("isModalOpen anchor not found")

new_state = anchor + """

  // Edit modal state
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingAction, setEditingAction] = useState<ActionItem | null>(null);
  const [editForm, setEditForm] = useState<Partial<ActionItem>>({});
  const [editBusy, setEditBusy] = useState(false);
  const [editError, setEditError] = useState('');"""

text = text.replace(anchor, new_state, 1)
print("  Added edit modal state")

# ============================================================
# 3. Add openEdit / handleEditSubmit / handleDelete handlers
# ============================================================
anchor2 = "const handleSubmit = async (e: React.FormEvent) => {"
if anchor2 not in text:
    raise SystemExit("handleSubmit anchor not found")

new_handlers = '''const openEditModal = (action: ActionItem) => {
    setEditingAction(action);
    setEditForm({ ...action });
    setEditError('');
    setIsEditModalOpen(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingAction) return;
    setEditError('');
    setEditBusy(true);
    try {
      await onUpdateAction(editingAction.id, editForm);
      setIsEditModalOpen(false);
      setEditingAction(null);
    } catch (err: any) {
      setEditError(err?.message || 'Failed to save changes');
    } finally {
      setEditBusy(false);
    }
  };

  const handleDeleteAction = async (action: ActionItem) => {
    const confirmed = window.confirm(
      `Delete action ${action.id}?\\n\\n"${action.title}"\\n\\nThis cannot be undone and will be recorded in the audit log.`
    );
    if (!confirmed) return;
    try {
      // Call the API directly
      const { api } = await import('../../services/api.ts');
      await api.deleteAction(action.id);
      window.location.reload();
    } catch (err: any) {
      alert(`Delete failed: ${err?.message || 'Unknown error'}`);
    }
  };

  const canDeleteAction = (action: ActionItem) => {
    // Only T1/T2 can delete; the backend enforces it, this is a UI hint
    return true; // we let the backend return 403 if not permitted
  };

  const handleSubmit = async (e: React.FormEvent) => {'''

text = text.replace(anchor2, new_handlers, 1)
print("  Added openEditModal, handleEditSubmit, handleDeleteAction")

# ============================================================
# 4. Insert Edit + Delete buttons next to the Mark Completed / Verify buttons
# ============================================================
# Find the existing action buttons area (the block that has Mark Completed / Verify & Close)
# It should end with "</div>" after those buttons
# Look for the pattern: "Mark Completed" button and its surrounding container

# Find the container div that has "Progress:" and the buttons
progress_idx = text.find("Progress:")
if progress_idx == -1:
    raise SystemExit("Could not find 'Progress:' in the card")

# Find the closing </div> of that row (the parent of the progress + buttons)
# Walk forward from progress_idx to find "</div>\n          </div>" or similar
# Simpler: find the closing of the row that contains the buttons
# The buttons Mark Completed / Verify & Close appear after this
mark_btn_idx = text.find("Mark Completed", progress_idx)
verify_btn_idx = text.find("Verify & Close", progress_idx)

# The end of the buttons row is the first </div> after the last button tag
last_btn = max(mark_btn_idx, verify_btn_idx)
if last_btn == -1:
    raise SystemExit("Could not find Mark Completed / Verify & Close buttons")

# Find the closing </div> after the last button
end_btn_block = text.find("</div>", last_btn)
if end_btn_block == -1:
    raise SystemExit("Could not find closing </div> after the buttons")

# Insert Edit + Delete buttons just BEFORE the closing </div>
# We insert them right after the last button's closing </button>, but before </div>
insert_at = text.rfind("</button>", 0, end_btn_block)
if insert_at == -1:
    raise SystemExit("Could not find </button> in the button block")
insert_at += len("</button>")

new_buttons = """

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
                </button>"""

text = text[:insert_at] + new_buttons + text[insert_at:]
print("  Inserted Edit + Delete buttons on each card")

TARGET.write_text(text, encoding="utf-8")
print(f"\nPatched {TARGET.name}")
print()
print("Part 1 done. Now run add_action_edit_modal.py to insert the edit modal UI.")