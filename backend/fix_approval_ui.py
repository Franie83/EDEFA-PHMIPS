"""
Fix the approval UI migration.

The previous migration inserted handlers that reference undefined variables:
  - currentUser  (not in props)
  - onRefresh    (not in props)
  - api          (not imported)

This script:
  1. Adds api import to both components
  2. Adds currentUser and onRefresh to both prop interfaces + destructures
  3. Wires the new props from App.tsx
  4. Fixes the App.tsx render calls

Idempotent.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERVENTIONS = ROOT / "src" / "components" / "interventions" / "InterventionPlanning.tsx"
PROJECTS = ROOT / "src" / "components" / "projects" / "ProjectList.tsx"
APP = ROOT / "src" / "App.tsx"

for f in [INTERVENTIONS, PROJECTS, APP]:
    if not f.exists():
        raise SystemExit(f"Not found: {f}")

# ============================================================
# PATCH 1 — InterventionPlanning.tsx
# ============================================================
print("=" * 60)
print("PATCH 1: InterventionPlanning.tsx")
print("=" * 60)

text = INTERVENTIONS.read_text(encoding="utf-8")

# 1a: Add api import
if "from '../../services/api.ts'" not in text and "from '../../services/api'" not in text:
    old = "import { Intervention, Hazard, Project } from '../../types/index.ts';"
    new = "import { Intervention, Hazard, Project } from '../../types/index.ts';\nimport { api } from '../../services/api.ts';"
    if old in text:
        text = text.replace(old, new, 1)
        print("  Added api import")
    else:
        print("  WARNING: types import anchor not found")
else:
    print("  api import already present")

# 1b: Extend prop interface
old_iface = """interface InterventionPlanningProps {
  interventions: Intervention[];
  hazards: Hazard[];
  projects: Project[];
  onUpdateIntervention: (id: string, data: Partial<Intervention>) => Promise<void>;
}"""
new_iface = """interface InterventionPlanningProps {
  interventions: Intervention[];
  hazards: Hazard[];
  projects: Project[];
  onUpdateIntervention: (id: string, data: Partial<Intervention>) => Promise<void>;
  currentUser?: { role?: string; name?: string } | null;
  onRefresh?: () => Promise<void> | void;
}"""
if old_iface in text:
    text = text.replace(old_iface, new_iface, 1)
    print("  Extended prop interface")
elif "currentUser?:" in text and "onRefresh?:" in text:
    print("  Prop interface already extended")
else:
    print("  WARNING: prop interface anchor not found")

# 1c: Extend destructure
old_destr = """export const InterventionPlanning: React.FC<InterventionPlanningProps> = ({
  interventions = [],
  hazards = [],
  projects = [],
  onUpdateIntervention
}) => {"""
new_destr = """export const InterventionPlanning: React.FC<InterventionPlanningProps> = ({
  interventions = [],
  hazards = [],
  projects = [],
  onUpdateIntervention,
  currentUser,
  onRefresh
}) => {"""
if old_destr in text:
    text = text.replace(old_destr, new_destr, 1)
    print("  Extended destructure")
elif "currentUser,\n  onRefresh" in text:
    print("  Destructure already extended")
else:
    print("  WARNING: destructure anchor not found")

INTERVENTIONS.write_text(text, encoding="utf-8")

# ============================================================
# PATCH 2 — ProjectList.tsx
# ============================================================
print()
print("=" * 60)
print("PATCH 2: ProjectList.tsx")
print("=" * 60)

text = PROJECTS.read_text(encoding="utf-8")

# 2a: Add api import
if "from '../../services/api.ts'" not in text and "from '../../services/api'" not in text:
    old = "import { Project, ProjectStatus } from '../../types/index.ts';"
    new = "import { Project, ProjectStatus } from '../../types/index.ts';\nimport { api } from '../../services/api.ts';"
    if old in text:
        text = text.replace(old, new, 1)
        print("  Added api import")
    else:
        print("  WARNING: types import anchor not found")
else:
    print("  api import already present")

# 2b: Extend prop interface
old_iface = """interface ProjectListProps {
  projects?: Project[];
  onSelectProject: (project: Project) => void;
  onOpenCreateModal?: () => void;
  onNewProjectClick?: () => void;
  states?: string[];
  statesAndLgas?: Record<string, string[]>;
  categories?: string[];
}"""
new_iface = """interface ProjectListProps {
  projects?: Project[];
  onSelectProject: (project: Project) => void;
  onOpenCreateModal?: () => void;
  onNewProjectClick?: () => void;
  states?: string[];
  statesAndLgas?: Record<string, string[]>;
  categories?: string[];
  currentUser?: { role?: string; name?: string } | null;
  onRefresh?: () => Promise<void> | void;
}"""
if old_iface in text:
    text = text.replace(old_iface, new_iface, 1)
    print("  Extended prop interface")
elif "currentUser?:" in text and "onRefresh?:" in text:
    print("  Prop interface already extended")
else:
    print("  WARNING: prop interface anchor not found")

# 2c: Extend destructure
old_destr = """export const ProjectList: React.FC<ProjectListProps> = ({
  projects = [],
  onSelectProject,
  onOpenCreateModal,
  onNewProjectClick,
  states,
  statesAndLgas,
  categories = []
}) => {"""
new_destr = """export const ProjectList: React.FC<ProjectListProps> = ({
  projects = [],
  onSelectProject,
  onOpenCreateModal,
  onNewProjectClick,
  states,
  statesAndLgas,
  categories = [],
  currentUser,
  onRefresh
}) => {"""
if old_destr in text:
    text = text.replace(old_destr, new_destr, 1)
    print("  Extended destructure")
elif "currentUser,\n  onRefresh" in text:
    print("  Destructure already extended")
else:
    print("  WARNING: destructure anchor not found")

PROJECTS.write_text(text, encoding="utf-8")

# ============================================================
# PATCH 3 — App.tsx — pass the new props
# ============================================================
print()
print("=" * 60)
print("PATCH 3: App.tsx")
print("=" * 60)

text = APP.read_text(encoding="utf-8")

# 3a: InterventionPlanning render
old_render = """<InterventionPlanning
                interventions={interventions}
                hazards={hazards}
                projects={projects}
                onUpdateIntervention={handleUpdateIntervention}
              />"""
new_render = """<InterventionPlanning
                interventions={interventions}
                hazards={hazards}
                projects={projects}
                onUpdateIntervention={handleUpdateIntervention}
                currentUser={currentUser}
                onRefresh={loadData}
              />"""
if old_render in text:
    text = text.replace(old_render, new_render, 1)
    print("  Wired InterventionPlanning props")
elif "onRefresh={loadData}" in text and "InterventionPlanning" in text:
    print("  InterventionPlanning already wired")
else:
    # Try a looser match
    print("  WARNING: InterventionPlanning render anchor not found — trying looser match")
    import re
    pattern = r'(<InterventionPlanning\b[^/]*?)(\s*/>)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        block = match.group(0)
        if "currentUser" not in block:
            # Insert props before the closing />
            new_block = block.replace(
                "onUpdateIntervention={handleUpdateIntervention}",
                "onUpdateIntervention={handleUpdateIntervention}\n                currentUser={currentUser}\n                onRefresh={loadData}",
            )
            text = text.replace(block, new_block, 1)
            print("  Wired via looser match")
    else:
        print("  WARNING: could not wire InterventionPlanning")

# 3b: ProjectList render
old_render = """<ProjectList
                projects={projects}
                statesAndLgas={referenceData?.states_and_lgas || {}}
                categories={referenceData?.hazard_categories || []}
                onSelectProject={p => setSelectedProject(p)}
                onNewProjectClick={() => setIsProjectModalOpen(true)}
              />"""
new_render = """<ProjectList
                projects={projects}
                statesAndLgas={referenceData?.states_and_lgas || {}}
                categories={referenceData?.hazard_categories || []}
                onSelectProject={p => setSelectedProject(p)}
                onNewProjectClick={() => setIsProjectModalOpen(true)}
                currentUser={currentUser}
                onRefresh={loadData}
              />"""
if old_render in text:
    text = text.replace(old_render, new_render, 1)
    print("  Wired ProjectList props")
elif "onRefresh={loadData}" in text and "ProjectList" in text:
    print("  ProjectList already wired")
else:
    print("  WARNING: ProjectList render anchor not found — trying looser match")
    import re
    pattern = r'(<ProjectList\b[^/]*?)(\s*/>)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        block = match.group(0)
        if "currentUser" not in block:
            new_block = block.replace(
                "onNewProjectClick={() => setIsProjectModalOpen(true)}",
                "onNewProjectClick={() => setIsProjectModalOpen(true)}\n                currentUser={currentUser}\n                onRefresh={loadData}",
            )
            text = text.replace(block, new_block, 1)
            print("  Wired via looser match")
    else:
        print("  WARNING: could not wire ProjectList")

APP.write_text(text, encoding="utf-8")

print()
print("=" * 60)
print("FIX COMPLETE")
print("=" * 60)
print("""
Next:
  1. Run: npx tsc --noEmit   (should be clean)
  2. Restart Vite if needed
  3. Reload the browser
  4. Log in as inspector (Director) → intervention card should show "Director Approve"
  5. Log in as executive → intervention card with "Director Approved" should show "Executive Approve"

The queue tabs and approve buttons still need to be placed manually — see
the previous migration script's output for the snippets.
""")