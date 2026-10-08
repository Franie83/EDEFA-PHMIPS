"""
EDEFA-PHMIPS permission model.

Four tiers:
    TIER_1_ADMIN    <- SUPER_ADMIN
    TIER_2_EXEC     <- EXECUTIVE, AUDITOR
    TIER_3_DIRECTOR <- COORDINATOR, INSPECTOR
    TIER_4_STAFF    <- TECHNICAL_OFFICER, PLANNING_OFFICER

Capability model:
  * ALL tiers can READ, CREATE, VERIFY, ASSESS, RECOMMEND, REGISTER, LOG.
  * Only T1 + T2 can EDIT or DELETE (Auditor read-only).
  * Two-stage approval:
      - Stage 1a: Director approves intervention (T1 + T3)
      - Stage 1b: Executive approves intervention (T1 + T2)
      - Stage 2a: Director creates project (T1 + T3, requires Stage 1b)
      - Stage 2b: Executive approves project (T1 + T2)
  * Rejection returns an item to "Proposed" with a rejection_reason.
"""

import logging
from functools import wraps
from flask import jsonify, session

logger = logging.getLogger("ef-phmips.permissions")

TIER_MAP = {
    "SUPER_ADMIN":       "TIER_1_ADMIN",
    "EXECUTIVE":         "TIER_2_EXEC",
    "AUDITOR":           "TIER_2_EXEC",
    "COORDINATOR":       "TIER_3_DIRECTOR",
    "INSPECTOR":         "TIER_3_DIRECTOR",
    "TECHNICAL_OFFICER": "TIER_4_STAFF",
    "PLANNING_OFFICER":  "TIER_4_STAFF",
    "PUBLIC_USER":       "TIER_5_PUBLIC",
}

READONLY_ROLES = {"AUDITOR"}

TIER_LABELS = {
    "TIER_1_ADMIN":    "Super Admin",
    "TIER_2_EXEC":     "Executive (Admin)",
    "TIER_3_DIRECTOR": "Director",
    "TIER_4_STAFF":    "Staff",
    "TIER_5_PUBLIC":   "Public User",
}

LOGIN_GROUPS = [
    {"tier": "TIER_1_ADMIN",    "label": "Super Admin",       "roles": ["SUPER_ADMIN"]},
    {"tier": "TIER_2_EXEC",     "label": "Executive (Admin)", "roles": ["EXECUTIVE", "AUDITOR"]},
    {"tier": "TIER_3_DIRECTOR", "label": "Director",          "roles": ["COORDINATOR", "INSPECTOR"]},
    {"tier": "TIER_4_STAFF",    "label": "Staff",             "roles": ["TECHNICAL_OFFICER", "PLANNING_OFFICER"]},
]

EDIT_DELETE_TIERS = {"TIER_1_ADMIN", "TIER_2_EXEC"}
DB_ADMIN_TIERS = {"TIER_1_ADMIN"}

# Approval-specific tier sets
DIRECTOR_APPROVE_TIERS = {"TIER_1_ADMIN", "TIER_3_DIRECTOR"}
EXEC_APPROVE_TIERS = {"TIER_1_ADMIN", "TIER_2_EXEC"}


def tier_of(role: str) -> str:
    return TIER_MAP.get(role, "")


def is_readonly(role: str) -> bool:
    return role in READONLY_ROLES


def can_edit_or_delete(role: str) -> bool:
    t = tier_of(role)
    if t not in EDIT_DELETE_TIERS:
        return False
    if is_readonly(role):
        return False
    return True


# --- Decorators -------------------------------------------------------------

def require_tier(*allowed_tiers):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = session.get("role", "")
            t = tier_of(role)
            if t not in allowed_tiers:
                logger.warning("DENIED %s: role=%s tier=%s required=%s",
                               fn.__name__, role, t, allowed_tiers)
                return jsonify({
                    "error": "Forbidden",
                    "required_tiers": list(allowed_tiers),
                    "your_tier": t,
                    "your_role": role,
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_edit():
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = session.get("role", "")
            if not can_edit_or_delete(role):
                return jsonify({
                    "error": "Only Super Admin or Executive can edit records",
                    "your_role": role,
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_delete():
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = session.get("role", "")
            if not can_edit_or_delete(role):
                return jsonify({
                    "error": "Only Super Admin or Executive can delete records",
                    "your_role": role,
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_director_approve():
    """Director (T3) + Super Admin (T1). Not Executive, not Staff, not Auditor."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = session.get("role", "")
            t = tier_of(role)
            if t not in DIRECTOR_APPROVE_TIERS:
                logger.warning("DENIED director-approve %s: role=%s", fn.__name__, role)
                return jsonify({
                    "error": "Only Director or Super Admin can approve at the Director stage",
                    "your_role": role,
                    "your_tier": t,
                }), 403
            if is_readonly(role):
                return jsonify({"error": "Read-only role", "your_role": role}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_exec_approve():
    """Executive (T2) + Super Admin (T1). Not Director, not Staff, not Auditor."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = session.get("role", "")
            t = tier_of(role)
            if t not in EXEC_APPROVE_TIERS:
                logger.warning("DENIED exec-approve %s: role=%s", fn.__name__, role)
                return jsonify({
                    "error": "Only Executive or Super Admin can approve at the Executive stage",
                    "your_role": role,
                    "your_tier": t,
                }), 403
            if is_readonly(role):
                return jsonify({"error": "Read-only role", "your_role": role}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_login_strict():
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get("user_id"):
                return jsonify({"error": "Authentication required"}), 401
            return fn(*args, **kwargs)
        return wrapper
    return decorator

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
