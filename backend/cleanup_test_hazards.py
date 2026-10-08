"""Delete test hazards and restore the seed set. Then verify nxt works."""
import sqlite3
import json
from pathlib import Path

DB = Path(__file__).parent / "instance" / "ef_phmips.db"
con = sqlite3.connect(DB)

# 1. Show current state
print("BEFORE cleanup:")
rows = con.execute(
    "SELECT id, entity_id, data FROM records WHERE entity_type = 'hazards' ORDER BY id"
).fetchall()
for row_id, eid, data in rows:
    d = json.loads(data)
    print(f"  row {row_id:<4} {eid:<14} {d.get('title')}")

# 2. Delete test records
TEST_TITLES = {
    "Director hazard",
    "Counter test",
    "Final test",
    "Post-fix test",
    "Test",
    "Director-created hazard",
}
victims = []
for row_id, eid, data in rows:
    d = json.loads(data)
    if d.get("title") in TEST_TITLES:
        victims.append((row_id, eid, d.get("title")))

print(f"\nDeleting {len(victims)} test hazard(s)...")
for v in victims:
    con.execute("DELETE FROM records WHERE id = ?", (v[0],))
con.commit()

# 3. Show remaining
print("\nAFTER cleanup:")
for row_id, eid, data in con.execute(
    "SELECT id, entity_id, data FROM records WHERE entity_type = 'hazards' ORDER BY entity_id"
).fetchall():
    d = json.loads(data)
    print(f"  row {row_id:<4} {eid:<14} {d.get('title')}")

# 4. Clear counters so nxt recomputes from records on next create
con.execute("DELETE FROM counters WHERE key IN ('HAZ', 'projects')")
con.commit()

con.close()
print("\nDone. Counters reset. Next hazard should be EH-2026-007.")