import pathlib

p = pathlib.Path("src/components/projects/ProjectDetailModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add useState import
if "import React from 'react';" in src and "useState" not in src:
    src = src.replace(
        "import React from 'react';",
        "import React, { useState } from 'react';",
        1
    )
    changes.append("added useState import")

# 2. Add props for save callback
old_iface = """interface ProjectDetailModalProps {
  project: Project | null;
  onClose: () => void;
  onLogVisitClick: (project: Project) => void;
  onNavigateToMap: (lat: number, lng: number) => void;
  onApproveProject?: (project: Project) => void;
  currentUserRole?: string;
  onRejectProject?: (project: Project) => void;
}"""
new_iface = """interface ProjectDetailModalProps {
  project: Project | null;
  onClose: () => void;
  onLogVisitClick: (project: Project) => void;
  onNavigateToMap: (lat: number, lng: number) => void;
  onApproveProject?: (project: Project) => void;
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
  onRejectProject}) => {
  if (!project) return null;"""
new_dest = """  onApproveProject,
  currentUserRole,
  onRejectProject,
  onRefresh}) => {
  if (!project) return null;"""
if old_dest in src:
    src = src.replace(old_dest, new_dest)
    changes.append("destructured onRefresh")

# 4. Add state + handlers right after the `const canApproveProject = ...` line
# We'll find the marker and insert after it
marker = "  const canApproveProject ="
idx = src.find(marker)
if idx > 0:
    end_idx = src.find("\n", src.find("\n", idx) + 1)
    insert_block = """

  // --- Milestone editing ---
  const canEditProject = currentUserRole === 'SUPER_ADMIN' || currentUserRole === 'COORDINATOR' || currentUserRole === 'INSPECTOR';
  const [milestoneDraft, setMilestoneDraft] = useState<any | null>(null);
  const [savingMilestones, setSavingMilestones] = useState(false);

  const allMilestones: any[] = Array.isArray((project as any).milestones) ? (project as any).milestones : [];

  const saveMilestones = async (next: any[]) => {
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
      planned_start: '',
      planned_end: '',
      planned_percentage: 10,
      completed: false,
      completed_at: null,
      notes: '',
    });
  };

  const openEditMilestone = (m: any) => setMilestoneDraft({ ...m });

  const saveMilestoneDraft = async () => {
    if (!milestoneDraft || !milestoneDraft.title?.trim()) return;
    const draft = { ...milestoneDraft };
    if (!draft.id) {
      // Generate a simple id
      draft.id = 'M' + (allMilestones.length + 1) + '-' + Date.now().toString().slice(-4);
    }
    let next: any[];
    const existingIndex = allMilestones.findIndex(x => x.id === draft.id);
    if (existingIndex >= 0) {
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

  const toggleMilestoneComplete = async (m: any) => {
    const next = allMilestones.map(x =>
      x.id === m.id
        ? { ...x, completed: !x.completed, completed_at: !x.completed ? new Date().toISOString() : null }
        : x
    );
    await saveMilestones(next);
  };
"""
    src = src[:end_idx] + insert_block + src[end_idx:]
    changes.append("added milestone state + handlers")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)
print("\nNOTE: This is a skeleton — the full patch needs the Milestone type + refresh handling.")