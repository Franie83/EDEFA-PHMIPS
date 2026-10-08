"""
patch_sidebar_reorg_v2.py
Reorganises the sidebar into 3 balanced categories, drops number prefixes.
Uses the exact current NAV_ITEMS block as the anchor.
"""
import pathlib
import re

p = pathlib.Path("src/components/common/Sidebar.tsx")
src = p.read_text(encoding="utf-8")

# Verbatim from the file — including the blank lines between groups
old_block = """const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard', label: '1. Executive Dashboard', icon: LayoutDashboard, category: 'OVERVIEW' },

  { id: 'hazards', label: '2. Hazard Reports', icon: AlertTriangle, category: 'OVERVIEW' },

  { id: 'projects', label: '3. Projects Register', icon: FolderGit2, category: 'INTERVENTIONS & WORKFLOW' },
  { id: 'actions', label: '10. Actions & Follow-up', icon: CheckCircle, category: 'INTERVENTIONS & WORKFLOW' },

  { id: 'reports', label: '12. Comprehensive Reports', icon: FileSpreadsheet, category: 'INTELLIGENCE & REPORTS' },
  { id: 'analytics', label: '13. Analytics & Decision Support', icon: LineChart, category: 'INTELLIGENCE & REPORTS' },

  { id: 'audit', label: '14. Audit Logs & Compliance', icon: History, category: 'GOVERNANCE & SYSTEM' },
  { id: 'cms', label: '15. Content Management', icon: Settings, category: 'GOVERNANCE & SYSTEM' }
];"""

new_block = """const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard', label: 'Executive Dashboard',          icon: LayoutDashboard, category: 'OVERVIEW' },
  { id: 'hazards',   label: 'Hazard Reports',               icon: AlertTriangle,   category: 'OVERVIEW' },
  { id: 'projects',  label: 'Projects Register',            icon: FolderGit2,      category: 'OVERVIEW' },
  { id: 'actions',   label: 'Actions & Follow-up',          icon: CheckCircle,     category: 'OVERVIEW' },

  { id: 'reports',   label: 'Comprehensive Reports',        icon: FileSpreadsheet, category: 'INTELLIGENCE' },
  { id: 'analytics', label: 'Analytics & Decision Support', icon: LineChart,       category: 'INTELLIGENCE' },

  { id: 'audit',     label: 'Audit Logs & Compliance',      icon: History,         category: 'GOVERNANCE' },
  { id: 'cms',       label: 'Content Management',           icon: Settings,        category: 'GOVERNANCE' }
];"""

if new_block in src:
    print("Already reorganised — nothing to do.")
    raise SystemExit(0)

if old_block not in src:
    print("Exact NAV_ITEMS block NOT FOUND — paste lines 29-45 verbatim.")
    raise SystemExit(1)

src = src.replace(old_block, new_block, 1)

# Cleanup unused icons if any are now unreferenced (only the import line remains)
for icon in ["MapPin", "Camera", "CheckSquare", "Video", "Compass"]:
    hits = len(re.findall(rf"\b{icon}\b", src))
    if hits == 1:
        src = re.sub(rf"(\n\s*){icon},", "", src, count=1)
        print(f"Removed unused {icon} import")
    elif hits == 0:
        print(f"{icon} already gone")
    else:
        print(f"{icon} still used ({hits} refs) — kept")

p.write_text(src, encoding="utf-8")

print()
print("Changes:")
print(" - reorganized NAV_ITEMS into OVERVIEW / INTELLIGENCE / GOVERNANCE")
print(" - dropped numeric prefixes from labels")

o, c = src.count("{"), src.count("}")
print(f"\nSidebar.tsx brace balance: {'OK' if o == c else f'MISMATCH ({o} vs {c})'}")