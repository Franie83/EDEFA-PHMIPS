"""
Correctly rewire the "Plan Engineering Intervention" button.
Restores the modal-close handler that was damaged, and rewires
the actual Plan button to call onPlanIntervention.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "hazards" / "HazardDetailModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

# -------- STEP 1: Fix the damaged close+intervention handler --------
# It currently reads:
#   onClick={() => onPlanIntervention ? onPlanIntervention(hazard) : onInterventionClick(hazard)}
# in a button whose body also had `onClose()`.

# Find the damaged onClick and restore the correct close + navigate behavior
damaged = "onClick={() => onPlanIntervention ? onPlanIntervention(hazard) : onInterventionClick(hazard)}"

# Determine if this damaged line is on the CLOSE button (has onClose nearby) or the Plan button
# We'll look at each occurrence in context.

occurrences = [m.start() for m in re.finditer(re.escape(damaged), text)]
print(f"Found {len(occurrences)} occurrence(s) of the damaged handler.")

# Look at the button text near each occurrence to identify which is which
for i, pos in enumerate(occurrences):
    # Look 500 chars after for "Close" text or "Plan Engineering Intervention"
    after = text[pos:pos+800]
    before = text[max(0, pos-400):pos]

    is_close = "Close\n" in after or ">Close<" in after or "Close</button>" in after
    is_plan = "Plan Engineering Intervention" in after or "Plan Engineering Intervention" in before
    print(f"  Occurrence {i}: close={is_close}, plan={is_plan}")

# -------- STEP 2: Restore the close button --------
# The Close button (with onClose() in it originally) was changed from:
#   onClick={() => { onClose(); onInterventionClick(hazard); }}
# to the damaged version.

# We restore it.
close_handler_old = damaged
close_handler_new = "onClick={() => { onClose(); onInterventionClick(hazard); }}"

# Only restore the FIRST occurrence that was originally the close-button
# (we can't distinguish by content alone, so we look for "Close" text nearby)

def restore_close_button(text):
    """Find the button whose onClick was mangled and restore it."""
    # Look for the pattern: the damaged handler followed by a button that says Close
    for match in re.finditer(re.escape(close_handler_old), text):
        pos = match.start()
        # Check 800 chars after for "Close"
        window = text[pos:pos+800]
        if re.search(r">\s*Close\s*<", window):
            # This is the close button — restore it
            text = text[:pos] + close_handler_new + text[pos + len(close_handler_old):]
            return text, True
    return text, False

text, restored = restore_close_button(text)
if restored:
    print("  Restored the 'Close + navigate' handler")
else:
    print("  WARNING: Could not find the close button to restore")

# -------- STEP 3: Rewire the actual "Plan Engineering Intervention" button --------
# Now find the button whose text is "Plan Engineering Intervention" and
# rewire its onClick.

def rewire_plan_button(text):
    # Look for onClick={() => onInterventionClick(hazard)} immediately before
    # the Plan Engineering Intervention button text.
    patterns = [
        # Variant A: single expression
        (r"onClick=\{\(\) => onInterventionClick\(hazard\)\}",
         "onClick={() => onPlanIntervention ? onPlanIntervention(hazard) : onInterventionClick(hazard)}"),
        # Variant B: close+intervention (still not fixed)
        (r"onClick=\{\(\) => \{\s*onClose\(\);\s*onInterventionClick\(hazard\);\s*\}\}",
         "onClick={() => onPlanIntervention ? onPlanIntervention(hazard) : (onClose(), onInterventionClick(hazard))}"),
    ]
    for pat, repl in patterns:
        for match in re.finditer(pat, text):
            pos = match.start()
            # Check 400 chars after for "Plan Engineering Intervention"
            window = text[pos:pos+400]
            if "Plan Engineering Intervention" in window:
                text = text[:pos] + repl + text[pos + len(match.group(0)):]
                print(f"  Rewired Plan button via pattern: {pat[:50]}...")
                return text, True
    return text, False

text, rewired = rewire_plan_button(text)
if rewired:
    print("  Plan Engineering Intervention button rewired")
else:
    print("  WARNING: Could not find Plan Engineering Intervention button")

TARGET.write_text(text, encoding="utf-8")
print()
print(f"Saved {TARGET.name}")