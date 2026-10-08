"""
Patch src/components/hazards/HazardDetailModal.tsx to add Edit and Delete
buttons. Buttons are only shown when the current user has canEdit / canDelete.
Delete uses window.confirm() for safety.

Idempotent.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "hazards" / "HazardDetailModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "onEdit" in text and "onDelete" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# --- Patch 1: add icons to import ---
old_icon_import = """  ExternalLink,
  Layers
} from 'lucide-react';"""
new_icon_import = """  ExternalLink,
  Layers,
  Pencil,
  Trash2
} from 'lucide-react';"""
if old_icon_import not in text:
    raise SystemExit("Icon import not found — aborting.")
text = text.replace(old_icon_import, new_icon_import)

# --- Patch 2: add canEdit import ---
old_type_import = "import { Hazard, Evidence, ActionItem, Intervention } from '../../types/index.ts';"
new_type_import = "import { Hazard, Evidence, ActionItem, Intervention } from '../../types/index.ts';\nimport { canEdit as canEditFn, canDelete as canDeleteFn } from '../../types/tiers.ts';"
if old_type_import not in text:
    raise SystemExit("Type import not found — aborting.")
text = text.replace(old_type_import, new_type_import)

# --- Patch 3: extend props interface ---
old_props = """interface HazardDetailModalProps {
  hazard: Hazard | null;
  onClose: () => void;
  onVerifyClick: (hazard: Hazard) => void;
  onAssessClick: (hazard: Hazard) => void;
  onInterventionClick: (hazard: Hazard) => void;
  onNavigateToMap: (lat: number, lng: number) => void;
}"""
new_props = """interface HazardDetailModalProps {
  hazard: Hazard | null;
  onClose: () => void;
  onVerifyClick: (hazard: Hazard) => void;
  onAssessClick: (hazard: Hazard) => void;
  onInterventionClick: (hazard: Hazard) => void;
  onNavigateToMap: (lat: number, lng: number) => void;
  onEdit?: (hazard: Hazard) => void;
  onDelete?: (hazard: Hazard) => void;
  currentRole?: string;
}"""
if old_props not in text:
    raise SystemExit("Props interface not found — aborting.")
text = text.replace(old_props, new_props)

# --- Patch 4: extend destructure + compute permissions ---
old_dest = """export const HazardDetailModal: React.FC<HazardDetailModalProps> = ({
  hazard,
  onClose,
  onVerifyClick,
  onAssessClick,
  onInterventionClick,
  onNavigateToMap
}) => {
  const [activeMedia, setActiveMedia] = useState<Evidence | null>(null);

  if (!hazard) return null;"""
new_dest = """export const HazardDetailModal: React.FC<HazardDetailModalProps> = ({
  hazard,
  onClose,
  onVerifyClick,
  onAssessClick,
  onInterventionClick,
  onNavigateToMap,
  onEdit,
  onDelete,
  currentRole
}) => {
  const [activeMedia, setActiveMedia] = useState<Evidence | null>(null);

  if (!hazard) return null;

  const userCanEdit = canEditFn(currentRole);
  const userCanDelete = canDeleteFn(currentRole);

  const handleDeleteClick = () => {
    if (!onDelete) return;
    const confirmed = window.confirm(
      `Delete hazard ${hazard.id}?\\n\\n"${hazard.title}"\\n\\nThis cannot be undone. The deletion will be permanently recorded in the audit log.`
    );
    if (confirmed) onDelete(hazard);
  };"""
if old_dest not in text:
    raise SystemExit("Component destructure not found — aborting.")
text = text.replace(old_dest, new_dest)

# --- Patch 5: add Edit and Delete buttons in header ---
# Insert them right before the existing close button.
# We look for the X close button inside the header.
old_close = """          </div>
          <button
            onClick={onClose}"""
new_close = """          </div>
          <div className="flex items-center space-x-1.5">
            {userCanEdit && onEdit && (
              <button
                onClick={() => onEdit(hazard)}
                title="Edit this hazard (Super Admin / Executive only)"
                className="p-1.5 rounded-lg bg-emerald-800/60 hover:bg-emerald-700 text-emerald-100 transition-colors inline-flex items-center space-x-1"
              >
                <Pencil className="w-4 h-4" />
                <span className="hidden sm:inline text-[11px] font-semibold">Edit</span>
              </button>
            )}
            {userCanDelete && onDelete && (
              <button
                onClick={handleDeleteClick}
                title="Delete this hazard (Super Admin / Executive only)"
                className="p-1.5 rounded-lg bg-rose-900/60 hover:bg-rose-800 text-rose-100 transition-colors inline-flex items-center space-x-1"
              >
                <Trash2 className="w-4 h-4" />
                <span className="hidden sm:inline text-[11px] font-semibold">Delete</span>
              </button>
            )}
            <button
              onClick={onClose}"""
if old_close not in text:
    raise SystemExit("Close button anchor not found — aborting.")
text = text.replace(old_close, new_close, 1)

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  - Added Pencil, Trash2 icons")
print("  - Added canEdit, canDelete imports")
print("  - Added onEdit, onDelete, currentRole props")
print("  - Added userCanEdit, userCanDelete derived flags")
print("  - Added handleDeleteClick with confirmation")
print("  - Added Edit and Delete buttons in header")