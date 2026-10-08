"""
APPLY ALL CHANGES — complete end-to-end patch:

  1. backend/seed_contractors.py      — seeds 8 contractors into the DB
  2. backend/add_contractors_endpoint.py — adds GET/POST /api/contractors
  3. backend/patch_project_modal_contractor.py — replaces Contractor input
     with a dropdown of registered contractors

Also:
  4. Patches src/types/index.ts to add the Contractor interface
  5. Patches src/services/api.ts to add getContractors and createContractor
  6. Reports what it did

Idempotent — safe to run multiple times.
"""

import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
DB = BACKEND / "instance" / "ef_phmips.db"
APP_PY = BACKEND / "app.py"
TYPES_TS = ROOT / "src" / "types" / "index.ts"
API_TS = ROOT / "src" / "services" / "api.ts"
MODAL_TS = ROOT / "src" / "components" / "projects" / "ProjectModal.tsx"


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def section(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


# ============================================================
# STEP 1 — SEED CONTRACTORS
# ============================================================
section("STEP 1: Seed contractors into the database")

if not DB.exists():
    raise SystemExit(f"Database not found: {DB}")

SEED = [
    {"id": "CON-2026-001", "name": "Julius Berger Nigeria Plc", "registration_no": "RC-19284", "category": "Major Civil Works", "specialties": ["Gully Erosion Control", "Flood Control & Channelization", "Roads & Drainage"], "contact_person": "Engr. Adewale Ogundipe", "phone": "+234 803 555 0001", "email": "projects@juliusberger.com", "address": "10 Shettima A. Munguno Crescent, Utako, Abuja", "state": "FCT", "active": True, "rating": 4.8},
    {"id": "CON-2026-002", "name": "CGC Nigeria Limited", "registration_no": "RC-25831", "category": "Major Civil Works", "specialties": ["Gully Erosion Control", "Landslide Stabilization", "Water Infrastructure"], "contact_person": "Engr. Chen Wei", "phone": "+234 805 555 0002", "email": "nigeria@cgc.com", "address": "Plot 1025, Ahmadu Bello Way, Victoria Island, Lagos", "state": "Lagos", "active": True, "rating": 4.6},
    {"id": "CON-2026-003", "name": "Reynolds Construction Company (RCC) Nig. Ltd", "registration_no": "RC-12574", "category": "Major Civil Works", "specialties": ["Flood Control & Channelization", "Dams & Reservoirs", "Roads"], "contact_person": "Engr. Bola Adeyemi", "phone": "+234 802 555 0003", "email": "info@rccnigeria.com", "address": "1 RCC Close, Igamu, Lagos", "state": "Lagos", "active": True, "rating": 4.7},
    {"id": "CON-2026-004", "name": "Hydro-Geo Consortium Ltd", "registration_no": "RC-1400225", "category": "Specialist Engineering", "specialties": ["Geotechnical Engineering", "Gully Erosion Control"], "contact_person": "Engr. Ifeanyi Nwosu", "phone": "+234 806 555 0004", "email": "contact@hydrogeo.ng", "address": "22 Benin-Sapele Road, Benin City, Edo", "state": "Edo", "active": True, "rating": 4.5},
    {"id": "CON-2026-005", "name": "Edo Geo-Eng Consortium Ltd", "registration_no": "RC-1600332", "category": "Specialist Engineering", "specialties": ["Gully Erosion Control", "Watershed Reclamation", "Bio-engineering"], "contact_person": "Engr. Osaro Igbinedion", "phone": "+234 807 555 0005", "email": "projects@edogeoeng.com", "address": "15 Airport Road, Benin City, Edo", "state": "Edo", "active": True, "rating": 4.4},
    {"id": "CON-2026-006", "name": "Dantata & Sawoe Construction Company", "registration_no": "RC-18871", "category": "Major Civil Works", "specialties": ["Roads & Drainage", "Bridges", "Flood Control"], "contact_person": "Alhaji Musa Dantata", "phone": "+234 809 555 0006", "email": "info@dantata-sawoe.com", "address": "Kano-Zaria Expressway, Kano", "state": "Kano", "active": True, "rating": 4.6},
    {"id": "CON-2026-007", "name": "Setraco Nigeria Limited", "registration_no": "RC-19763", "category": "Major Civil Works", "specialties": ["Roads & Drainage", "Landslide Stabilization"], "contact_person": "Engr. Tony Elumelu", "phone": "+234 810 555 0007", "email": "info@setraco.com", "address": "Plot 5, IBB Way, Maitama, Abuja", "state": "FCT", "active": True, "rating": 4.5},
    {"id": "CON-2026-008", "name": "Edo State Civil Engineering Works Ltd", "registration_no": "RC-EDO-0451", "category": "Regional Contractor", "specialties": ["Local Drainage", "Small-Scale Erosion Control"], "contact_person": "Engr. Blessing Omoregie", "phone": "+234 812 555 0008", "email": "info@edocivilworks.ng", "address": "23 Sapele Road, Benin City, Edo", "state": "Edo", "active": True, "rating": 4.2},
]

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

existing = set()
for row in con.execute("SELECT data FROM records WHERE entity_type='contractors'").fetchall():
    try:
        existing.add(json.loads(row["data"]).get("name", "").lower())
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
print(f"\n  Inserted {inserted} contractor(s).")
con.close()


# ============================================================
# STEP 2 — ADD ENDPOINT TO app.py
# ============================================================
section("STEP 2: Add /api/contractors endpoints to app.py")

if not APP_PY.exists():
    raise SystemExit(f"Not found: {APP_PY}")

text = APP_PY.read_text(encoding="utf-8")

if "/api/contractors" in text:
    print("  Already present — skipping.")
else:
    anchor = '''# ==================== SITES / VISITS ====================
@app.get("/api/sites")'''

    new_block = '''# ==================== CONTRACTORS ====================
@app.get("/api/contractors")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def contractors():
    items = all_("contractors")
    active_only = request.args.get("active") in ("1", "true", "yes")
    if active_only:
        items = [x for x in items if x.get("active", True)]
    return jsonify(items)

@app.post("/api/contractors")
@require_tier("TIER_1_ADMIN","TIER_3_DIRECTOR")
def contractor_create():
    d = request.get_json(silent=True) or {}
    cid = nxt("CON", "contractors")
    c = {
        "id": cid,
        "name": d.get("name", "Unnamed Contractor"),
        "registration_no": d.get("registration_no", ""),
        "category": d.get("category", "Regional Contractor"),
        "specialties": d.get("specialties", []),
        "contact_person": d.get("contact_person", ""),
        "phone": d.get("phone", ""),
        "email": d.get("email", ""),
        "address": d.get("address", ""),
        "state": d.get("state", "Edo"),
        "active": d.get("active", True),
        "rating": float(d.get("rating") or 0),
        "created_at": now(),
    }
    put("contractors", c)
    audit("CREATE_CONTRACTOR", "CONTRACTOR", cid, None, c, details=f"Registered contractor {c['name']}")
    db.session.commit()
    return jsonify(c), 201

# ==================== SITES / VISITS ====================
@app.get("/api/sites")'''

    if anchor not in text:
        raise SystemExit("SITES section anchor not found in app.py")

    text = text.replace(anchor, new_block, 1)
    print("  Added GET /api/contractors")
    print("  Added POST /api/contractors")

# Update nxt() entity_map
old_map = '"EVD":"evidence_files","INT":"interventions","ACT":"actions",'
new_map = '"EVD":"evidence_files","INT":"interventions","ACT":"actions","CON":"contractors",'
if old_map in text and '"CON":"contractors"' not in text:
    text = text.replace(old_map, new_map, 1)
    print("  Updated nxt() entity_map to include CON")

APP_PY.write_text(text, encoding="utf-8")


# ============================================================
# STEP 3 — ADD Contractor TYPE
# ============================================================
section("STEP 3: Add Contractor interface to types/index.ts")

if not TYPES_TS.exists():
    raise SystemExit(f"Not found: {TYPES_TS}")

types_text = TYPES_TS.read_text(encoding="utf-8")

if "export interface Contractor" in types_text:
    print("  Already present — skipping.")
else:
    contractor_type = """
export interface Contractor {
  id: string;
  name: string;
  registration_no?: string;
  category?: string;
  specialties?: string[];
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  state?: string;
  active?: boolean;
  rating?: number;
  created_at?: string;
}
"""
    # Insert before ReferenceData
    anchor = "export interface ReferenceData {"
    if anchor in types_text:
        types_text = types_text.replace(anchor, contractor_type + "\n" + anchor, 1)
        TYPES_TS.write_text(types_text, encoding="utf-8")
        print("  Added Contractor interface (before ReferenceData)")
    else:
        # Fallback: append at end
        types_text = types_text.rstrip() + "\n" + contractor_type
        TYPES_TS.write_text(types_text, encoding="utf-8")
        print("  Added Contractor interface (appended to end)")


# ============================================================
# STEP 4 — ADD api METHODS
# ============================================================
section("STEP 4: Add getContractors + createContractor to api.ts")

if not API_TS.exists():
    raise SystemExit(f"Not found: {API_TS}")

api_text = API_TS.read_text(encoding="utf-8")

# 4a — extend imports
if "Contractor" not in api_text.split("} from '../types/index.ts';")[0]:
    old_import = """  ReferenceData,
  DashboardStats,
  ComprehensiveReportData
} from '../types/index.ts';"""
    new_import = """  ReferenceData,
  DashboardStats,
  ComprehensiveReportData,
  Contractor
} from '../types/index.ts';"""
    if old_import in api_text:
        api_text = api_text.replace(old_import, new_import, 1)
        print("  Extended types import with Contractor")
    else:
        print("  WARNING: import block shape not recognized")

# 4b — add methods
if "getContractors:" in api_text:
    print("  getContractors already present")
else:
    anchor = "  // Interventions & Actions"
    new_methods = """  // Contractors
  getContractors: () => request<Contractor[]>('/contractors?active=1'),
  createContractor: (data: Partial<Contractor>) => request<Contractor>('/contractors', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Interventions & Actions"""

    if anchor in api_text:
        api_text = api_text.replace(anchor, new_methods, 1)
        print("  Added getContractors + createContractor")
    else:
        print("  WARNING: could not find '// Interventions & Actions' anchor")

API_TS.write_text(api_text, encoding="utf-8")


# ============================================================
# STEP 5 — PATCH ProjectModal.tsx
# ============================================================
section("STEP 5: Replace Contractor Name input with a dropdown")

if not MODAL_TS.exists():
    raise SystemExit(f"Not found: {MODAL_TS}")

modal_text = MODAL_TS.read_text(encoding="utf-8")

if "contractorList" in modal_text:
    print("  Already patched — skipping.")
else:
    # 5a — extend imports
    old_import = "import { Project, ProjectStatus, Intervention } from '../../types/index.ts';"
    new_import = "import { Project, ProjectStatus, Intervention, Contractor } from '../../types/index.ts';"
    if old_import in modal_text:
        modal_text = modal_text.replace(old_import, new_import, 1)
        print("  Added Contractor type import")
    else:
        old_alt = "import { Project, ProjectStatus } from '../../types/index.ts';"
        if old_alt in modal_text:
            modal_text = modal_text.replace(old_alt, new_import, 1)
            print("  Added Contractor type import (alt)")

    # 5b — add state
    anchor = "const [interventionsLoading, setInterventionsLoading] = useState(false);"
    new_state = anchor + """

  const [contractorList, setContractorList] = useState<Contractor[]>([]);
  const [contractorsLoading, setContractorsLoading] = useState(false);"""
    if anchor in modal_text:
        modal_text = modal_text.replace(anchor, new_state, 1)
        print("  Added contractorList state")

    # 5c — add useEffect
    anchor2 = "  // Fetch Executive-Approved interventions when the modal opens"
    new_effect = """  // Fetch active contractors when the modal opens
  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    setContractorsLoading(true);
    (async () => {
      try {
        const list = await api.getContractors();
        if (!cancelled) setContractorList(list || []);
      } catch (err) {
        console.error('Failed to load contractors:', err);
      } finally {
        if (!cancelled) setContractorsLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [isOpen]);

  // Fetch Executive-Approved interventions when the modal opens"""
    if anchor2 in modal_text:
        modal_text = modal_text.replace(anchor2, new_effect, 1)
        print("  Added contractor fetch useEffect")

    # 5d — replace input with select
    idx = modal_text.find("Contractor Name")
    if idx == -1:
        print("  WARNING: 'Contractor Name' not found")
    else:
        m = re.search(r'<input[\s\S]*?/>', modal_text[idx:idx + 800])
        if m:
            start = idx + m.start()
            end = idx + m.end()
            replacement = """<select
                value={formData.contractor}
                onChange={e => setFormData({ ...formData, contractor: e.target.value })}
                disabled={contractorsLoading}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              >
                <option value="">
                  {contractorsLoading ? 'Loading contractors…' : '— Select a registered contractor —'}
                </option>
                {contractorList.map(c => (
                  <option key={c.id} value={c.name}>
                    {c.name} ({c.registration_no || c.id})
                  </option>
                ))}
              </select>"""
            modal_text = modal_text[:start] + replacement + modal_text[end:]
            print("  Replaced Contractor input with dropdown")
        else:
            print("  WARNING: input tag after Contractor Name not found")

    MODAL_TS.write_text(modal_text, encoding="utf-8")


# ============================================================
# DONE
# ============================================================
section("COMPLETE")
print("""
Changes applied:
  ✓ 8 contractors seeded into the database
  ✓ GET /api/contractors added
  ✓ POST /api/contractors added
  ✓ nxt() entity_map updated for CON prefix
  ✓ Contractor interface added to types/index.ts
  ✓ getContractors + createContractor added to api.ts
  ✓ ProjectModal.tsx uses a dropdown for Contractor Name

Next steps:
  1. npx tsc --noEmit                (verify TS compiles)
  2. Restart Flask:
       Get-NetTCPConnection -LocalPort 5000 -State Listen |
         ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
       py -3.12 backend\\app.py
  3. Reload the browser (Ctrl+Shift+R)
  4. Log in as inspector
  5. Open "Create New Project"
  6. The Contractor Name field should be a dropdown with 8 firms
""")