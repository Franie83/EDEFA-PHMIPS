import pathlib

p = pathlib.Path("backend/permissions.py")
src = p.read_text(encoding="utf-8")

# --- Fix 1: require_director_approve missing return block ---
old1 = """            if is_readonly(role):
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_exec_approve():"""

new1 = """            if is_readonly(role):
                return jsonify({"error": "Read-only role", "your_role": role}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_exec_approve():"""

# --- Fix 2: require_exec_approve malformed if block ---
old2 = """            role = session.get("role", "")
            t = tier_of(role)
                logger.warning("DENIED exec-approve %s: role=%s", fn.__name__, role)
                return jsonify({
                    "error": "Only Executive or Super Admin can approve at the Executive stage",
                    "your_role": role,
                    "your_tier": t,
                }), 403
            if is_readonly(role):"""

new2 = """            role = session.get("role", "")
            t = tier_of(role)
            if t not in EXEC_APPROVE_TIERS:
                logger.warning("DENIED exec-approve %s: role=%s", fn.__name__, role)
                return jsonify({
                    "error": "Only Executive or Super Admin can approve at the Executive stage",
                    "your_role": role,
                    "your_tier": t,
                }), 403
            if is_readonly(role):"""

changes = []
if old1 in src:
    src = src.replace(old1, new1)
    changes.append("fixed require_director_approve missing return")
elif new1 in src:
    changes.append("require_director_approve already correct")
else:
    changes.append("require_director_approve pattern not found")

if old2 in src:
    src = src.replace(old2, new2)
    changes.append("fixed require_exec_approve malformed if")
elif new2 in src:
    changes.append("require_exec_approve already correct")
else:
    changes.append("require_exec_approve pattern not found")

p.write_text(src, encoding="utf-8")
print("changes:", changes)

# Verify syntax
import ast
ast.parse(src)
print("SYNTAX OK")