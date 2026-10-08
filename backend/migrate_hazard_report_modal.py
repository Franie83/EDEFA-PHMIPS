"""
Patch src/components/hazards/HazardReportModal.tsx to support edit mode.
When `editHazard` prop is provided, the modal pre-fills with that hazard's
data and switches the submit button to "Save Changes".

Idempotent — safe to run multiple times.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "hazards" / "HazardReportModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "editHazard" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# --- Patch 1: extend props interface ---
old_props = """interface HazardReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (formData: any) => Promise<void>;
  statesAndLgas: Record<string, string[]>;
  categories: string[];
}"""

new_props = """interface HazardReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (formData: any) => Promise<void>;
  statesAndLgas: Record<string, string[]>;
  categories: string[];
  editHazard?: Hazard | null;
}"""

if old_props not in text:
    raise SystemExit("Props interface not found — aborting.")
text = text.replace(old_props, new_props)

# --- Patch 2: extend destructure ---
old_dest = """export const HazardReportModal: React.FC<HazardReportModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories
}) => {"""

new_dest = """export const HazardReportModal: React.FC<HazardReportModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories,
  editHazard
}) => {
  const isEditMode = Boolean(editHazard);"""

if old_dest not in text:
    raise SystemExit("Component signature not found — aborting.")
text = text.replace(old_dest, new_dest)

# --- Patch 3: add useEffect that loads editHazard into formData ---
# Insert right after the useState for formData is closed.
marker = "  const [evidenceFiles, setEvidenceFiles] = useState<any[]>([]);"
effect = """

  // Load hazard into form when entering edit mode
  useEffect(() => {
    if (!editHazard || !isOpen) return;
    setFormData({
      title: editHazard.title || '',
      category: editHazard.category || categories[0] || 'Gully Erosion',
      hazard_type: (editHazard as any).hazard_type || '',
      description: editHazard.description || '',
      date_observed: editHazard.date_observed || new Date().toISOString().split('T')[0],
      state: editHazard.state || Object.keys(statesAndLgas)[0] || 'Edo',
      lga: editHazard.lga || '',
      ward: editHazard.ward || '',
      community: editHazard.community || '',
      address_description: editHazard.address_description || '',
      latitude: editHazard.latitude ?? 6.2209,
      longitude: editHazard.longitude ?? 7.0722,
      estimated_affected_area_sqm: editHazard.estimated_affected_area_sqm ?? 5000,
      estimated_affected_population: editHazard.estimated_affected_population ?? 500,
      estimated_affected_assets: editHazard.estimated_affected_assets || '',
      potential_impact: editHazard.potential_impact || '',
      severity: (editHazard.severity || 'HIGH') as HazardSeverity,
      urgency: (editHazard.urgency || 'HIGH') as HazardUrgency,
      reporter_name: editHazard.reporter_name || '',
      reporter_type: ((editHazard as any).reporter_type || 'FIELD_OFFICER') as any,
      reporter_contact: editHazard.reporter_contact || '',
      is_recurring: (editHazard as any).is_recurring ?? false,
      recurring_count: (editHazard as any).recurring_count ?? 1,
    });
  }, [editHazard, isOpen]);
"""

if marker not in text:
    raise SystemExit("useState marker not found — aborting.")
text = text.replace(marker, marker + effect, 1)

# --- Patch 4: submit button label ---
old_btn = "{isSubmitting ? 'Registering...' : 'Register Hazard Report'}"
new_btn = "{isSubmitting ? (isEditMode ? 'Saving...' : 'Registering...') : (isEditMode ? 'Save Changes' : 'Register Hazard Report')}"

if old_btn not in text:
    raise SystemExit("Submit button label not found — aborting.")
text = text.replace(old_btn, new_btn)

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  - Added editHazard prop")
print("  - Added isEditMode flag")
print("  - Added useEffect to pre-fill form")
print("  - Submit button label now switches between Register / Save")