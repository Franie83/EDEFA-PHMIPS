import pathlib

p = pathlib.Path("src/components/projects/ProjectDetailModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add useState + api imports
if "import React, { useState }" not in src:
    src = src.replace("import React from 'react';", "import React, { useState } from 'react';", 1)
    changes.append("added useState import")
if "import { api } from" not in src:
    # Insert after the lucide-react import block
    marker = "} from 'lucide-react';"
    if marker in src:
        src = src.replace(marker, marker + "\nimport { api } from '../../services/api.ts';", 1)
        changes.append("added api import")

# 2. Add onRefresh prop
old_iface = """  onApproveProject?: (project: Project) => void;
  currentUserRole?: string;
  onRejectProject?: (project: Project) => void;
}"""
new_iface = """  onApproveProject?: (project: Project) => void;
  currentUserRole?: string;
  onRejectProject?: (project: Project) => void;
  onRefresh?: () => Promise<void> | void;
}"""
if old_iface in src:
    src = src.replace(old_iface, new_iface)
    changes.append("added onRefresh prop")

# 3. Destructure onRefresh
old_dest = """  onApproveProject,
  currentUserRole,
  onRejectProject}) => {"""
new_dest = """  onApproveProject,
  currentUserRole,
  onRejectProject,
  onRefresh}) => {"""
if old_dest in src:
    src = src.replace(old_dest, new_dest)
    changes.append("destructured onRefresh")

# 4. Insert milestone state + handlers after the `if (!project) return null;` line
guard = "  if (!project) return null;"
insert = """  if (!project) return null;

  // --- Milestone editing ---
  const canEditProject = currentUserRole === 'SUPER_ADMIN' || currentUserRole === 'COORDINATOR' || currentUserRole === 'INSPECTOR';
  const [milestoneDraft, setMilestoneDraft] = useState<any | null>(null);
  const [savingMilestones, setSavingMilestones] = useState(false);
  const allMilestones: Milestone[] = Array.isArray(project.milestones) ? project.milestones : [];

  const saveMilestones = async (next: Milestone[]) => {
    setSavingMilestones(true);
    try {
      await api.updateProject(project.id, { milestones: next } as any);
      await onRefresh?.();
    } catch (err: any) {
      alert('Failed to save milestones: ' + (err.message || err));
    } finally {
      setSavingMilestones(false);
    }
  };

  const openAddMilestone = () => {
    setMilestoneDraft({
      id: '',
      title: '',
      due_date: new Date().toISOString().split('T')[0],
      status: 'Pending' as const,
      progress_percentage: 0,
    });
  };

  const openEditMilestone = (m: Milestone) => setMilestoneDraft({ ...m });

  const saveMilestoneDraft = async () => {
    if (!milestoneDraft || !milestoneDraft.title?.trim()) return;
    const draft = { ...milestoneDraft };
    if (!draft.id) {
      draft.id = 'M' + (allMilestones.length + 1) + '-' + Date.now().toString().slice(-4);
    }
    let next: Milestone[];
    const idx = allMilestones.findIndex(x => x.id === draft.id);
    if (idx >= 0) {
      next = allMilestones.map(x => (x.id === draft.id ? draft : x));
    } else {
      next = [...allMilestones, draft];
    }
    await saveMilestones(next);
    setMilestoneDraft(null);
  };

  const deleteMilestone = async (id: string) => {
    if (!window.confirm('Delete this milestone?')) return;
    await saveMilestones(allMilestones.filter(x => x.id !== id));
  };

  const cycleMilestoneStatus = async (m: Milestone) => {
    const order: Milestone['status'][] = ['Pending', 'In Progress', 'Completed', 'Delayed'];
    const i = order.indexOf(m.status);
    const nextStatus = order[(i + 1) % order.length];
    const nextPct = nextStatus === 'Completed' ? 100 : m.progress_percentage;
    const next = allMilestones.map(x =>
      x.id === m.id ? { ...x, status: nextStatus, progress_percentage: nextPct } : x
    );
    await saveMilestones(next);
  };"""

if guard in src:
    src = src.replace(guard, insert, 1)
    changes.append("added milestone state + handlers")

# 5. Replace the milestone render block with the editor version
old_block = """          {/* Milestones Schedule */}
          <div>
            <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider mb-2">
              Project Contract Milestones ({project.milestones?.length || 0})
            </h4>
            <div className="space-y-2">
              {(!project.milestones || project.milestones.length === 0) ? (
                <div className="p-3 text-center bg-slate-50 rounded-lg text-slate-400">
                  No milestone schedule defined for this project.
                </div>
              ) : (
                project.milestones.map(m => (
                  <div
                    key={m.id}
                    className="p-2.5 rounded-lg border border-slate-200 bg-slate-50 flex items-center justify-between"
                  >"""

new_block = """          {/* Milestones Schedule */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
                Project Contract Milestones ({allMilestones.length})
              </h4>
              {canEditProject && (
                <button
                  type="button"
                  onClick={openAddMilestone}
                  disabled={savingMilestones}
                  className="px-2 py-1 rounded text-[10px] font-bold bg-emerald-700 hover:bg-emerald-800 text-white disabled:opacity-50"
                >
                  + Add Milestone
                </button>
              )}
            </div>
            <div className="space-y-2">
              {allMilestones.length === 0 ? (
                <div className="p-3 text-center bg-slate-50 rounded-lg text-slate-400 text-xs">
                  No milestone schedule defined for this project.
                  {canEditProject && (
                    <div className="mt-1 text-[10px]">Click "+ Add Milestone" to define one.</div>
                  )}
                </div>
              ) : (
                allMilestones.map(m => (
                  <div
                    key={m.id}
                    className="p-2.5 rounded-lg border border-slate-200 bg-slate-50 flex items-center justify-between text-xs"
                  >
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[10px] text-slate-500">{m.id}</span>
                        <button
                          type="button"
                          onClick={() => canEditProject && cycleMilestoneStatus(m)}
                          disabled={!canEditProject || savingMilestones}
                          className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                            m.status === 'Completed' ? 'bg-emerald-100 text-emerald-800' :
                            m.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                            m.status === 'Delayed' ? 'bg-rose-100 text-rose-800' :
                            'bg-slate-200 text-slate-700'
                          } ${canEditProject ? 'cursor-pointer hover:opacity-80' : ''}`}
                          title={canEditProject ? 'Click to cycle status' : m.status}
                        >
                          {m.status}
                        </button>
                        <span className="font-semibold text-slate-800 truncate">{m.title}</span>
                      </div>
                      <div className="text-[10px] text-slate-500 mt-0.5">
                        Due {m.due_date || '—'} · {m.progress_percentage || 0}%
                      </div>
                    </div>
                    {canEditProject && (
                      <div className="flex items-center gap-1 ml-2 shrink-0">
                        <button
                          type="button"
                          onClick={() => openEditMilestone(m)}
                          disabled={savingMilestones}
                          className="px-1.5 py-0.5 rounded text-[10px] border border-slate-300 hover:bg-slate-100"
                          title="Edit"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => deleteMilestone(m.id)}
                          disabled={savingMilestones}
                          className="px-1.5 py-0.5 rounded text-[10px] border border-rose-300 text-rose-700 hover:bg-rose-50"
                          title="Delete"
                        >
                          ✕
                        </button>
                      </div>
                    )}
                  </div>"""

if old_block in src:
    src = src.replace(old_block, new_block)
    changes.append("replaced milestone render block")

# 6. Append the milestone form modal at the end of the component (before the closing `</div>` of the outer wrapper)
# Find the last </div> that closes the outer modal, and insert before it.
# Simpler: append a new component and render it conditionally at the end of the JSX.
# Find the closing of the outer modal by locating the footer's "Close" button block.
close_marker = "</div>\n    </div>\n  );\n};"
if close_marker in src:
    milestone_form = """
      {/* Milestone editor modal */}
      {milestoneDraft && (
        <div className="fixed inset-0 z-[60] bg-black/60 flex items-center justify-center p-4" onClick={() => setMilestoneDraft(null)}>
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-5 space-y-3 text-xs" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-sm font-bold text-slate-900">
              {milestoneDraft.id ? 'Edit Milestone' : 'Add Milestone'}
            </h3>
            <label className="block">
              <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Title *</span>
              <input
                autoFocus
                value={milestoneDraft.title}
                onChange={e => setMilestoneDraft({ ...milestoneDraft, title: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300"
                placeholder="e.g. Foundation excavation complete"
              />
            </label>
            <div className="grid grid-cols-2 gap-2">
              <label className="block">
                <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Due Date</span>
                <input
                  type="date"
                  value={milestoneDraft.due_date}
                  onChange={e => setMilestoneDraft({ ...milestoneDraft, due_date: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300"
                />
              </label>
              <label className="block">
                <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Progress %</span>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={milestoneDraft.progress_percentage}
                  onChange={e => setMilestoneDraft({ ...milestoneDraft, progress_percentage: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300"
                />
              </label>
            </div>
            <label className="block">
              <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Status</span>
              <select
                value={milestoneDraft.status}
                onChange={e => setMilestoneDraft({ ...milestoneDraft, status: e.target.value as any })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
              >
                <option value="Pending">Pending</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Delayed">Delayed</option>
              </select>
            </label>
            <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
              <button
                type="button"
                onClick={() => setMilestoneDraft(null)}
                className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={saveMilestoneDraft}
                disabled={savingMilestones || !milestoneDraft.title?.trim()}
                className="px-3 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white font-bold disabled:opacity-50"
              >
                {savingMilestones ? 'Saving…' : 'Save Milestone'}
              </button>
            </div>
          </div>
        </div>
      )}
"""
    src = src.replace(close_marker, milestone_form + close_marker, 1)
    changes.append("added milestone editor modal")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)