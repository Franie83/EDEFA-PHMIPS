"""Restore the seed hazard EH-2026-002 that was overwritten during testing."""
import sqlite3
import json
from pathlib import Path

DB = Path(__file__).parent / "instance" / "ef_phmips.db"
if not DB.exists():
    raise SystemExit(f"Database not found: {DB}")

con = sqlite3.connect(DB)

existing = con.execute(
    "SELECT id FROM records WHERE entity_type='hazards' AND entity_id='EH-2026-002'"
).fetchone()

if existing:
    print("EH-2026-002 already exists — nothing to do.")
    con.close()
    raise SystemExit(0)

hazard = {
    "id": "EH-2026-002",
    "title": "Catastrophic Flash Flooding & Blocked Canal at Oredo LGA",
    "category": "Flooding",
    "hazard_type": "Severe urban flooding and waterway obstruction",
    "description": ("Massive accumulation of plastic refuse and silt obstructing the "
                    "primary municipal drainage canal at Forestry / Sakponba junction. "
                    "Water submerges roads by 1.2 meters after 30 minutes of rain."),
    "date_observed": "2026-08-20",
    "date_reported": "2026-08-20T14:10:00Z",
    "reporter_name": "Tariq Mohammed, MNIQS",
    "reporter_type": "FIELD_OFFICER",
    "reporter_contact": "+234 806 555 7788",
    "state": "Edo",
    "lga": "Oredo",
    "ward": "Ward 4 (Ogbelaka / Nekpenekpen)",
    "community": "Forestry Road / Sakponba Junction",
    "address_description": ("Major arterial drainage canal crossing Sakponba Road "
                            "toward Ogba River basin."),
    "latitude": 6.3298,
    "longitude": 5.6261,
    "estimated_affected_area_sqm": 35000,
    "estimated_affected_population": 8500,
    "estimated_affected_assets": ("120 commercial shops, 65 residential houses, "
                                  "2 primary schools, major traffic artery."),
    "potential_impact": ("Severe business disruption, flood damage to properties, "
                         "outbreak of waterborne diseases (cholera/malaria), "
                         "vehicular submergence."),
    "severity": "HIGH",
    "urgency": "IMMEDIATE",
    "status": "Intervention Ongoing",
    "tracking_code": "EF-HAZ-2026-0820-ORED",
    "is_recurring": True,
    "recurring_count": 5,
    "verified_by": "Arch. Olumide Johnson",
    "verified_at": "2026-08-21T16:00:00Z",
    "verification_notes": ("Inspected by Monitoring Coordinator Arch. Olumide Johnson "
                           "on Aug 21, 2026. Obstruction confirmed; water flow reduced by 85%."),
    "assessment": {
        "severity_score": 8, "urgency_score": 8.5, "exposure_score": 8,
        "impact_score": 7.5, "escalation_risk_score": 8,
        "calculated_priority_score": 8.05, "recommended_priority": "HIGH",
        "environmental_impact": "Stagnant wastewater, vector breeding, urban siltation.",
        "economic_impact": "Daily economic loss estimated at N35 Million in lost trade during rain episodes.",
        "social_impact": "School closures, pedestrian danger, contamination of shallow boreholes.",
        "technical_findings": "Over 1,200 metric tons of debris and sediment trapped under low-clearance slab bridge.",
        "recommended_intervention_type": "Drainage Desilting & Channel Widening",
        "assessed_by": "Engr. Chinwe Okoro", "assessed_at": "2026-08-22T10:00:00Z",
    },
    "recommended_intervention": {
        "intervention_id": "INT-2026-002",
        "title": "Emergency Mechanical Desilting and Trash Rack Installation at Forestry Canal",
        "scope_description": ("Immediate deployment of amphibious excavators to clear 2.8km "
                              "of blocked channel, installation of hydraulic debris "
                              "interceptors, and raising bridge headwall."),
        "estimated_cost_ngn": 210000000,
        "proposed_funding": "State-Federal Ecological Matching Grant",
        "responsible_department": "Urban Drainage & Flood Mitigation Unit",
        "responsible_officer": "Tariq Mohammed, MNIQS",
        "proposed_start_date": "2026-08-25",
        "proposed_completion_date": "2026-10-15",
        "expected_outcome": ("Restore 100% hydraulic discharge capacity, eliminate "
                             "standing floodwaters in residential quarters."),
    },
}

con.execute(
    "INSERT INTO records (entity_type, entity_id, data) VALUES (?, ?, ?)",
    ("hazards", "EH-2026-002", json.dumps(hazard)),
)
con.commit()
con.close()
print("Restored EH-2026-002 — Catastrophic Flash Flooding & Blocked Canal at Oredo LGA")