"""
patch_sidebar_remove_fieldops.py
Removes '4. Field Operations' from the Sidebar. Keeps the field-ops route
alive in App.tsx so '+ Add Site' and other internal navigations keep working.
"""
import pathlib
import re

p = pathlib.Path("src/components/common/Sidebar.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Remove the nav item
old_nav = "  { id: 'field-ops', label: '4. Field Operations', icon: MapPin, category: 'FIELD & HAZARDS' },\n"
if old_nav in src:
    src = src.replace(old_nav, "", 1)
    changes.append("removed '4. Field Operations' from NAV_ITEMS")
else:
    print("field-ops nav item NOT FOUND — checking if already removed")
    if "id: 'field-ops'" not in src:
        changes.append("field-ops nav item already absent")
    else:
        raise SystemExit(1)

# 2. Remove the "isActive" clause for field-ops
old_active_clause = """                  (item.id === 'field-ops' && (current === 'sites' || current === 'visits' || current === 'field_visits' || current === 'monitoring')) ||\n"""
if old_active_clause in src:
    src = src.replace(old_active_clause, "", 1)
    changes.append("removed field-ops isActive clause")
elif "item.id === 'field-ops'" in src:
    # try multiline-tolerant variant
    pattern = re.compile(
        r"^\s*\(item\.id === 'field-ops' && \(current === 'sites' \|\| current === 'visits' \|\| current === 'field_visits' \|\| current === 'monitoring'\)\) \|\|\s*\n",
        re.MULTILINE,
    )
    src, n = pattern.subn("", src)
    if n:
        changes.append("removed field-ops isActive clause (regex)")
    else:
        changes.append("WARNING: could not remove isActive clause — check manually")

# 3. Drop MapPin from imports if no longer used
# MapPin is used only by the field-ops nav item.
map_pin_hits = len(re.findall(r"\bMapPin\b", src))
if map_pin_hits == 1:
    # Only the import remains — remove it
    src = re.sub(r"(\n\s*)MapPin,", "", src, count=1)
    changes.append("removed unused MapPin import")
elif map_pin_hits == 0:
    changes.append("MapPin already gone")
else:
    changes.append(f"MapPin still used ({map_pin_hits} references) — kept in imports")

p.write_text(src, encoding="utf-8")

print("Changes:")
for c in changes:
    print(" -", c)

o, c = src.count("{"), src.count("}")
print(f"\nSidebar.tsx brace balance: {'OK' if o == c else f'MISMATCH ({o} vs {c})'}")