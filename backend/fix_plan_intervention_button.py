"""
Rewire the 'Plan Engineering Intervention' button in HazardDetailModal.tsx
to call onPlanIntervention if available, falling back to onInterventionClick.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "hazards" / "HazardDetailModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

# Already fixed?
if "onPlanIntervention ? onPlanIntervention(hazard)" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# Find the button. It probably looks like:
#   onClick={() => onInterventionClick(hazard)}
# or a variation with whitespace
import re

patterns = [
    r"onClick=\{\(\) => onInterventionClick\(hazard\)\}",
    r"onClick=\{\(\) => onInterventionClick\(hazard as Hazard\)\}",
    r"onClick=\{\(\)\s*=>\s*onInterventionClick\(hazard\)\}",
]

matched = False
for pattern in patterns:
    if re.search(pattern, text):
        text = re.sub(
            pattern,
            "onClick={() => onPlanIntervention ? onPlanIntervention(hazard) : onInterventionClick(hazard)}",
            text,
            count=1,
        )
        matched = True
        print(f"  Rewired via pattern: {pattern}")
        break

if not matched:
    # Fallback: find any onClick with onInterventionClick(hazard)
    idx = text.find("onInterventionClick(hazard)")
    if idx == -1:
        raise SystemExit(
            "Could not find onInterventionClick(hazard) in the file. "
            "Paste the section around the 'Plan Engineering Intervention' button."
        )
    # Replace the whole onClick expression containing it
    # Find the opening "onClick={"
    before = text.rfind("onClick={", 0, idx)
    if before == -1:
        raise SystemExit("Could not find onClick={ before the handler")
    # Find the matching "}" — crude but works for single-expression
    after = text.find("}", idx)
    if after == -1:
        raise SystemExit("Could not find closing } for onClick")
    old_expr = text[before:after + 1]
    new_expr = "onClick={() => onPlanIntervention ? onPlanIntervention(hazard) : onInterventionClick(hazard)}"
    text = text.replace(old_expr, new_expr, 1)
    print(f"  Rewired via fallback: replaced {old_expr!r}")

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")