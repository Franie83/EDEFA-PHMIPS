import pathlib

p = pathlib.Path("src/components/common/Sidebar.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# Remove the "9. Intervention Planning" nav item
old_item = """  { id: 'interventions', label: '9. Intervention Planning', icon: Compass, category: 'INTERVENTIONS & WORKFLOW' },\n"""
if old_item in src:
    src = src.replace(old_item, "")
    changes.append("removed item 9 (Intervention Planning) from NAV_ITEMS")
else:
    changes.append("item 9 pattern NOT FOUND — check the exact label")

# Now the `current === 'interventions'` / `planning` alias in Sidebar's active check will
# no longer be used. We can leave those safe — they just never fire.

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)