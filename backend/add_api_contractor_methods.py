"""Add updateContractor and deleteContractor to api.ts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "services" / "api.ts"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "updateContractor:" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

anchor = """  getContractors: () => request<Contractor[]>('/contractors?active=1'),"""

new_block = """  getContractors: () => request<Contractor[]>('/contractors?active=1'),
  getAllContractors: () => request<Contractor[]>('/contractors'),
  updateContractor: (id: string, data: Partial<Contractor>) => request<Contractor>(`/contractors/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  deleteContractor: (id: string) => request<{ success: boolean; deactivated_id: string }>(`/contractors/${id}`, {
    method: 'DELETE'
  }),"""

if anchor not in text:
    raise SystemExit("getContractors anchor not found in api.ts")

text = text.replace(anchor, new_block, 1)
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Added getAllContractors")
print("  Added updateContractor")
print("  Added deleteContractor")