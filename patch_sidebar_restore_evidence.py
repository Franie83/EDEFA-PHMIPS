"""
patch_sidebar_restore_evidence.py
Restores 'Evidence & Media Repository' to the sidebar with a Video icon,
underscoring its role as the primary archive for video evidence.
"""
import pathlib

p = pathlib.Path("src/components/common/Sidebar.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Ensure Video is imported (Camera may still be there from before — leave it if
#    unused, or clean both up below)
if "  Video," not in src and "Video," not in src.split("from 'lucide-react'")[0]:
    if "  Camera," in src:
        # Replace Camera with Video in the import list
        src = src.replace("  Camera,", "  Video,", 1)
        changes.append("swapped Camera → Video in lucide import")
    else:
        # Insert Video before CheckSquare
        anchor = "  CheckSquare,"
        if anchor in src:
            src = src.replace(anchor, "  Video,\n" + anchor, 1)
            changes.append("added Video to lucide import")
        else:
            print("WARN: could not find lucide import anchor — add Video manually")
else:
    changes.append("Video already imported")

# 2. Restore the nav item, renamed + video icon
if "id: 'evidence'" in src:
    print("Evidence nav item already present — nothing to add.")
else:
    # Original anchor was: after 'field-ops' line, before blank line + 'projects'
    anchor_ops = "  { id: 'field-ops', label: '4. Field Operations', icon: MapPin, category: 'FIELD & HAZARDS' },\n"
    new_evidence = "  { id: 'evidence', label: '7. Evidence & Media Repository', icon: Video, category: 'FIELD & HAZARDS' },\n"
    if anchor_ops not in src:
        print("field-ops anchor NOT FOUND — paste the NAV_ITEMS block and I'll adjust.")
        raise SystemExit(1)
    src = src.replace(anchor_ops, anchor_ops + new_evidence, 1)
    changes.append("restored Evidence Repository with Video icon + renamed label")

p.write_text(src, encoding="utf-8")

print("Changes:")
for c in changes:
    print(" -", c)

# Brace balance sanity
o, c = src.count("{"), src.count("}")
print(f"\nSidebar.tsx brace balance: {'OK' if o == c else f'MISMATCH ({o} vs {c})'}")