"""
Fix the mangled dropdown in BeforeAfterMonitoring.tsx.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "monitoring" / "BeforeAfterMonitoring.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

# The broken pattern
BROKEN = """          })}
</select>"""

FIXED = """          })}
        </select>"""

if BROKEN in text:
    text = text.replace(BROKEN, FIXED, 1)
    print("  Fixed closing tag spacing")
else:
    print("  WARNING: exact broken pattern not found")

# Also look for the mangled `})}</select>` on a single line
BROKEN2 = "})}</select>"
if BROKEN2 in text:
    text = text.replace(BROKEN2, "})}\n        </select>", 1)
    print("  Fixed single-line mangled closing")

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")