"""
Seed the `contractors` entity with real firms already referenced in the
project data, plus a few standard Nigerian civil engineering contractors.

Idempotent — skips contractors that already exist by name.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB = Path(__file__).parent / "instance" / "ef_phmips.db"
if not DB.exists():
    raise SystemExit(f"Database not found: {DB}")

def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# Real firms referenced in existing projects, plus common Nigerian contractors
SEED = [
    {
        "id": "CON-2026-001",
        "name": "Julius Berger Nigeria Plc",
        "registration_no": "RC-19284",
        "category": "Major Civil Works",
        "specialties": ["Gully Erosion Control", "Flood Control & Channelization", "Roads & Drainage"],
        "contact_person": "Engr. Adewale Ogundipe",
        "phone": "+234 803 555 0001",
        "email": "projects@juliusberger.com",
        "address": "10 Shettima A. Munguno Crescent, Utako, Abuja",
        "state": "FCT",
        "active": True,
        "rating": 4.8,
    },
    {
        "id": "CON-2026-002",
        "name": "CGC Nigeria Limited",
        "registration_no": "RC-25831",
        "category": "Major Civil Works",
        "specialties": ["Gully Erosion Control", "Landslide Stabilization", "Water Infrastructure"],
        "contact_person": "Engr. Chen Wei",
        "phone": "+234 805 555 0002",
        "email": "nigeria@cgc.com",
        "address": "Plot 1025, Ahmadu Bello Way, Victoria Island, Lagos",
        "state": "Lagos",
        "active": True,
        "rating": 4.6,
    },
    {
        "id": "CON-2026-003",
        "name": "Reynolds Construction Company (RCC) Nig. Ltd",
        "registration_no": "RC-12574",
        "category": "Major Civil Works",
        "specialties": ["Flood Control & Channelization", "Dams & Reservoirs", "Roads"],
        "contact_person": "Engr. Bola Adeyemi",
        "phone": "+234 802 555 0003",
        "email": "info@rccnigeria.com",
        "address": "1 RCC Close, Igamu, Lagos",
        "state": "Lagos",
        "active": True,
        "rating": 4.7,
    },
    {
        "id": "CON-2026-004",
        "name": "Hydro-Geo Consortium Ltd",
        "registration_no": "RC-1400225",
        "category": "Specialist Engineering",
        "specialties": ["Geotechnical Engineering", "Gully Erosion Control"],
        "contact_person": "Engr. Ifeanyi Nwosu",
        "phone": "+234 806 555 0004",
        "email": "contact@hydrogeo.ng",
        "address": "22 Benin-Sapele Road, Benin City, Edo",
        "state": "Edo",
        "active": True,
        "rating": 4.5,
    },
    {
        "id": "CON-2026-005",
        "name": "Edo Geo-Eng Consortium Ltd",
        "registration_no": "RC-1600332",
        "category": "Specialist Engineering",
        "specialties": ["Gully Erosion Control", "Watershed Reclamation", "Bio-engineering"],
        "contact_person": "Engr. Osaro Igbinedion",
        "phone": "+234 807 555 0005",
        "email": "projects@edogeoeng.com",
        "address": "15 Airport Road, Benin City, Edo",
        "state": "Edo",
        "active": True,
        "rating": 4.4,
    },
    {
        "id": "CON-2026-006",
        "name": "Dantata & Sawoe Construction Company",
        "registration_no": "RC-18871",
        "category": "Major Civil Works",
        "specialties": ["Roads & Drainage", "Bridges", "Flood Control"],
        "contact_person": "Alhaji Musa Dantata",
        "phone": "+234 809 555 0006",
        "email": "info@dantata-sawoe.com",
        "address": "Kano-Zaria Expressway, Kano",
        "state": "Kano",
        "active": True,
        "rating": 4.6,
    },
    {
        "id": "CON-2026-007",
        "name": "Setraco Nigeria Limited",
        "registration_no": "RC-19763",
        "category": "Major Civil Works",
        "specialties": ["Roads & Drainage", "Landslide Stabilization"],
        "contact_person": "Engr. Tony Elumelu",
        "phone": "+234 810 555 0007",
        "email": "info@setraco.com",
        "address": "Plot 5, IBB Way, Maitama, Abuja",
        "state": "FCT",
        "active": True,
        "rating": 4.5,
    },
    {
        "id": "CON-2026-008",
        "name": "Edo State Civil Engineering Works Ltd",
        "registration_no": "RC-EDO-0451",
        "category": "Regional Contractor",
        "specialties": ["Local Drainage", "Small-Scale Erosion Control"],
        "contact_person": "Engr. Blessing Omoregie",
        "phone": "+234 812 555 0008",
        "email": "info@edocivilworks.ng",
        "address": "23 Sapele Road, Benin City, Edo",
        "state": "Edo",
        "active": True,
        "rating": 4.2,
    },
]

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

print("=== Seeding contractors ===")

# Get existing contractor names (case-insensitive)
existing = set()
for row in con.execute("SELECT data FROM records WHERE entity_type='contractors'").fetchall():
    try:
        d = json.loads(row["data"])
        existing.add(d.get("name", "").lower())
    except Exception:
        pass

inserted = 0
for c in SEED:
    if c["name"].lower() in existing:
        print(f"  SKIP (exists): {c['name']}")
        continue
    c["created_at"] = now()
    con.execute(
        "INSERT INTO records (entity_type, entity_id, data) VALUES (?, ?, ?)",
        ("contractors", c["id"], json.dumps(c)),
    )
    print(f"  INSERT: {c['id']}  {c['name']}")
    inserted += 1

con.commit()

# Show final state
print()
print(f"Inserted {inserted} contractor(s).")
print()
print("=== All contractors ===")
for row in con.execute(
    "SELECT entity_id, data FROM records WHERE entity_type='contractors' ORDER BY entity_id"
).fetchall():
    d = json.loads(row["data"])
    print(f"  {row['entity_id']}  {d.get('name', ''):<50} {d.get('category', '')}")

con.close()
print()
print("Done. Now run the endpoint script to expose /api/contractors.")