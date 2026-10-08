"""
Add the missing approvedInterventions and interventionsLoading state variables
to ProjectModal.tsx.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "projects" / "ProjectModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "const [approvedInterventions" in text:
    print("Already added — skipping.")
    raise SystemExit(0)

# Find the isSubmitting state line
anchor = "const [isSubmitting, setIsSubmitting] = useState(false);"

if anchor not in text:
    raise SystemExit("anchor 'isSubmitting' not found — paste the current file's first 80 lines")

# Insert the two new state declarations right after isSubmitting
new_state = """const [isSubmitting, setIsSubmitting] = useState(false);

  // Executive-Approved interventions available for project registration
  const [approvedInterventions, setApprovedInterventions] = useState<Intervention[]>([]);
  const [interventionsLoading, setInterventionsLoading] = useState(false);"""

text = text.replace(anchor, new_state, 1)

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Added approvedInterventions state")
print("  Added interventionsLoading state")