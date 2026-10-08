"""
Add evidence gallery + upload button + preview lightbox to ActionTracking.tsx.
Also gate the Edit button visibility by role.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "evidence-gallery" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# 1. Extend imports
needed = ["Upload", "FileText", "Image", "Paperclip", "ExternalLink"]
m = re.search(r"import\s*\{([^}]+)\}\s*from\s*'lucide-react'", text)
if m:
    existing = m.group(1)
    missing = [ic for ic in needed if ic not in existing]
    if missing:
        new_import = "import {\n  " + existing.strip().rstrip(",") + ",\n  " + ",\n  ".join(missing) + "\n} from 'lucide-react'"
        text = text[:m.start()] + new_import + text[m.end():]
        print(f"  Added icons: {missing}")

# 2. Add state for evidence upload + preview + role
anchor = "const [editBusy, setEditBusy] = useState(false);"
if anchor not in text:
    raise SystemExit("editBusy anchor not found")

new_state = anchor + """

  // Evidence upload + preview
  const [evidenceForAction, setEvidenceForAction] = useState<ActionItem | null>(null);
  const [evidenceFile, setEvidenceFile] = useState<string>('');
  const [evidenceFileName, setEvidenceFileName] = useState<string>('');
  const [evidenceFileType, setEvidenceFileType] = useState<string>('');
  const [evidenceDescription, setEvidenceDescription] = useState<string>('');
  const [evidenceBusy, setEvidenceBusy] = useState(false);
  const [evidenceError, setEvidenceError] = useState('');
  const [previewItem, setPreviewItem] = useState<{ evidence: any; action: any } | null>(null);

  // Role — set from props or a global context
  const currentRole = (window as any).__EDEFA_ROLE__ || (window as any).currentUser?.role || '';"""

text = text.replace(anchor, new_state, 1)
print("  Added evidence + preview state")

# 3. Add file picker handler + evidence upload handler
anchor2 = "const openEditModal = (action: ActionItem) => {"
if anchor2 not in text:
    raise SystemExit("openEditModal anchor not found")

new_handlers = '''const openEvidenceModal = (action: ActionItem) => {
    setEvidenceForAction(action);
    setEvidenceFile('');
    setEvidenceFileName('');
    setEvidenceFileType('');
    setEvidenceDescription('');
    setEvidenceError('');
  };

  const handleEvidenceFilePick = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      setEvidenceFile(String(reader.result || ''));
      setEvidenceFileName(file.name);
      setEvidenceFileType(file.type);
    };
    reader.readAsDataURL(file);
  };

  const submitEvidence = async () => {
    if (!evidenceForAction || !evidenceFile) {
      setEvidenceError('Please select a file.');
      return;
    }
    setEvidenceBusy(true);
    setEvidenceError('');
    try {
      const { api } = await import('../../services/api.ts');
      const mediaType = evidenceFileType.startsWith('image') ? 'photo' : 'document';
      await api.uploadActionEvidence(evidenceForAction.id, {
        file_name: evidenceFileName,
        file_type: evidenceFileType,
        base64_data: evidenceFile,
        media_type: mediaType,
        description: evidenceDescription || 'Action completion evidence',
        stage_tag: 'after',
      });
      setEvidenceForAction(null);
      window.location.reload();
    } catch (err: any) {
      setEvidenceError(err?.message || 'Upload failed');
    } finally {
      setEvidenceBusy(false);
    }
  };

  const canEditActionMetadata = currentRole === 'SUPER_ADMIN' || currentRole === 'EXECUTIVE';
  const canMarkComplete = (action: ActionItem) => {
    if (currentRole === 'SUPER_ADMIN' || currentRole === 'EXECUTIVE') return true;
    return false; // Staff/Director handled by backend ownership check
  };

  const openEditModal = (action: ActionItem) => {'''

text = text.replace(anchor2, new_handlers, 1)
print("  Added evidence handlers + role-based helpers")

TARGET.write_text(text, encoding="utf-8")
print(f"\nPatched {TARGET.name} (part 1 of 2)")
print()
print("Run add_action_evidence_modal.py next to insert the UI modals.")