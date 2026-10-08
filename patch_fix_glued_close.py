"""
patch_fix_glued_close.py  (v2)
Fix: line 551 currently reads '          )})}' — two adjacent conditionals
glued together by the previous patch. Should be a single ')}'.
"""
import pathlib

p = pathlib.Path("src/components/projects/ProjectDetailModal.tsx")
src = p.read_text(encoding="utf-8")

bad = "          )})}\n"
good = "          )}\n"

if bad not in src:
    print("Buggy line NOT FOUND. Current closing block:")
    idx = src.find("{monitoringSubTab === 'before_after'")
    if idx > 0:
        print(src[max(0, idx-200):idx+100])
    else:
        print("Could not find monitoringSubTab === 'before_after' anchor")
    raise SystemExit(1)

count = src.count(bad)
src = src.replace(bad, good, 1)
p.write_text(src, encoding="utf-8")

print("Changes:")
print(" - replaced the glued '          )})}' with '          )}'")
print(" - occurrences found:", count, "| fixed: 1")
opens = src.count("{")
closes = src.count("}")
print()
print("Brace balance:", "OK" if opens == closes else f"MISMATCH ({opens} vs {closes})")