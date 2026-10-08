import pathlib
import re

p = pathlib.Path("src/components/hazards/HazardDetailModal.tsx")
src = p.read_text(encoding="utf-8")

# Split at the "return (" marker — everything before is setup, after is JSX
marker = "  return ("
idx = src.find(marker)
if idx == -1:
    print("return ( marker NOT FOUND")
else:
    before = src[:idx]
    after = src[idx:]

    # In the JSX portion, replace `hazard.` with `h.` but not:
    # - `hazard={...}` (JSX prop)
    # - `fullHazard`, `setFullHazard` (identifiers)
    # Use word boundary to avoid matching sub-strings
    after_fixed = re.sub(r'\bhazard\.', 'h.', after)

    # Handle the fallback for `<HazardDetailModal hazard={...}>` style props just in case
    # (there aren't any in the JSX; the prop is passed from parent)
    src = before + after_fixed
    p.write_text(src, encoding="utf-8")
    print("Replaced hazard. with h. in JSX portion")

    # Count remaining references for sanity
    remaining = len(re.findall(r'\bhazard\.', src[idx:]))
    print(f"Remaining 'hazard.' references: {remaining}")