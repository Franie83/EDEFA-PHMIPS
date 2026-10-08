"""
fix_milestone_save.py — fixes the milestone save bug.

Root cause: ProjectDetailModal gets `project={selectedProject}` which is a
snapshot from when the user clicked the card. After saving a milestone,
App.tsx calls loadData() which refreshes the `projects` array — but
`selectedProject` is stale, so the modal keeps rendering the old data
and the new milestone never appears.

Fix: make ProjectDetailModal derive its `project` prop from the live
`projects` array by looking up the currently selected project's id.

This script:
  1. Backs up App.tsx.
  2. Finds the <ProjectDetailModal ...> JSX block.
  3. Rewrites the `project={...}` prop to look up from `projects`.
  4. Verifies the change was applied.

Run from the eco/ folder:  python fix_milestone_save.py
"""
import re
import shutil
from datetime import datetime
from pathlib import Path

APP_TSX = Path(r".\src\App.tsx")
if not APP_TSX.exists():
    raise SystemExit(f"Not found: {APP_TSX.resolve()}")

src = APP_TSX.read_text(encoding="utf-8")

ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")
backup = APP_TSX.with_suffix(f".tsx.bak_{ts}")
shutil.copy2(APP_TSX, backup)
print(f"Backup written: {backup}")

# The fix: derive `project` from the live `projects` array.
NEW_PROJECT_PROP = (
    "project={selectedProject ? "
    "(projects.find(p => p.id === selectedProject.id) || selectedProject) "
    ": null}"
)

# Already applied?
if "projects.find(p => p.id === selectedProject.id)" in src:
    print("Fix already applied — nothing to do.")
    raise SystemExit(0)

# Find the ProjectDetailModal opening tag and rewrite its `project=` prop.
pattern = re.compile(
    r"(<ProjectDetailModal\b[^>]*?)\bproject=\{selectedProject\}",
    re.DOTALL,
)
m = pattern.search(src)

if not m:
    # Fallback: any `project={selectedProject}` inside the file
    alt = re.compile(r"\bproject=\{selectedProject\}", re.MULTILINE)
    if not alt.search(src):
        raise SystemExit(
            "Could not find <ProjectDetailModal project={selectedProject} ...>. "
            "Nothing written."
        )
    src = alt.sub(NEW_PROJECT_PROP, src, count=1)
    print(" - PATCH 1 (fallback): replaced project={selectedProject}")
else:
    src = src[:m.start()] + m.group(1) + NEW_PROJECT_PROP + src[m.end():]
    print(" - PATCH 1: updated <ProjectDetailModal> to derive project from live data")

APP_TSX.write_text(src, encoding="utf-8")
print()
print(f"Patched: {APP_TSX.resolve()}")
print("Next: hard-refresh the browser (Ctrl+Shift+R twice), then test saving a milestone.")