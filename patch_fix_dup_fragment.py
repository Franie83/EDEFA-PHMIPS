"""
patch_fix_dup_fragment.py  (v2)
Removes the duplicated </> that step 7 of the map-links patch inserted.
The two </> lines have different indentation (12 spaces then 10 spaces).
"""
import pathlib
import re

p = pathlib.Path("src/components/projects/ProjectDetailModal.tsx")
src = p.read_text(encoding="utf-8")

# Match: any two consecutive </> lines, possibly with different indentation,
# followed by a line containing only `)}`.
pattern = re.compile(
    r"^([ \t]*)</>\s*\n([ \t]*)</>\s*\n([ \t]*\)\})\s*\n",
    re.MULTILINE
)

m = pattern.search(src)
if not m:
    print("Buggy double-</> pattern NOT FOUND.")
    print("Dump lines 545-556 and I'll target the exact bytes.")
    raise SystemExit(1)

# Keep the SECOND </> and its trailing )} — replace both with a single </>
indent_first = m.group(1)
indent_second = m.group(2)
indent_close = m.group(3)
replacement = f"{indent_first}</>\n{indent_close})}}\n"

before = src
src = src[:m.start()] + replacement + src[m.end():]

if src == before:
    print("Replacement made no change — aborting.")
    raise SystemExit(1)

p.write_text(src, encoding="utf-8")

print("Changes:")
print(f" - removed duplicated </> (kept the first at indent {len(indent_first)}, "
      f"dropped the second at indent {len(indent_second)})")
opens = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")