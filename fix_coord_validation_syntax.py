import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")
changes = []

# Fix the public_report for-loop
old_pub_loop = """;put("hazards",h)
 for ev in d.get("evidence") or []:evidence_create(ev,{"hazard_id":hid,"project_id":h.get("linked_project_id") or "","latitude":h["latitude"],"longitude":h["longitude"],"stage_tag":"before"})"""

new_pub_loop = """;put("hazards",h)
 for ev in d.get("evidence") or []:
  evidence_create(ev,{"hazard_id":hid,"project_id":h.get("linked_project_id") or "","latitude":h["latitude"],"longitude":h["longitude"],"stage_tag":"before"})"""

if old_pub_loop in src:
    src = src.replace(old_pub_loop, new_pub_loop)
    changes.append("split hazard_create for-loop onto its own line")

# Same for public_report
old_pub = """ for ev in d.get("evidence") or []:
  evidence_create(ev,{"hazard_id":hid,"latitude":h["latitude"],"longitude":h["longitude"],"stage_tag":"before"});"""
# Not applicable — public_report uses its own line

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)

import ast
try:
    ast.parse(src)
    print("\nSYNTAX OK")
except SyntaxError as e:
    print(f"\nSYNTAX ERROR at line {e.lineno}: {e.text}")
    print("\nFix: open backend/app.py around line", e.lineno, "and put the `for ev` block on its own line with the body indented on the next line.")