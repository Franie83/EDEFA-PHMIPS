"""
Programmatic patch of frontend files to support edit/delete.

Patches:
  1. src/types/tiers.ts — add canEdit() and canDelete() helpers
  2. src/services/api.ts — add updateHazard, deleteHazard, updateProject,
     deleteProject, updateSite, deleteSite, updateIntervention,
     deleteIntervention, deleteAction

Idempotent — safe to run multiple times.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIERS = ROOT / "src" / "types" / "tiers.ts"
API = ROOT / "src" / "services" / "api.ts"

if not TIERS.exists():
    raise SystemExit(f"Not found: {TIERS}")
if not API.exists():
    raise SystemExit(f"Not found: {API}")

# ============================================================
# PATCH 1 — src/types/tiers.ts
# ============================================================
print("=" * 60)
print("PATCH 1: src/types/tiers.ts")
print("=" * 60)

tiers_text = TIERS.read_text(encoding="utf-8")

HELPERS = """

// T1 + T2 can edit and delete — Auditor is read-only so it's excluded
export function canEdit(role: string | undefined | null): boolean {
  const tier = tierOf(role);
  if (!tier) return false;
  if (isReadonly(role)) return false;
  return tier === 'TIER_1_ADMIN' || tier === 'TIER_2_EXEC';
}

export function canDelete(role: string | undefined | null): boolean {
  return canEdit(role);
}
"""

if "export function canEdit(" in tiers_text:
    print("  Already patched — skipping.")
else:
    tiers_text = tiers_text.rstrip() + "\n" + HELPERS
    TIERS.write_text(tiers_text, encoding="utf-8")
    print(f"  Appended canEdit() and canDelete() to {TIERS.name}")

# ============================================================
# PATCH 2 — src/services/api.ts
# ============================================================
print()
print("=" * 60)
print("PATCH 2: src/services/api.ts")
print("=" * 60)

api_text = API.read_text(encoding="utf-8")

# Each patch is (anchor, insert_after_marker, snippet, description)
PATCHES = [
    (
        "updateHazard",
        "  bulkVerifyHazards:",
        """  updateHazard: (id: string, data: Partial<Hazard>) => request<Hazard>(`/hazards/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  deleteHazard: (id: string) => request<{ success: boolean; deleted_id: string }>(`/hazards/${id}`, {
    method: 'DELETE'
  }),
""",
        "hazard update/delete methods",
    ),
    (
        "deleteIntervention",
        "  updateIntervention:",
        """  deleteIntervention: (id: string) => request<{ success: boolean; deleted_id: string }>(`/interventions/${id}`, {
    method: 'DELETE'
  }),
""",
        "intervention delete method",
    ),
    (
        "updateProject",
        "  createProject:",
        """  updateProject: (id: string, data: Partial<Project>) => request<Project>(`/projects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  deleteProject: (id: string) => request<{ success: boolean; deleted_id: string }>(`/projects/${id}`, {
    method: 'DELETE'
  }),
""",
        "project update/delete methods",
    ),
    (
        "updateSite",
        "  createSite:",
        """  updateSite: (id: string, data: Partial<Site>) => request<Site>(`/sites/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  deleteSite: (id: string) => request<{ success: boolean; deleted_id: string }>(`/sites/${id}`, {
    method: 'DELETE'
  }),
""",
        "site update/delete methods",
    ),
    (
        "deleteAction",
        "  updateAction:",
        """  deleteAction: (id: string) => request<{ success: boolean; deleted_id: string }>(`/actions/${id}`, {
    method: 'DELETE'
  }),
""",
        "action delete method",
    ),
]

for marker, anchor, snippet, desc in PATCHES:
    if marker in api_text:
        print(f"  Already present: {desc}")
        continue
    if anchor not in api_text:
        print(f"  WARNING: anchor not found for {desc}: {anchor!r}")
        continue
    # Find end of the anchor function block — the next occurrence of a blank line
    # followed by two-space indentation (start of next method)
    idx = api_text.find(anchor)
    # Find the next line that begins with "  " and a letter (next method def)
    # We'll insert right after the anchor's block. Simpler: insert after the
    # first occurrence of "  },\n" that follows the anchor
    search_from = idx
    insert_at = -1
    while True:
        close = api_text.find("  },\n", search_from)
        if close == -1:
            break
        insert_at = close + len("  },\n")
        break
    if insert_at == -1:
        print(f"  WARNING: could not find insertion point for {desc}")
        continue
    api_text = api_text[:insert_at] + snippet + api_text[insert_at:]
    print(f"  Inserted: {desc}")

API.write_text(api_text, encoding="utf-8")

print()
print("=" * 60)
print("PATCH COMPLETE")
print("=" * 60)
print(f"  {TIERS}")
print(f"  {API}")
print("\nNext: verify with npx tsc --noEmit")