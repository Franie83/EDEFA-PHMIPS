"""
1. Replace the 'Mark Completed' button with one that:
   - If no evidence exists → opens the Upload Evidence modal
   - If evidence exists → marks complete
2. Add error handling to the button clicks
3. Also handle 'Verify & Close'
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "handleMarkCompleted" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# ============================================================
# 1. Add handleMarkCompleted + handleVerifyClose helpers
# ============================================================
anchor = "const openEvidenceModal = (action: ActionItem) => {"
if anchor not in text:
    raise SystemExit("openEvidenceModal anchor not found")

helpers = '''const handleMarkCompleted = async (action: ActionItem) => {
    const evidence = (action as any).evidence_files || [];
    if (evidence.length === 0) {
      // No evidence yet — open the upload modal instead
      const proceed = window.confirm(
        'Evidence is required to mark this action complete.\\n\\nDo you want to upload evidence now?'
      );
      if (proceed) openEvidenceModal(action);
      return;
    }
    try {
      await onUpdateAction(action.id, { status: 'Completed', progress_percentage: 100 });
    } catch (err: any) {
      alert(`Failed to mark complete: ${err?.message || 'Unknown error'}`);
    }
  };

  const handleVerifyClose = async (action: ActionItem) => {
    try {
      await onUpdateAction(action.id, {
        status: 'Verified',
        verified_by: 'Engr. Director Audits',
      });
    } catch (err: any) {
      alert(`Failed to verify: ${err?.message || 'Unknown error'}`);
    }
  };

  const openEvidenceModal = (action: ActionItem) => {'''

text = text.replace(anchor, helpers, 1)
print("  Added handleMarkCompleted + handleVerifyClose helpers")

# ============================================================
# 2. Replace the button onClick handlers
# ============================================================
old_mark = "onClick={() => onUpdateAction(item.id, { status: 'Completed', progress_percentage: 100 })}"
new_mark = "onClick={() => handleMarkCompleted(item)}"
if old_mark in text:
    text = text.replace(old_mark, new_mark, 1)
    print("  Rewired Mark Completed → handleMarkCompleted")
else:
    print("  WARNING: could not find Mark Completed onClick")

old_verify = "onClick={() => onUpdateAction(item.id, { status: 'Verified', verified_by: 'Engr. Director Audits' })}"
new_verify = "onClick={() => handleVerifyClose(item)}"
if old_verify in text:
    text = text.replace(old_verify, new_verify, 1)
    print("  Rewired Verify & Close → handleVerifyClose")
else:
    print("  WARNING: could not find Verify & Close onClick")

TARGET.write_text(text, encoding="utf-8")
print()
print(f"Patched {TARGET.name}")