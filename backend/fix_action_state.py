"""Fix the mangled state declarations at the top of ActionTracking.tsx."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

# The broken block — match everything from the mangled previewItem line
# through the duplicated state declarations
BROKEN_PATTERN = re.compile(
    r"const \[previewItem, setPreviewItem\] = useState<\{ evidence: any;\s*\n"
    r"\s*const \[viewMode, setViewMode\] = useState<'grid' \| 'list'>\('grid'\);\s*\n"
    r"\s*const \[selectedActionForDetail, setSelectedActionForDetail\] = useState<ActionItem \| null>\(null\);\s*\n"
    r"\s*const \[viewMode, setViewMode\] = useState<'grid' \| 'list'>\('grid'\);\s*\n"
    r"\s*const \[selectedActionForDetail, setSelectedActionForDetail\] = useState<ActionItem \| null>\(null\); action: any \} \| null>\(null\);",
    re.MULTILINE,
)

FIXED = "const [previewItem, setPreviewItem] = useState<{ evidence: any; action: any } | null>(null);"

if BROKEN_PATTERN.search(text):
    text = BROKEN_PATTERN.sub(FIXED, text, count=1)
    print("  Replaced mangled state block with single clean line")
elif 'const [previewItem, setPreviewItem] = useState<{ evidence: any; action: any } | null>(null);' in text:
    print("  Already clean — no changes needed")
else:
    # Fallback: find and fix any duplicate viewMode/selectedActionForDetail declarations
    # Remove duplicate lines
    lines = text.split('\n')
    seen_view = False
    seen_selected = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("const [viewMode, setViewMode]"):
            if seen_view:
                print("  Removing duplicate viewMode line")
                continue
            seen_view = True
        if stripped.startswith("const [selectedActionForDetail"):
            if seen_selected:
                print("  Removing duplicate selectedActionForDetail line")
                continue
            seen_selected = True
        new_lines.append(line)
    text = '\n'.join(new_lines)

    # Now fix the mangled previewItem line if it exists
    text = re.sub(
        r"const \[previewItem, setPreviewItem\] = useState<\{ evidence: any;\s*$",
        FIXED,
        text,
        count=1,
        flags=re.MULTILINE,
    )
    # If there's a dangling "action: any } | null>(null);" line
    text = re.sub(r"^\s*action: any \} \| null>\(null\);.*$", "", text, flags=re.MULTILINE)
    print("  Applied fallback fixes")

TARGET.write_text(text, encoding="utf-8")
print()
print(f"Patched {TARGET.name}")