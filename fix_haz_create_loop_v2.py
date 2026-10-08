import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

# Join the two broken lines back into one
# The current state has:
#    for ev in d.get("evidence") or
#    []:evidence_create(...)
# (with whatever indentation/line breaks)

# Easiest approach: find the "for ev in d.get(\"evidence\") or" substring
# and rebuild the line from there.

marker = 'for ev in d.get("evidence") or'
idx = src.find(marker)
if idx == -1:
    print("for ev marker NOT FOUND")
else:
    # Find the end of this logical statement — the closing `)` of evidence_create
    # Look for the next `)` followed by a newline or `;` or `\n` (something ending the call)
    # Simplest: find the next occurrence of `"stage_tag":"before"})` after idx
    end_marker = '"stage_tag":"before"})'
    end_idx = src.find(end_marker, idx)
    if end_idx == -1:
        print("end marker NOT FOUND")
    else:
        end_idx += len(end_marker)
        # Reconstruct the full single-line for-loop
        fixed_line = 'for ev in d.get("evidence") or []:evidence_create(ev,{"hazard_id":hid,"project_id":h.get("linked_project_id") or "","latitude":h["latitude"],"longitude":h["longitude"],"stage_tag":"before"})'
        src = src[:idx] + fixed_line + src[end_idx:]
        p.write_text(src, encoding="utf-8")
        print("Rejoined for-loop into single line")

import ast
try:
    ast.parse(src)
    print("\nSYNTAX OK")
except SyntaxError as e:
    print(f"\nSTILL BROKEN at line {e.lineno}: {e.text}")
    print("\nPaste this to see the current state:")
    print("  Get-Content backend\\app.py | Select-Object -Skip 366 -First 8")