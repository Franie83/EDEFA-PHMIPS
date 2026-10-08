import pathlib

# ============================================================
# 1. Add PUBLIC_USER to permissions.py
# ============================================================
pp = pathlib.Path("backend/permissions.py")
psrc = pp.read_text(encoding="utf-8")

if '"PUBLIC_USER"' not in psrc:
    psrc = psrc.replace(
        '    "PLANNING_OFFICER":  "TIER_4_STAFF",\n}',
        '    "PLANNING_OFFICER":  "TIER_4_STAFF",\n    "PUBLIC_USER":       "TIER_5_PUBLIC",\n}'
    )
    psrc = psrc.replace(
        '    "TIER_4_STAFF":    "Staff",\n}',
        '    "TIER_4_STAFF":    "Staff",\n    "TIER_5_PUBLIC":   "Public User",\n}'
    )
    pp.write_text(psrc, encoding="utf-8")
    print("permissions.py: added PUBLIC_USER / TIER_5_PUBLIC")
else:
    print("permissions.py: PUBLIC_USER already present")

# ============================================================
# 2. Add CMS endpoints to app.py
# ============================================================
ap = pathlib.Path("backend/app.py")
src = ap.read_text(encoding="utf-8")

if "/api/cms/branding" in src:
    print("app.py: CMS endpoints already present, skipping")
