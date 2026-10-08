"""
Restore handleSubmit in ActionTracking.tsx — it was accidentally removed by
the filter patch's regex.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "const handleSubmit" in text:
    print("handleSubmit already present — skipping.")
    raise SystemExit(0)

# Insert handleSubmit just before `return (`
marker = "\n  return ("
idx = text.find(marker)
if idx == -1:
    raise SystemExit("Could not find 'return (' in the file")

restored = '''
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onCreateAction(formData);
    setIsModalOpen(false);
  };

'''

text = text[:idx] + restored + text[idx:]
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Restored handleSubmit function")