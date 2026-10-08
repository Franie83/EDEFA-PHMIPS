"""Count records per entity type and list users."""
import sqlite3
import json
from pathlib import Path

DB = Path(__file__).parent / "instance" / "ef_phmips.db"

if not DB.exists():
    print(f"ERROR: DB not found at {DB}")
    raise SystemExit(1)

print(f"DB file: {DB}")
print(f"Size:    {DB.stat().st_size} bytes")
print(f"Modified: {__import__('datetime').datetime.fromtimestamp(DB.stat().st_mtime)}")
print()

con = sqlite3.connect(DB)

print("=== Entity counts ===")
rows = con.execute(
    "SELECT entity_type, COUNT(*) FROM records GROUP BY entity_type ORDER BY entity_type"
).fetchall()
for row in rows:
    print(f"  {row[0]:20} {row[1]:5}")
print()

print("=== Users ===")
users = con.execute(
    "SELECT entity_id, data FROM records WHERE entity_type='users' ORDER BY entity_id"
).fetchall()
for eid, raw in users:
    d = json.loads(raw)
    print(f"  {eid:<10}  {d.get('username', '?'):<15} {d.get('role', '?')}")
print()

print("=== Interventions ===")
ints = con.execute(
    "SELECT entity_id, data FROM records WHERE entity_type='interventions' ORDER BY entity_id"
).fetchall()
for eid, raw in ints:
    d = json.loads(raw)
    print(f"  {eid:<14}  status={d.get('approval_status', '?'):<20}  {d.get('title', '')[:50]}")
print()

print("=== Projects (last 6) ===")
projs = con.execute(
    "SELECT entity_id, data FROM records WHERE entity_type='projects' ORDER BY id DESC LIMIT 6"
).fetchall()
for eid, raw in projs:
    d = json.loads(raw)
    print(f"  {eid:<14}  status={d.get('status', '?'):<20}  {d.get('title', '')[:50]}")
print()

con.close()