else:
    # --- Add PUBLIC_USER to ROLES list ---
    src = src.replace(
        '("AUDITOR","Auditor","Read-only access to all registers and audit trails")',
        '("AUDITOR","Auditor","Read-only access to all registers and audit trails"),'
        '("PUBLIC_USER","Public User","Public reporter - can submit hazards, no dashboard access")'
    )

    # --- Add default branding constant right after ROLES ---
    branding_default = '''
DEFAULT_BRANDING = {
    "app_name": "EDEFA-PHMIPS",
    "app_tagline": "Ecological Fund Project & Hazard Management",
    "agency_name": "Edo State Ecological Fund Agency",
    "logo_url": "",
    "primary_color": "#0F5132",
    "footer_text": "(c) Edo State Ecological Fund Agency"
}

def get_branding():
    s = db.session.get(Setting, "branding")
    if not s:
        s = Setting(key="branding", value=dict(DEFAULT_BRANDING))
        db.session.add(s)
        db.session.commit()
    return dict(s.value)
'''
    src = src.replace(
        'ENTITIES=["users","hazards","projects","sites","site_visits","evidence_files","interventions","actions","audit_logs","notifications"]',
        'ENTITIES=["users","hazards","projects","sites","site_visits","evidence_files","interventions","actions","audit_logs","notifications"]\n' + branding_default
    )

    # --- Append CMS endpoints before the SPA fallback route ---
    cms_block = '''
# ==================== CMS / CONTENT MANAGEMENT ====================
# All endpoints here are SUPER_ADMIN only.

@app.get("/api/cms/branding")
@require_tier("TIER_1_ADMIN")
def cms_branding_get():
    return jsonify(get_branding())

@app.put("/api/cms/branding")
@require_tier("TIER_1_ADMIN")
def cms_branding_put():
    d = request.get_json(silent=True) or {}
    s = db.session.get(Setting, "branding")
    if not s:
        s = Setting(key="branding", value=dict(DEFAULT_BRANDING))
        db.session.add(s)
    new = {**s.value, **d}
    # Handle logo upload
    logo_b64 = d.get("logo_base64")
    if logo_b64:
        raw = re.sub(r"^data:[^;]+;base64,", "", logo_b64)
        try:
            content = base64.b64decode(raw, validate=True)
        except (ValueError, binascii.Error):
            return jsonify({"error": "Invalid base64 logo"}), 400
        ext = ".png"
        if "image/jpeg" in (d.get("logo_mime") or ""):
            ext = ".jpg"
        elif "image/svg" in (d.get("logo_mime") or ""):
            ext = ".svg"
        fname = f"logo_{uuid.uuid4().hex}{ext}"
        (UPLOADS / fname).write_bytes(content)
        new["logo_url"] = f"/api/evidence/file/{fname}"
        new.pop("logo_base64", None)
        new.pop("logo_mime", None)
    s.value = new
    audit("UPDATE_BRANDING", "SETTINGS", "branding", old=None, new=new)
    db.session.commit()
    return jsonify(new)

@app.get("/api/cms/users")
@require_tier("TIER_1_ADMIN")
def cms_users():
    users = _raw("users")
    return jsonify([{
        "id": u.get("id"),
        "name": u.get("name"),
        "username": u.get("username"),
        "email": u.get("email"),
        "role": u.get("role"),
        "role_title": u.get("role_title"),
        "department": u.get("department"),
        "phone": u.get("phone"),
        "active": u.get("active", True),
        "quick_access": u.get("quick_access", False),
        "created_at": u.get("created_at"),
        "last_login": u.get("last_login"),
    } for u in users])

@app.post("/api/cms/users")
@require_tier("TIER_1_ADMIN")
def cms_user_create():
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    username = (d.get("username") or "").strip().lower()
    email = (d.get("email") or "").strip().lower()
    password = d.get("password") or ""
    role = d.get("role") or "PUBLIC_USER"

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400
    if not email:
        return jsonify({"error": "email required"}), 400

    users = _raw("users")
    if any(str(u.get("username", "")).lower() == username for u in users):
        return jsonify({"error": "username already exists"}), 409
    if any(str(u.get("email", "")).lower() == email for u in users):
        return jsonify({"error": "email already exists"}), 409
    if role not in {r[0] for r in ROLES}:
        return jsonify({"error": f"invalid role: {role}"}), 400

    uid = f"USR-{len(users)+1:04d}"
    u = {
        "id": uid, "name": name or username.title(),
        "username": username, "email": email,
        "role": role, "role_title": role.replace("_", " ").title(),
        "department": d.get("department", "Operations"),
        "phone": d.get("phone", ""),
        "password_hash": generate_password_hash(password),
        "active": True, "quick_access": False,
        "created_at": now(),
    }
    put("users", u)
    audit("CMS_CREATE_USER", "SETTINGS", uid, None, _clean(u))
    db.session.commit()
    return jsonify(_clean(u)), 201

@app.put("/api/cms/users/<id>")
@require_tier("TIER_1_ADMIN")
def cms_user_update(id):
    r = one("users", id)
    if not r:
        return jsonify({"error": "User not found"}), 404
    d = request.get_json(silent=True) or {}
    old = dict(r.data)
    me = user()
    if old.get("role") == "SUPER_ADMIN" and me.get("id") != id:
        if "role" in d and d["role"] != "SUPER_ADMIN":
            return jsonify({"error": "Cannot demote another Super Admin"}), 403
    immutable = {"id", "created_at", "password_hash"}
    new = {**old, **{k: v for k, v in d.items() if k not in immutable and k != "password"}}
    if d.get("password"):
        new["password_hash"] = generate_password_hash(str(d["password"]))
    r.data = new
    audit("CMS_UPDATE_USER", "SETTINGS", id, old=_clean(old), new=_clean(new))
    db.session.commit()
    return jsonify(_clean(new))

@app.delete("/api/cms/users/<id>")
@require_tier("TIER_1_ADMIN")
def cms_user_delete(id):
    r = one("users", id)
    if not r:
        return jsonify({"error": "User not found"}), 404
    me = user()
    if me.get("id") == id:
        return jsonify({"error": "Cannot delete your own account"}), 403
    if r.data.get("role") == "SUPER_ADMIN":
        return jsonify({"error": "Cannot delete a Super Admin"}), 403
    deleted = dict(r.data)
    db.session.delete(r)
    audit("CMS_DELETE_USER", "SETTINGS", id, old=_clean(deleted), new=None)
    db.session.commit()
    return jsonify({"success": True, "deleted_id": id})

@app.post("/api/cms/users/<id>/suspend")
@require_tier("TIER_1_ADMIN")
def cms_user_suspend(id):
    r = one("users", id)
    if not r:
        return jsonify({"error": "User not found"}), 404
    me = user()
    if me.get("id") == id:
        return jsonify({"error": "Cannot suspend your own account"}), 403
    u = dict(r.data)
    u["active"] = not u.get("active", True)
    r.data = u
    audit("CMS_SUSPEND_USER", "SETTINGS", id, old=None, new={"active": u["active"]})
    db.session.commit()
    return jsonify({"success": True, "active": u["active"]})

@app.post("/api/cms/users/<id>/reset-password")
@require_tier("TIER_1_ADMIN")
def cms_user_reset_pw(id):
    r = one("users", id)
    if not r:
        return jsonify({"error": "User not found"}), 404
    d = request.get_json(silent=True) or {}
    pw = d.get("password") or ""
    if len(pw) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400
    u = dict(r.data)
    u["password_hash"] = generate_password_hash(pw)
    r.data = u
    audit("CMS_RESET_PASSWORD", "SETTINGS", id, old=None, new=None)
    db.session.commit()
    return jsonify({"success": True})

@app.get("/api/cms/database/stats")
@require_tier("TIER_1_ADMIN")
def cms_db_stats():
    out = {}
    for e in ENTITIES:
        out[e] = len(_raw(e))
    backups = list(BACKUPS.glob("*.json"))
    out["_backups"] = len(backups)
    return jsonify(out)

@app.post("/api/cms/database/flush")
@require_tier("TIER_1_ADMIN")
def cms_db_flush():
    # auto-snapshot first
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fn = f"preflush_{ts}.json"
    payload = {e: all_(e) for e in ENTITIES}
    payload.update(reference_data=db.session.get(Setting, "reference_data").value,
                   system_settings=db.session.get(Setting, "system_settings").value,
                   branding=get_branding())
    (BACKUPS / fn).write_text(json.dumps(payload, indent=2))
    clear_seed_data()
    audit("CMS_FLUSH_DATABASE", "SETTINGS", "db", old=None, new={"snapshot": fn})
    db.session.commit()
    return jsonify({"success": True, "snapshot": fn,
                    "message": "Database flushed. Quick-access users preserved."})

@app.post("/api/cms/database/reseed")
@require_tier("TIER_1_ADMIN")
def cms_db_reseed():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fn = f"prereseed_{ts}.json"
    payload = {e: all_(e) for e in ENTITIES}
    payload.update(reference_data=db.session.get(Setting, "reference_data").value,
                   system_settings=db.session.get(Setting, "system_settings").value,
                   branding=get_branding())
    (BACKUPS / fn).write_text(json.dumps(payload, indent=2))
    seed(True)
    audit("CMS_RESEED_DATABASE", "SETTINGS", "db", old=None, new={"snapshot": fn})
    db.session.commit()
    return jsonify({"success": True, "snapshot": fn,
                    "message": "Database reseeded from seed_data.json"})

@app.post("/api/cms/database/snapshot")
@require_tier("TIER_1_ADMIN")
def cms_db_snapshot():
    d = request.get_json(silent=True) or {}
    label = secure_filename(d.get("label", "")) or "manual"
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fn = f"cms_{label}_{ts}.json"
    payload = {e: all_(e) for e in ENTITIES}
    payload.update(reference_data=db.session.get(Setting, "reference_data").value,
                   system_settings=db.session.get(Setting, "system_settings").value,
                   branding=get_branding())
    (BACKUPS / fn).write_text(json.dumps(payload, indent=2))
    return jsonify({"success": True, "filename": fn,
                    "size": (BACKUPS / fn).stat().st_size,
                    "created_at": now()})

@app.get("/api/cms/database/backups")
@require_tier("TIER_1_ADMIN")
def cms_db_backups():
    out = []
    for p in sorted(BACKUPS.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        out.append({
            "filename": p.name,
            "created_at": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(),
            "size": p.stat().st_size,
        })
    return jsonify(out)

@app.post("/api/cms/database/rollback")
@require_tier("TIER_1_ADMIN")
def cms_db_rollback():
    d = request.get_json(silent=True) or {}
    fn = secure_filename(d.get("filename", ""))
    p = BACKUPS / fn
    if not p.exists():
        return jsonify({"error": "Backup not found"}), 404
    data = json.loads(p.read_text())
    # auto-snapshot before rollback
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    pre = f"prerollback_{ts}.json"
    payload = {e: all_(e) for e in ENTITIES}
    payload.update(reference_data=db.session.get(Setting, "reference_data").value,
                   system_settings=db.session.get(Setting, "system_settings").value,
                   branding=get_branding())
    (BACKUPS / pre).write_text(json.dumps(payload, indent=2))
    # apply
    db.session.query(Record).delete()
    db.session.query(Setting).delete()
    db.session.query(Counter).delete()
    for e in ENTITIES:
        for x in data.get(e, []):
            put(e, x)
    if "reference_data" in data:
        db.session.add(Setting(key="reference_data", value=data["reference_data"]))
    if "system_settings" in data:
        db.session.add(Setting(key="system_settings", value=data["system_settings"]))
    if "branding" in data:
        db.session.add(Setting(key="branding", value=data["branding"]))
    db.session.commit()
    ensure_quick_access_users()
    audit("CMS_ROLLBACK", "SETTINGS", "db", old=None, new={"restored": fn, "presnapshot": pre})
    db.session.commit()
    return jsonify({"success": True, "restored": fn, "presnapshot": pre})

# ==================== PUBLIC SIGNUP ====================

@app.post("/api/public/signup")
def public_signup():
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    username = (d.get("username") or "").strip().lower()
    email = (d.get("email") or "").strip().lower()
    password = d.get("password") or ""
    phone = (d.get("phone") or "").strip()

    if not username or not password or not email:
        return jsonify({"error": "username, email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400
    if "@" not in email:
        return jsonify({"error": "invalid email"}), 400

    users = _raw("users")
    if any(str(u.get("username", "")).lower() == username for u in users):
        return jsonify({"error": "username already exists"}), 409
    if any(str(u.get("email", "")).lower() == email for u in users):
        return jsonify({"error": "email already exists"}), 409

    uid = f"USR-{len(users)+1:04d}"
    u = {
        "id": uid,
        "name": name or username.title(),
        "username": username,
        "email": email,
        "phone": phone,
        "role": "PUBLIC_USER",
        "role_title": "Public User",
        "department": "Public",
        "password_hash": generate_password_hash(password),
        "active": True,
        "quick_access": False,
        "created_at": now(),
    }
    put("users", u)
    audit("PUBLIC_SIGNUP", "SETTINGS", uid, None, {"username": username, "email": email})
    notify("New user registration",
           f"{username} ({email}) signed up and is awaiting role assignment.",
           "USER", None, priority="NORMAL")
    db.session.commit()
    return jsonify({"success": True, "user": _clean(u),
                    "message": "Account created. An administrator will assign your role."}), 201

'''

    src = src.replace(
        '# ==================== SPA FALLBACK ====================',
        cms_block + '\n# ==================== SPA FALLBACK ===================='
    )
    ap.write_text(src, encoding="utf-8")
    print("app.py: added CMS + signup endpoints")

print("\nDONE. Now restart Flask.")