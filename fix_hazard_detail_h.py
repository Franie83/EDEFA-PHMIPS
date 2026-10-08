import pathlib
import re

p = pathlib.Path("src/components/hazards/HazardDetailModal.tsx")
src = p.read_text(encoding="utf-8")

# The only places `hazard.` should be replaced with `h.` are INSIDE the JSX return block.
# Everywhere else (hooks, effects, guards), keep `hazard.`.

# Strategy: split at "return ("
marker = "  return ("
idx = src.find(marker)
if idx == -1:
    print("return ( marker NOT FOUND")
else:
    before = src[:idx]
    after = src[idx:]

    # Revert h. → hazard. in the "before" region
    before = re.sub(r'\bh\.', 'hazard.', before)

    # Also fix `if (!h) return null;` inside before → `if (!hazard) return null;`
    before = before.replace("if (!h) return null;", "if (!hazard) return null;")

    src = before + after
    p.write_text(src, encoding="utf-8")
    print("Reverted h. → hazard. in setup code (before JSX return)")

# Sanity: count remaining h. and hazard. in the file
h_count = len(re.findall(r'\bh\.', src))
hazard_count = len(re.findall(r'\bhazard\.', src))
print(f"\nRemaining h. references: {h_count}")
print(f"Remaining hazard. references: {hazard_count}")