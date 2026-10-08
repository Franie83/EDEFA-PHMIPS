"""
Convert Action Tracking from a list view to a grid of square cards.
Clicking a card opens a detail modal with full content and all buttons.
Adds a Grid/List toggle.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "viewMode" in text and "action-detail-modal" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# ============================================================
# 1. Add viewMode + selectedActionForDetail state
# ============================================================
anchor = "const [previewItem, setPreviewItem] = useState"
idx = text.find(anchor)
if idx == -1:
    raise SystemExit("previewItem state not found")

end_of_state = text.find(";", idx) + 1
new_state = "\n  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');\n  const [selectedActionForDetail, setSelectedActionForDetail] = useState<ActionItem | null>(null);"

text = text[:end_of_state] + new_state + text[end_of_state:]
print("  Added viewMode + selectedActionForDetail state")

TARGET.write_text(text, encoding="utf-8")
print()
print(f"Patched {TARGET.name} (part 1 of 3)")
print("Now run part 2: convert_actions_to_grid_p2.py")