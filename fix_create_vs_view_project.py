import pathlib

p = pathlib.Path("src/components/interventions/InterventionPlanning.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# ---------- 1. Card-level button ----------
old_btn = """                  {isFullyApproved && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setProjectSourceIntervention(item);
                        setIsProjectModalOpen(true);
                      }}
                      className="px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center gap-1.5"
                    >
                      <FolderGit2 className="w-3.5 h-3.5" />
                      Create Project
                    </button>
                  )}"""

new_btn = """                  {isFullyApproved && !item.project_id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setProjectSourceIntervention(item);
                        setIsProjectModalOpen(true);
                      }}
                      className="px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center gap-1.5"
                    >
                      <FolderGit2 className="w-3.5 h-3.5" />
                      Create Project
                    </button>
                  )}
                  {item.project_id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        // Fire an event the parent can listen for, or just navigate
                        window.dispatchEvent(new CustomEvent('navigate-view', { detail: 'projects' }));
                      }}
                      className="px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-700 hover:bg-slate-600 text-white inline-flex items-center gap-1.5"
                      title={`Open project ${item.project_id} in the Projects register`}
                    >
                      <FolderGit2 className="w-3.5 h-3.5" />
                      View Project ({item.project_id})
                    </button>
                  )}"""

if old_btn in src:
    src = src.replace(old_btn, new_btn)
    changes.append("card button toggles between Create / View Project")
else:
    changes.append("card button pattern NOT FOUND")

# ---------- 2. Detail modal footer button ----------
old_modal_btn = """          {isFullyApproved && !project && (
            <button
              onClick={() => onCreateProject(intervention)}
              className="px-3 py-2 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center gap-1.5"
            >
              Create Project
            </button>
          )}"""

new_modal_btn = """          {isFullyApproved && !project && !intervention.project_id && (
            <button
              onClick={() => onCreateProject(intervention)}
              className="px-3 py-2 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center gap-1.5"
            >
              Create Project
            </button>
          )}
          {(intervention.project_id || project) && (
            <button
              onClick={() => {
                window.dispatchEvent(new CustomEvent('navigate-view', { detail: 'projects' }));
                onClose();
              }}
              className="px-3 py-2 rounded-lg text-xs font-bold bg-slate-700 hover:bg-slate-600 text-white inline-flex items-center gap-1.5"
            >
              <FolderGit2 className="w-3.5 h-3.5" />
              View Project ({intervention.project_id || project?.id})
            </button>
          )}"""

if old_modal_btn in src:
    src = src.replace(old_modal_btn, new_modal_btn)
    changes.append("modal button toggles between Create / View Project")
else:
    changes.append("modal button pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)