"""
Open /api/reference-data to all authenticated tiers.

Reference data (LGAs, categories) is not sensitive and is needed by
Directors and Staff to file reports and register projects.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "backend" / "app.py"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

OLD = '''@app.get("/api/reference-data")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC")
def ref():return jsonify(db.session.get(Setting,"reference_data").value)'''

NEW = '''@app.get("/api/reference-data")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def ref():return jsonify(db.session.get(Setting,"reference_data").value)'''

if NEW in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

if OLD not in text:
    raise SystemExit("reference-data endpoint not found in expected form")

text = text.replace(OLD, NEW, 1)
TARGET.write_text(text, encoding="utf-8")
print("Patched backend/app.py")
print("  /api/reference-data now readable by all 4 tiers")
print()
print("NEXT: restart Flask for the change to take effect.")