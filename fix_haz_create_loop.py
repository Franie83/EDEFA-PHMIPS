import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")
changes = []

# Find the broken for-loop line and rewrite it fully
old = """ for ev in d.get("evidence") or []:
;audit("CREATE_HAZARD","HAZARD",hid,None,h)"""

# more likely — the body ended up on the next line as part of the audit chain:
old2 = """ for ev in d.get("evidence") or []:
evidence_create(ev,{"hazard_id":hid,"project_id":h.get("linked_project_id") or "","latitude":h["latitude"],"longitude":h["longitude"],"stage_tag":"before"})"""

new = """ for ev in d.get("evidence") or []:
  evidence_create(ev,{"hazard_id":hid,"project_id":h.get("linked_project_id") or "","latitude":h["latitude"],"longitude":h["longitude"],"stage_tag":"before"})"""

if old2 in src:
    src = src.replace(old2, new)
    changes.append("fixed for-loop with indent for body")
else:
    # Try to find the pattern where the for line is followed by semicolon-free body
    # Look at line 373 area
    lines = src.split("\n")
    for i in range(len(lines)):
        if 'for ev in d.get("evidence") or []:' in lines[i]:
            # Check if next line begins with evidence_create
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].strip().startswith("evidence_create"):
                # Fix indentation of the body
                lines[j] = "  " + lines[j].lstrip()
                src = "\n".join(lines)
                changes.append(f"reindented evidence_create at line {j+1}")
                break
    else:
        changes.append("could not locate for-loop")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)

import ast
try:
    ast.parse(src)
    print("\nSYNTAX OK")
except SyntaxError as e:
    print(f"\nSTILL BROKEN at line {e.lineno}: {e.text}")
    print("Paste this output so I can see the exact state:")
    print("  Get-Content backend\\app.py | Select-Object -Skip 368 -First 10")