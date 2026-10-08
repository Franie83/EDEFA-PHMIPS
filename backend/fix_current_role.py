"""
Fix ActionTracking.tsx:
1. Add currentUser prop to the interface + destructure
2. Read currentRole from currentUser.role (not from window globals)
3. Wire currentUser from App.tsx
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "src" / "App.tsx"
ACTIONS = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

# ============================================================
# 1. Fix currentRole line
# ============================================================
at = ACTIONS.read_text(encoding="utf-8")

OLD_ROLE = "const currentRole = (window as any).__EDEFA_ROLE__ || (window as any).currentUser?.role || '';"
NEW_ROLE = "const currentRole = currentUser?.role || '';"

if OLD_ROLE in at:
    at = at.replace(OLD_ROLE, NEW_ROLE, 1)
    print("  Replaced window-based currentRole with prop-based")
elif NEW_ROLE in at:
    print("  currentRole already correct")
else:
    print("  WARNING: could not find currentRole line")

# ============================================================
# 2. Add currentUser to interface (if missing)
# ============================================================
if "currentUser?:" not in at:
    m = re.search(r"interface ActionTrackingProps\s*\{", at)
    if m:
        at = at[:m.end()] + "\n  currentUser?: { role?: string; name?: string; id?: string } | null;" + at[m.end():]
        print("  Added currentUser to interface")
    else:
        print("  WARNING: could not find ActionTrackingProps interface")
else:
    print("  currentUser already in interface")

# ============================================================
# 3. Add currentUser to destructure (if missing)
# ============================================================
if not re.search(r"=\s*\(\{\s*currentUser\s*,", at):
    # Look for the destructure pattern
    m = re.search(r"export const ActionTracking: React\.FC<ActionTrackingProps>\s*=\s*\(\{", at)
    if m:
        at = at[:m.end()] + "\n  currentUser," + at[m.end():]
        print("  Added currentUser to destructure")
    else:
        print("  WARNING: could not find destructure")
else:
    print("  currentUser already in destructure")

ACTIONS.write_text(at, encoding="utf-8")

# ============================================================
# 4. Wire currentUser from App.tsx
# ============================================================
app = APP.read_text(encoding="utf-8")

m = re.search(r"<ActionTracking[\s\S]{0,400}?/>", app)
if m:
    block = m.group(0)
    if "currentUser=" not in block:
        new_block = block.replace("<ActionTracking", "<ActionTracking\n                currentUser={currentUser}", 1)
        app = app.replace(block, new_block, 1)
        APP.write_text(app, encoding="utf-8")
        print("  Passed currentUser from App.tsx to ActionTracking")
    else:
        print("  currentUser already passed from App.tsx")
else:
    print("  WARNING: could not find <ActionTracking> in App.tsx")

print()
print("Done.")