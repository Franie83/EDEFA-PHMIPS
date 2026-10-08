"""Fix the duplicate closing brace on the Plan Engineering Intervention button."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "hazards" / "HazardDetailModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

# The broken line
BROKEN = "onClick={() => onPlanIntervention ? onPlanIntervention(hazard) : (onClose(), onInterventionClick(hazard))}}"

# The correct line — proper arrow function, single closing brace
FIXED = "onClick={() => { if (onPlanIntervention) { onClose(); onPlanIntervention(hazard); } else { onClose(); onInterventionClick(hazard); } }}"

if FIXED in text:
    print("Already fixed — skipping.")
    raise SystemExit(0)

if BROKEN not in text:
    # Try alternative broken forms
    BROKEN_ALT = "onClick={() => onPlanIntervention ? onPlanIntervention(hazard) : (onClose(), onInterventionClick(hazard))}"
    if BROKEN_ALT + "}" in text:
        text = text.replace(BROKEN_ALT + "}", FIXED, 1)
        print("Fixed via ALT pattern (with duplicate }).")
    elif BROKEN_ALT in text:
        text = text.replace(BROKEN_ALT, FIXED, 1)
        print("Fixed via ALT pattern.")
    else:
        raise SystemExit(
            "Could not find the broken button onClick. "
            "Open the file and search for 'onPlanIntervention ?' to fix manually."
        )
else:
    text = text.replace(BROKEN, FIXED, 1)
    print("Fixed via primary pattern.")

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print()
print("The button now:")
print("  - Calls onClose() in both branches (closes the modal)")
print("  - If onPlanIntervention provided: opens the intervention form")
print("  - Else: falls back to the old navigate-to-Module-9 behavior")