"""Re-add viewMode and selectedActionForDetail state declarations."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

has_view = "const [viewMode, setViewMode]" in text
has_selected = "const [selectedActionForDetail, setSelectedActionForDetail]" in text

print(f"  viewMode declared: {has_view}")
print(f"  selectedActionForDetail declared: {has_selected}")

if has_view and has_selected:
    print("  Both present — nothing to do.")
    raise SystemExit(0)

anchor = "const [previewItem, setPreviewItem] = useState<{ evidence: any; action: any } | null>(null);"
if anchor not in text:
    raise SystemExit("Could not find previewItem anchor")

additions = ""
if not has_view:
    additions += "\n  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');"
    print("  Adding viewMode declaration")
if not has_selected:
    additions += "\n  const [selectedActionForDetail, setSelectedActionForDetail] = useState<ActionItem | null>(null);"
    print("  Adding selectedActionForDetail declaration")

text = text.replace(anchor, anchor + additions, 1)
TARGET.write_text(text, encoding="utf-8")
print()
print(f"Patched {TARGET.name}")