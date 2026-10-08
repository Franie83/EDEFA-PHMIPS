"""
Add the approval methods to src/services/api.ts.

The earlier migration tried to insert them but the anchor didn't match,
so the methods were never added. This script inserts them cleanly.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "src" / "services" / "api.ts"

if not API.exists():
    raise SystemExit(f"Not found: {API}")

text = API.read_text(encoding="utf-8")

if "directorApproveIntervention" in text and "executiveApproveProject" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

METHODS = """  // Approval flow — Stage 1: Intervention approvals
  directorApproveIntervention: (id: string, notes?: string) =>
    request<{ success: boolean; intervention: Intervention }>(`/interventions/${id}/director-approve`, {
      method: 'POST',
      body: JSON.stringify({ notes })
    }),
  executiveApproveIntervention: (id: string, notes?: string, approved_amount_ngn?: number) =>
    request<{ success: boolean; intervention: Intervention }>(`/interventions/${id}/executive-approve`, {
      method: 'POST',
      body: JSON.stringify({ notes, approved_amount_ngn })
    }),
  rejectIntervention: (id: string, rejection_reason: string) =>
    request<{ success: boolean; intervention: Intervention }>(`/interventions/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ rejection_reason })
    }),
  getInterventionsByQueue: (queue: 'director' | 'executive' | 'approved') => {
    const q = new URLSearchParams({ queue }).toString();
    return request<Intervention[]>(`/interventions?${q}`);
  },

  // Approval flow — Stage 2: Project approvals
  executiveApproveProject: (id: string, notes?: string, approved_amount_ngn?: number) =>
    request<{ success: boolean; project: Project }>(`/projects/${id}/executive-approve`, {
      method: 'POST',
      body: JSON.stringify({ notes, approved_amount_ngn })
    }),
  getProjectsByQueue: (queue: 'approval') => {
    const q = new URLSearchParams({ queue }).toString();
    return request<Project[]>(`/projects?${q}`);
  },

"""

# Anchor on getInterventions, insert right before it
anchor = "  getInterventions: () => request<Intervention[]>('/interventions'),"

if anchor not in text:
    raise SystemExit("anchor not found in api.ts — paste the file's top 250 lines")

text = text.replace(anchor, METHODS + anchor, 1)
API.write_text(text, encoding="utf-8")
print(f"Patched {API.name}")
print("  Inserted 6 approval/queue methods before getInterventions")