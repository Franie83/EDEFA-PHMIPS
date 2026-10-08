"""
patch_sidebar_remove_evidence_v2.py
Removes '7. Evidence & Media Repository' from the sidebar. Keeps the
'evidence' route alive in App.tsx.
Moves 'Hazard Reports' under a renamed 'OVERVIEW' category so we don't
leave a single-item 'FIELD & HAZARDS' header orphaned.
"""
import pathlib
import re

p = pathlib.Path("src/components/common/Sidebar.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Remove the evidence nav item
old_evidence = "  { id: 'evidence', label: '7. Evidence & Media Repository', icon: Video, category: 'FIELD & HAZARDS' },\n"
if old_evidence in src:
    src = src.replace(old_evidence, "", 1)
    changes.append("removed '7. Evidence & Media Repository' from NAV_ITEMS")
else:
    if "id: 'evidence'" not in src:
        changes.append("evidence nav item already absent")
    else:
        print("Exact evidence nav line NOT FOUND. Dump the NAV_ITEMS block and paste it back.")
        raise SystemExit(1)

# 2. Move Hazard Reports to the OVERVIEW category + rename that category
old_hazards = "  { id: 'hazards', label: '2. Hazard Reports', icon: AlertTriangle, category: 'FIELD & HAZARDS' },\n"
new_hazards = "  { id: 'hazards', label: '2. Hazard Reports', icon: AlertTriangle, category: 'OVERVIEW' },\n"
if old_hazards in src:
    src = src.replace(old_hazards, new_hazards, 1)
    changes.append("moved Hazard Reports to 'OVERVIEW' category")
else:
    print("Hazard Reports nav line NOT FOUND.")
    raise SystemExit(1)

# Rename the dashboard's category from 'EXECUTIVE OVERVIEW' to 'OVERVIEW'
old_dashboard = "  { id: 'dashboard', label: '1. Executive Dashboard', icon: LayoutDashboard, category: 'EXECUTIVE OVERVIEW' },\n"
new_dashboard = "  { id: 'dashboard', label: '1. Executive Dashboard', icon: LayoutDashboard, category: 'OVERVIEW' },\n"
if old_dashboard in src:
    src = src.replace(old_dashboard, new_dashboard, 1)
    changes.append("renamed category 'EXECUTIVE OVERVIEW' → 'OVERVIEW'")
else:
    print("Dashboard nav line NOT FOUND.")
    raise SystemExit(1)

# 3. Drop Video import if now unused
video_hits = len(re.findall(r"\bVideo\b", src))
if video_hits == 1:
    # Only the import line remains
    src = re.sub(r"(\n\s*)Video,", "", src, count=1)
    changes.append("removed unused Video import")
elif video_hits == 0:
    changes.append("Video already gone")
else:
    changes.append(f"Video still used ({video_hits} references) — kept")

p.write_text(src, encoding="utf-8")

print("Changes:")
for c in changes:
    print(" -", c)

o, c = src.count("{"), src.count("}")
print(f"\nSidebar.tsx brace balance: {'OK' if o == c else f'MISMATCH ({o} vs {c})'}")