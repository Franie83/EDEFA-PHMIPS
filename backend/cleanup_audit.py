"""
One-shot cleanup: remove test-created audit entries and stale test hazards.

Removes:
  1. Test hazards titled "Counter test", "Final test", "Director hazard",
     "Director created", "Staff created", "Test", "Counter verify",
     "Post-fix test", "Director-created hazard"
  2. Audit log entries for those hazards
  3. Collapses stale CREATE_HAZARD entries for EH-2026-001

Preserves:
  - Legitimate seed hazards (EH-2026-002 through EH-2026-006)
  - All SWITCH_ACTIVE_ROLE, CREATE_PROJECT, ASSESS_HAZARD, VERIFY_HAZARD,
    PUBLIC_SUBMIT_HAZARD entries
  - All non-test EDIT_HAZARD and DELETE_HAZARD entries

Idempotent — safe to run multiple times.
"""

import sqlite3
import json
from pathlib import Path

DB = Path(__file__).parent / "instance" / "ef_phmips.db"
if not DB.exists():
    raise SystemExit(f"Database not found: {DB}")

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

TEST_TITLES = {
    "Counter test",
    "Final test",
    "Director hazard",
    "Director created",
    "Staff created",
    "Test",
    "Counter verify",
    "Post-fix test",
    "Director-created hazard",
}

# ============================================================
# PHASE 1 — identify test hazards
# ============================================================
print("=" * 60)
print("PHASE 1: Identify test hazards")
print("=" * 60)

test_hazard_ids = []
for row in con.execute(
    "SELECT id, entity_id, data FROM records WHERE entity_type='hazards'"
).fetchall():
    d = json.loads(row["data"])
    title = d.get("title", "")
    if title in TEST_TITLES:
        test_hazard_ids.append(row["entity_id"])
        print(f"  MARK DELETE: {row['entity_id']:<14} {title}")

print(f"\nFound {len(test_hazard_ids)} test hazard(s).\n")

# ============================================================
# PHASE 2 — delete test hazards
# ============================================================
print("=" * 60)
print("PHASE 2: Delete test hazards")
print("=" * 60)

for eid in test_hazard_ids:
    con.execute(
        "DELETE FROM records WHERE entity_type='hazards' AND entity_id=?",
        (eid,),
    )
    print(f"  Deleted hazard {eid}")
con.commit()

# ============================================================
# PHASE 3 — clean audit log
# ============================================================
print()
print("=" * 60)
print("PHASE 3: Clean audit log")
print("=" * 60)

audit_rows = con.execute(
    "SELECT id, entity_id, data FROM records WHERE entity_type='audit_logs'"
).fetchall()

to_delete_audit = []
for row in audit_rows:
    d = json.loads(row["data"])
    action = d.get("action", "")
    entity_id = d.get("entity_id", "")

    if entity_id in test_hazard_ids and action in {
        "CREATE_HAZARD",
        "EDIT_HAZARD",
        "DELETE_HAZARD",
        "VERIFY_HAZARD",
        "ASSESS_HAZARD",
        "RECOMMEND_INTERVENTION",
    }:
        to_delete_audit.append((row["id"], f"{action} {entity_id}"))
        continue

    if action == "CREATE_HAZARD" and entity_id == "EH-2026-001":
        title = (d.get("new_value") or {}).get("title", "")
        if title in TEST_TITLES:
            to_delete_audit.append(
                (row["id"], f"stale CREATE_HAZARD {entity_id} — {title}")
            )

print(f"Found {len(to_delete_audit)} stale audit entries.")
for row_id, reason in to_delete_audit:
    con.execute("DELETE FROM records WHERE id=?", (row_id,))
    print(f"  Deleted audit row {row_id}: {reason}")

con.commit()

# ============================================================
# PHASE 4 — final state
# ============================================================
print()
print("=" * 60)
print("PHASE 4: Final state")
print("=" * 60)

hazards_remaining = con.execute(
    "SELECT entity_id, data FROM records WHERE entity_type='hazards' "
    "ORDER BY entity_id"
).fetchall()
print(f"\nHazards remaining: {len(hazards_remaining)}")
for row in hazards_remaining:
    d = json.loads(row["data"])
    print(f"  {row['entity_id']:<14} {d.get('title', '')}")

audit_remaining = con.execute(
    "SELECT COUNT(*) AS c FROM records WHERE entity_type='audit_logs'"
).fetchone()["c"]
print(f"\nAudit entries remaining: {audit_remaining}")

con.execute("DELETE FROM counters")
con.commit()
print("Counters reset — next hazard recomputes from live records.")

con.close()
print("\nDone.")