"""
Insert the Edit Action modal UI into ActionTracking.tsx.
Handles both onClick and onSubmit paths.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "edit-action-modal" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# Find the closing `</div>` of the root, just before `);` and `};`
# Structure is:   </div>\n  );\n};\n
closing_candidates = [
    "\n    </div>\n  );\n};\n",
    "\n  </div>\n  );\n};\n",
    "</div>\n  );\n};",
]

insert_at = None
for cand in closing_candidates:
    idx = text.rfind(cand)
    if idx != -1:
        insert_at = idx
        break

if insert_at is None:
    raise SystemExit("Could not find component closing pattern. Paste the last 30 lines.")

EDIT_MODAL = '''
      {/* Edit Action Modal */}
      {isEditModalOpen && editingAction && (
        <div
          id="edit-action-modal"
          className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4"
        >
          <div className="bg-white rounded-xl shadow-2xl max-w-xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200 text-xs">
            <div className="px-5 py-4 bg-emerald-950 text-white flex items-center justify-between border-b border-emerald-900">
              <div>
                <h2 className="text-sm font-bold">Edit Action Directive</h2>
                <p className="text-[11px] text-emerald-300">{editingAction.id}</p>
              </div>
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="p-1 rounded bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="flex-1 overflow-y-auto p-5 space-y-3">
              {editError && (
                <div className="rounded-lg bg-rose-50 border border-rose-200 text-rose-800 p-2.5">
                  {editError}
                </div>
              )}

              <label className="block">
                <span className="font-semibold text-slate-700">Title</span>
                <input
                  value={editForm.title || ''}
                  onChange={e => setEditForm({ ...editForm, title: e.target.value })}
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                />
              </label>

              <label className="block">
                <span className="font-semibold text-slate-700">Description</span>
                <textarea
                  value={editForm.description || ''}
                  onChange={e => setEditForm({ ...editForm, description: e.target.value })}
                  rows={3}
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 resize-y"
                />
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <label className="block">
                  <span className="font-semibold text-slate-700">Responsible Person</span>
                  <input
                    value={editForm.responsible_person || ''}
                    onChange={e => setEditForm({ ...editForm, responsible_person: e.target.value })}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  />
                </label>

                <label className="block">
                  <span className="font-semibold text-slate-700">Organization</span>
                  <input
                    value={editForm.responsible_organization || ''}
                    onChange={e => setEditForm({ ...editForm, responsible_organization: e.target.value })}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  />
                </label>

                <label className="block">
                  <span className="font-semibold text-slate-700">Priority</span>
                  <select
                    value={editForm.priority || 'HIGH'}
                    onChange={e => setEditForm({ ...editForm, priority: e.target.value as any })}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  >
                    <option value="CRITICAL">CRITICAL</option>
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="LOW">LOW</option>
                  </select>
                </label>

                <label className="block">
                  <span className="font-semibold text-slate-700">Status</span>
                  <select
                    value={editForm.status || 'Assigned'}
                    onChange={e => setEditForm({ ...editForm, status: e.target.value as any })}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  >
                    <option value="Open">Open</option>
                    <option value="Assigned">Assigned</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                    <option value="Verified">Verified</option>
                    <option value="Closed">Closed</option>
                  </select>
                </label>

                <label className="block">
                  <span className="font-semibold text-slate-700">Due Date</span>
                  <input
                    type="date"
                    value={(editForm.due_date as string) || ''}
                    onChange={e => setEditForm({ ...editForm, due_date: e.target.value })}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  />
                </label>

                <label className="block">
                  <span className="font-semibold text-slate-700">Progress %</span>
                  <input
                    type="number"
                    min={0}
                    max={100}
                    value={editForm.progress_percentage ?? 0}
                    onChange={e => setEditForm({ ...editForm, progress_percentage: Number(e.target.value) })}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  />
                </label>
              </div>
            </form>

            <div className="px-5 py-3 border-t border-slate-200 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsEditModalOpen(false)}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={(e) => handleEditSubmit(e as any)}
                disabled={editBusy}
                className="px-5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white disabled:opacity-50 inline-flex items-center gap-1.5"
              >
                <Save className="w-4 h-4" />
                {editBusy ? 'Saving…' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}

'''

text = text[:insert_at] + EDIT_MODAL + text[insert_at:]
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Inserted edit action modal")