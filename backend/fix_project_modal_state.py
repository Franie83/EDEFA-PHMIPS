"""Fix the formData state in ProjectModal.tsx — the earlier patch missed it."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "projects" / "ProjectModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "intervention_id: ''" in text.split("const [isSubmitting")[0]:
    print("Already fixed — skipping.")
    raise SystemExit(0)

# Find the formData useState block
pattern = r"const \[formData, setFormData\] = useState\(\{[\s\S]*?\}\);"

match = re.search(pattern, text)
if not match:
    raise SystemExit("Could not find formData useState block")

old_state = match.group(0)

# Build the new state with intervention_id + Pending Approval
new_state = """const [formData, setFormData] = useState({
    intervention_id: '',
    title: '',
    category: categories[0] || 'Gully Erosion Remediation',
    description: '',
    state: Object.keys(statesAndLgas)[0] || 'Anambra',
    lga: '',
    ward: '',
    community: '',
    site_name: '',
    latitude: 6.2209,
    longitude: 7.0722,
    funding_source: 'Federal Ecological Fund (EPO)',
    approved_amount_ngn: 450000000,
    contract_amount_ngn: 420000000,
    contractor: '',
    implementing_agency: 'Ecological Project Office (EPO)',
    start_date: new Date().toISOString().split('T')[0],
    expected_completion_date: '2026-12-31',
    planned_percentage: 10,
    actual_percentage: 0,
    status: 'Pending Approval' as ProjectStatus,
    remarks: ''
  });"""

text = text[:match.start()] + new_state + text[match.end():]

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Added intervention_id to formData")
print("  Changed default status to 'Pending Approval'")