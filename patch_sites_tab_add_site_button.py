"""
patch_sites_tab_add_site_button.py  (v2 — string navigate-view)
In ProjectDetailModal's Sites tab, swap 'Log Visit' for '+ Add Site' and
redirect the user to Field Operations → Sites (which already has the full
Add Project Site form).
"""
import pathlib

p = pathlib.Path("src/components/projects/ProjectDetailModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# --- 1. Replace the Sites-tab Log Visit button -------------------------------
old_button = """                {canLogVisit && (
                  <button
                    type="button"
                    onClick={() => { onClose(); onLogVisitClick(project); }}
                    className="px-2.5 py-1 rounded text-xs font-semibold bg-emerald-700 text-white hover:bg-emerald-800 inline-flex items-center"
                  >
                    <ClipboardList className="w-3.5 h-3.5 mr-1" />
                    Log Visit
                  </button>
                )}
"""
if old_button not in src:
    print("Log Visit button anchor NOT FOUND.")
    raise SystemExit(1)

new_button = """                <button
                  type="button"
                  onClick={() => setIsAddSiteOpen(true)}
                  className="px-2.5 py-1 rounded text-xs font-semibold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center"
                  title="Register a new monitoring site under this project"
                >
                  <Plus className="w-3.5 h-3.5 mr-1" />
                  Add Site
                </button>
"""
src = src.replace(old_button, new_button, 1)
changes.append("Sites tab: 'Log Visit' → '+ Add Site'")

# --- 2. Add isAddSiteOpen state ---------------------------------------------
state_anchor = "  const [activeTab, setActiveTab] = useState<'overview' | 'sites' | 'inspections' | 'monitoring'>('overview');\n"
if state_anchor not in src:
    print("activeTab state anchor NOT FOUND.")
    raise SystemExit(1)
src = src.replace(
    state_anchor,
    state_anchor + "  const [isAddSiteOpen, setIsAddSiteOpen] = useState(false);\n",
    1,
)
changes.append("added isAddSiteOpen state")

# --- 3. Import Plus from lucide-react ---------------------------------------
import_anchor = "  ClipboardList,\n"
if "  Plus,\n" not in src and "  Plus\n" not in src:
    if import_anchor not in src:
        print("lucide import anchor NOT FOUND.")
        raise SystemExit(1)
    src = src.replace(import_anchor, "  Plus,\n" + import_anchor, 1)
    changes.append("imported Plus icon")

# --- 4. Insert the Add Site confirm modal before the Milestone editor -------
milestone_anchor = "      {/* Milestone editor modal */}\n"
if milestone_anchor not in src:
    print("Milestone modal anchor NOT FOUND.")
    raise SystemExit(1)

add_site_modal = """      {/* Add Site redirect modal */}
      {isAddSiteOpen && (
        <div
          className="fixed inset-0 z-[60] bg-black/60 flex items-center justify-center p-4"
          onClick={() => setIsAddSiteOpen(false)}
        >
          <div
            className="bg-white rounded-xl shadow-2xl max-w-md w-full p-5 space-y-4 text-xs"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-200 pb-2">
              <h3 className="font-bold text-slate-900 text-sm">Add Site to {project.id}</h3>
              <button
                type="button"
                onClick={() => setIsAddSiteOpen(false)}
                className="text-slate-400 hover:text-slate-700"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-slate-600 leading-relaxed">
              Sites are registered from the <strong>Field Operations → Sites</strong> page, where you can
              capture coordinates, terrain type, ecological zone, and baseline conditions.
              Click below to open that page.
            </p>
            <div className="flex justify-end gap-2 pt-2 border-t border-slate-200">
              <button
                type="button"
                onClick={() => setIsAddSiteOpen(false)}
                className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-200 hover:bg-slate-300 text-slate-800"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsAddSiteOpen(false);
                  onClose();
                  window.dispatchEvent(new CustomEvent('navigate-view', { detail: 'field-ops' }));
                }}
                className="px-4 py-1.5 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white"
              >
                Open Field Operations → Sites
              </button>
            </div>
          </div>
        </div>
      )}

"""
src = src.replace(milestone_anchor, add_site_modal + milestone_anchor, 1)
changes.append("inserted Add Site redirect modal")

p.write_text(src, encoding="utf-8")

print("Changes:")
for c in changes:
    print(" -", c)

opens = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")