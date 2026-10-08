"""
Allow TIER_3_DIRECTOR to edit projects (in addition to T1 + T2).

Rationale: Directors create projects and must be able to edit them when
Executive rejects them. Without this, the rejection cycle can't complete.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_PY = ROOT / "backend" / "app.py"
PERMS_PY = ROOT / "backend" / "permissions.py"

# 1. Patch permissions.py to add require_edit_project
perms = PERMS_PY.read_text(encoding="utf-8")

if "require_project_edit" not in perms:
    addition = '''

def require_project_edit():
    """Allow T1, T2, and T3 to edit projects.

    Distinct from require_edit() because projects need a looser rule —
    Directors create projects and must be able to fix rejected ones.
    Auditor is still excluded (read-only).
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = session.get("role", "")
            t = tier_of(role)
            if t not in ("TIER_1_ADMIN", "TIER_2_EXEC", "TIER_3_DIRECTOR"):
                logger.warning("DENIED project-edit %s: role=%s", fn.__name__, role)
                return jsonify({
                    "error": "Only Super Admin, Executive, or Director can edit projects",
                    "your_role": role,
                    "your_tier": t,
                }), 403
            if is_readonly(role):
                return jsonify({"error": "Read-only role", "your_role": role}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
'''
    perms = perms.rstrip() + addition
    PERMS_PY.write_text(perms, encoding="utf-8")
    print("  Added require_project_edit to permissions.py")
else:
    print("  require_project_edit already present")

# 2. Patch app.py — swap the decorator on project_update
app = APP_PY.read_text(encoding="utf-8")

# Import the new decorator
old_import = "    require_edit, require_delete, can_edit_or_delete,"
if old_import in app and "require_project_edit" not in app.split("# ==================== PROJECTS")[0]:
    new_import = "    require_edit, require_delete, can_edit_or_delete,\n    require_project_edit,"
    app = app.replace(old_import, new_import, 1)
    print("  Imported require_project_edit into app.py")

# Replace the decorator on project_update
old_update = '''@app.put("/api/projects/<id>")
@require_edit()
def project_update(id):'''
new_update = '''@app.put("/api/projects/<id>")
@require_project_edit()
def project_update(id):'''

if old_update in app:
    app = app.replace(old_update, new_update, 1)
    print("  project_update now uses @require_project_edit (T1 + T2 + T3)")
else:
    print("  WARNING: project_update decorator not found in expected form")

APP_PY.write_text(app, encoding="utf-8")
print()
print("Done. Restart Flask and Directors can now edit projects.")