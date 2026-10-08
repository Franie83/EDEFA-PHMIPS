"""Restrict the report endpoint to Executive + Super Admin only."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "backend" / "app.py"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

OLD = '''@app.post("/api/reports/hazard-intervention-planning")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def report():'''

NEW = '''@app.post("/api/reports/hazard-intervention-planning")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC")
def report():'''

if NEW in text:
    print("Already restricted — skipping.")
    raise SystemExit(0)

if OLD not in text:
    raise SystemExit("Report endpoint not found in expected form. Paste the decorator line.")

text = text.replace(OLD, NEW, 1)
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  /api/reports/hazard-intervention-planning now T1 + T2 only")