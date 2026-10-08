"""
Rewrite /api/reports/hazard-intervention-planning to return the full
ComprehensiveReportData shape the frontend expects.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "backend" / "app.py"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "geographic_analysis" in text and "sign_off" in text:
    print("Already enriched — skipping.")
    raise SystemExit(0)

# Find the existing endpoint
m = re.search(
    r'@app\.post\("/api/reports/hazard-intervention-planning"\)[\s\S]*?return jsonify\(\{[\s\S]*?\}\)\n',
    text,
)
if not m:
    raise SystemExit("Could not find the report endpoint")

NEW_ENDPOINT = '''@app.post("/api/reports/hazard-intervention-planning")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def report():
    """Generate the comprehensive hazard intervention & planning report."""
    d = request.get_json(silent=True) or {}
    db_state = db.session.get(Setting, "system_settings")
    sys_settings = db_state.value if db_state else {}
    ref_setting = db.session.get(Setting, "reference_data")
    reference_data = ref_setting.value if ref_setting else {}

    # ---------- Filter hazards ----------
    hazards = all_("hazards")
    filters = {}
    for k in ("state", "lga", "ward", "category", "severity"):
        v = d.get(k)
        if v:
            filters[k] = v
            if k == "severity":
                hazards = [h for h in hazards if h.get("severity") == v]
            else:
                hazards = [h for h in hazards if str(h.get(k, "")).lower() == str(v).lower()]

    # Date filters
    date_from = d.get("date_from")
    date_to = d.get("date_to")
    if date_from:
        hazards = [h for h in hazards if (h.get("date_reported") or "") >= date_from]
    if date_to:
        hazards = [h for h in hazards if (h.get("date_reported") or "") <= date_to]

    # Verification status filter
    vs = d.get("verification_status")
    if vs == "Verified":
        hazards = [h for h in hazards if h.get("status") not in ("Draft", "Submitted", "Under Review", "Rejected/Invalid")]
    elif vs == "Unverified":
        hazards = [h for h in hazards if h.get("status") in ("Draft", "Submitted", "Under Review")]
    elif vs == "Invalid":
        hazards = [h for h in hazards if h.get("status") == "Rejected/Invalid"]

    # ---------- Executive summary stats ----------
    total = len(hazards)
    verified = sum(h.get("status") not in ("Draft", "Submitted", "Under Review", "Rejected/Invalid") for h in hazards)
    unverified = sum(h.get("status") in ("Draft", "Submitted", "Under Review") for h in hazards)
    invalid = sum(h.get("status") == "Rejected/Invalid" for h in hazards)
    critical = sum(h.get("severity") == "CRITICAL" for h in hazards)
    high = sum(h.get("severity") == "HIGH" for h in hazards)
    medium = sum(h.get("severity") == "MEDIUM" for h in hazards)
    low = sum(h.get("severity") == "LOW" for h in hazards)
    requiring = sum(h.get("status") in ("Assessed", "Intervention Recommended", "Prioritised") for h in hazards)
    receiving = sum(h.get("status", "").startswith("Intervention ") for h in hazards)
    resolved = sum(h.get("status") in ("Resolved", "Closed") for h in hazards)

    # ---------- Geographic analysis ----------
    by_state = {}
    by_lga = {}
    by_ward = {}
    for h in hazards:
        st = h.get("state") or "Unknown"
        lga = h.get("lga") or "Unknown"
        wd = h.get("ward") or "Unknown"
        by_state[st] = by_state.get(st, 0) + 1
        lga_key = f"{lga} ({st})"
        by_lga[lga_key] = by_lga.get(lga_key, 0) + 1
        ward_key = f"{wd} - {lga}"
        by_ward[ward_key] = by_ward.get(ward_key, 0) + 1

    # ---------- Category analysis ----------
    by_category = {}
    for h in hazards:
        cat = h.get("category") or "Unknown"
        if cat not in by_category:
            by_category[cat] = {"count": 0, "percentage": 0}
        by_category[cat]["count"] += 1
    for cat, data in by_category.items():
        data["percentage"] = round((data["count"] / total) * 100, 1) if total else 0

    # ---------- Severity analysis ----------
    severity_analysis = {
        "CRITICAL": {"count": critical, "percentage": round((critical / total) * 100, 1) if total else 0},
        "HIGH": {"count": high, "percentage": round((high / total) * 100, 1) if total else 0},
        "MEDIUM": {"count": medium, "percentage": round((medium / total) * 100, 1) if total else 0},
        "LOW": {"count": low, "percentage": round((low / total) * 100, 1) if total else 0},
    }

    # ---------- Detailed register ----------
    evidence_all = all_("evidence_files")
    interventions_all = all_("interventions")
    int_by_hazard = {i.get("hazard_id"): i for i in interventions_all}

    rows = []
    recs = []
    for h in hazards:
        i = int_by_hazard.get(h.get("id"))
        rec = i or h.get("recommended_intervention") or {}
        photos = [
            {"id": e.get("id"), "file_name": e.get("file_name"),
             "url": e.get("file_url"), "description": e.get("description")}
            for e in evidence_all
            if e.get("hazard_id") == h.get("id") and e.get("media_type") == "photo"
        ][:3]
        videos = [
            {"evidence_id": e.get("id"), "file_name": e.get("file_name"),
             "date_time": e.get("upload_date"), "description": e.get("description"),
             "secure_link": e.get("file_url")}
            for e in evidence_all
            if e.get("hazard_id") == h.get("id") and e.get("media_type") == "video"
        ]
        rows.append({
            "hazard_id": h.get("id"),
            "title": h.get("title"),
            "category": h.get("category"),
            "description": h.get("description"),
            "state": h.get("state"),
            "lga": h.get("lga"),
            "ward": h.get("ward"),
            "community": h.get("community"),
            "coordinates": f"{h.get('latitude', 0)}, {h.get('longitude', 0)}",
            "date_reported": h.get("date_reported"),
            "reporter": h.get("reporter_name"),
            "verification_status": h.get("status"),
            "verified_by": h.get("verified_by", ""),
            "severity": h.get("severity"),
            "priority_score": h.get("assessment", {}).get("calculated_priority_score"),
            "potential_impact": h.get("potential_impact"),
            "recommended_intervention": rec.get("title", rec.get("scope_description", "")),
            "estimated_cost_ngn": rec.get("estimated_cost_ngn", 0),
            "responsible_authority": rec.get("responsible_department", ""),
            "photographs": photos,
            "video_references": videos,
        })
        if i or h.get("recommended_intervention"):
            recs.append({
                "hazard_id": h.get("id"),
                "recommended_intervention": rec.get("title", rec.get("scope_description", "")),
                "priority": h.get("severity"),
                "estimated_cost_ngn": rec.get("estimated_cost_ngn", 0),
                "responsible_organization": rec.get("responsible_department", ""),
                "expected_timeline": "3 - 6 months",
            })

    total_budget = sum(float(r.get("estimated_cost_ngn") or 0) for r in recs)

    # ---------- Planning analysis ----------
    high_risk_zones = sorted(by_lga.items(), key=lambda x: -x[1])[:5]
    recurring = [
        {"id": h.get("id"), "community": h.get("community"),
         "lga": h.get("lga"), "recurrence_count": h.get("recurring_count", 1)}
        for h in hazards if h.get("is_recurring")
    ]

    planning_analysis = {
        "immediate_intervention_requirements": critical,
        "short_term_requirements": high,
        "medium_term_requirements": medium,
        "long_term_requirements": low,
        "total_estimated_pipeline_budget_ngn": total_budget,
        "high_risk_zones": [{"lga": lga, "count": cnt} for lga, cnt in high_risk_zones],
        "recurring_hotspots": recurring,
    }

    # ---------- Conclusion ----------
    conclusion = (
        f"The Edo State ecological database contains {total} hazard report(s), of which "
        f"{verified} have been independently verified and {critical} are classified CRITICAL "
        f"with imminent risk to life, property, and strategic infrastructure. "
        f"The total estimated cost of recommended interventions stands at "
        f"NGN {(total_budget/1e9):.2f} Billion. "
        f"Priority attention is directed to "
        f"{', '.join([z['lga'] for z in planning_analysis['high_risk_zones'][:3]])} "
        f"where the highest concentration of hazards has been recorded. "
        f"Immediate intervention categories include gully erosion control, "
        f"stepped spillway construction, channelization, and mechanical desilting "
        f"across identified high-density watersheds in Edo State."
    )

    return jsonify({
        "report_metadata": {
            "report_title": d.get("title", "Edo State Comprehensive Ecological Hazard, Intervention & Planning Report"),
            "organization": sys_settings.get("organization_name", "Edo State Ecological Fund Agency (EDEFA)"),
            "department": sys_settings.get("department_name", "Ecological Hazard Management & GIS"),
            "generated_at": now(),
            "generated_by": f"{user().get('name')} ({user().get('role_title', user().get('role'))})",
            "reporting_scope": {
                "state": d.get("state") or "All States (National Coverage)",
                "lga": d.get("lga") or "All LGAs",
                "category": d.get("category") or "All Ecological Categories",
                "severity": d.get("severity") or "All Severity Levels",
            },
        },
        "executive_summary_stats": {
            "totalReports": total,
            "verifiedReports": verified,
            "unverifiedReports": unverified,
            "invalidReports": invalid,
            "criticalHazards": critical,
            "highHazards": high,
            "mediumHazards": medium,
            "lowHazards": low,
            "requiringIntervention": requiring,
            "alreadyReceivingIntervention": receiving,
            "resolvedHazards": resolved,
        },
        "geographic_analysis": {
            "by_state": by_state,
            "by_lga": by_lga,
            "by_ward": by_ward,
        },
        "hazard_category_analysis": by_category,
        "severity_analysis": severity_analysis,
        "detailed_hazard_register": rows,
        "intervention_recommendations": recs,
        "planning_analysis": planning_analysis,
        "conclusion_text": conclusion,
        "sign_off": {
            "prepared_by": d.get("prepared_by", "Engr. Director of Ecological Hazard Management & GIS"),
            "reviewed_by": d.get("reviewed_by", "Permanent Secretary, Edo State Ministry of Environment"),
            "approved_by": d.get("approved_by", "Executive Governor / Chairman, Edo State Ecological Fund Agency"),
        },
    })
'''

text = text[:m.start()] + NEW_ENDPOINT + text[m.end():]
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Enriched report endpoint with full ComprehensiveReportData shape")