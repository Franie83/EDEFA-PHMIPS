"""
patch_sidebar_remove_evidence.py
Removes the 'Evidence Repository' sidebar item.
Keeps the /evidence route alive in App.tsx so deep-links and navigate-view
events to 'evidence' still work (just no visible sidebar entry).
"""
import pathlib

p = pathlib.Path("src/components/common/Sidebar.tsx")
src = p.read_text(encoding="utf-8")

# The exact nav item line, verbatim from the file
old_line = """  { id: 'evidence', label: '7. Evidence Repository', icon: Camera, category: 'FIELD & HAZARDS' },\n"""

if old_line not in src:
    if "Evidence Repository" not in src:
        print("Already removed — nothing to do.")
    else:
        print("Exact anchor NOT FOUND. Dump the NAV_ITEMS block and paste it back.")
    raise SystemExit(0)

src = src.replace(old_line, "", 1)
p.write_text(src, encoding="utf-8")

print("Changes:")
print(" - removed 'Evidence Repository' from Sidebar NAV_ITEMS")
print()
print("Note: /evidence route still works in App.tsx — deep links and events to")
print("      'evidence' continue to render the EvidenceRepository view.")

# Sanity: ensure Camera import is still used by something else? If not, add a note.
if "Camera," in src and src.count("Camera") == 1:
    print()
    print("WARNING: 'Camera' icon import is now unused. You can safely remove")
    print("         it from the lucide-react import at the top of the file.")