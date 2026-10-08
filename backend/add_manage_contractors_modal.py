"""
Create ManageContractorsModal.tsx — full CRUD for contractors.
Patch ProjectModal.tsx to render it via a "Manage" button.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODAL = ROOT / "src" / "components" / "projects" / "ProjectModal.tsx"
MANAGE = ROOT / "src" / "components" / "projects" / "ManageContractorsModal.tsx"

# ============================================================
# CREATE — ManageContractorsModal.tsx
# ============================================================
print("=" * 60)
print("CREATE: ManageContractorsModal.tsx")
print("=" * 60)

if MANAGE.exists():
    print("  Already exists — skipping.")
else:
    MANAGE.write_text('''import React, { useState, useEffect } from 'react';
import { X, Plus, Save, Trash2, Building2, Search } from 'lucide-react';
import { api } from '../../services/api.ts';
import { Contractor } from '../../types/index.ts';

interface ManageContractorsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onChanged?: () => void;
}

const EMPTY: Partial<Contractor> = {
  name: '',
  registration_no: '',
  category: 'Regional Contractor',
  specialties: [],
  contact_person: '',
  phone: '',
  email: '',
  address: '',
  state: 'Edo',
  active: true,
  rating: 0,
};

export const ManageContractorsModal: React.FC<ManageContractorsModalProps> = ({
  isOpen,
  onClose,
  onChanged
}) => {
  const [list, setList] = useState<Contractor[]>([]);
  const [selected, setSelected] = useState<Contractor | null>(null);
  const [draft, setDraft] = useState<Partial<Contractor>>(EMPTY);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');

  const refresh = async () => {
    try {
      const all = await api.getAllContractors();
      setList(all || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load contractors');
    }
  };

  useEffect(() => {
    if (isOpen) {
      refresh();
      setDraft(EMPTY);
      setSelected(null);
      setSearch('');
      setError('');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const filtered = list.filter(c => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      c.name?.toLowerCase().includes(q) ||
      c.registration_no?.toLowerCase().includes(q) ||
      c.category?.toLowerCase().includes(q) ||
      c.state?.toLowerCase().includes(q)
    );
  });

  const selectContractor = (c: Contractor) => {
    setSelected(c);
    setDraft({ ...c });
    setError('');
  };

  const newContractor = () => {
    setSelected(null);
    setDraft({ ...EMPTY });
    setError('');
  };

  const save = async () => {
    setError('');
    if (!draft.name?.trim()) {
      setError('Company name is required.');
      return;
    }
    setBusy(true);
    try {
      if (selected) {
        const updated = await api.updateContractor(selected.id, draft);
        setSelected(updated);
        setDraft({ ...updated });
      } else {
        const created = await api.createContractor(draft);
        setSelected(created);
        setDraft({ ...created });
      }
      await refresh();
      onChanged?.();
    } catch (err: any) {
      setError(err.message || 'Save failed');
    } finally {
      setBusy(false);
    }
  };

  const remove = async () => {
    if (!selected) return;
    const confirmed = window.confirm(
      `Deactivate "${selected.name}"?\\n\\nThe contractor will be removed from new project dropdowns but remains in historical records for audit.\\n\\nYou can reactivate it later by editing and setting Active = yes.`
    );
    if (!confirmed) return;
    setBusy(true);
    try {
      await api.deleteContractor(selected.id);
      setSelected(null);
      setDraft(EMPTY);
      await refresh();
      onChanged?.();
    } catch (err: any) {
      setError(err.message || 'Deactivate failed');
    } finally {
      setBusy(false);
    }
  };

  const set = (k: keyof Contractor) => (e: any) =>
    setDraft(prev => ({ ...prev, [k]: e.target.value }));

  return (
    <div className="fixed inset-0 z-[70] overflow-y-auto bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-5xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200 text-xs">
        {/* Header */}
        <div className="px-5 py-4 bg-emerald-950 text-white flex items-center justify-between border-b border-emerald-900">
          <div className="flex items-center space-x-2">
            <Building2 className="w-5 h-5 text-amber-300" />
            <div>
              <h2 className="text-sm font-bold">Manage Contractors</h2>
              <p className="text-[11px] text-emerald-300">
                Register, edit, or deactivate civil engineering firms
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body: two columns */}
        <div className="flex-1 overflow-hidden flex flex-col md:flex-row">
          {/* LEFT: List */}
          <div className="md:w-1/2 border-r border-slate-200 flex flex-col overflow-hidden">
            <div className="p-3 border-b border-slate-200 bg-slate-50 space-y-2">
              <button
                onClick={newContractor}
                className="w-full px-3 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white font-semibold inline-flex items-center justify-center gap-1.5"
              >
                <Plus className="w-4 h-4" /> New Contractor
              </button>
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Search by name, RC, category, state…"
                  className="w-full pl-8 pr-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
              {filtered.length === 0 && (
                <div className="p-6 text-center text-slate-400">No contractors match.</div>
              )}
              {filtered.map(c => {
                const isActive = c.active !== false;
                const isSelected = selected?.id === c.id;
                return (
                  <button
                    key={c.id}
                    onClick={() => selectContractor(c)}
                    className={`w-full text-left px-3 py-2.5 hover:bg-slate-50 transition-colors ${
                      isSelected ? 'bg-emerald-50 border-l-4 border-emerald-600' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <div className="font-semibold text-slate-900 truncate">{c.name}</div>
                        <div className="text-[11px] text-slate-500 truncate">
                          {c.registration_no || c.id} · {c.category || '—'}
                        </div>
                        <div className="text-[10px] text-slate-400 truncate">
                          {c.state || ''} {c.contact_person ? `· ${c.contact_person}` : ''}
                        </div>
                      </div>
                      {!isActive && (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-100 text-rose-700 uppercase">
                          Inactive
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* RIGHT: Form */}
          <div className="md:w-1/2 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-slate-800">
                  {selected ? `Editing: ${selected.name}` : 'New Contractor'}
                </h3>
                {selected && (
                  <span className="text-[11px] text-slate-500 font-mono">{selected.id}</span>
                )}
              </div>

              {error && (
                <div className="rounded-lg bg-rose-50 border border-rose-200 text-rose-800 p-2.5">{error}</div>
              )}

              <label className="block">
                <span className="font-semibold text-slate-700">Company Name *</span>
                <input
                  value={draft.name || ''}
                  onChange={set('name')}
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                />
              </label>

              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="font-semibold text-slate-700">RC Number</span>
                  <input
                    value={draft.registration_no || ''}
                    onChange={set('registration_no')}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  />
                </label>
                <label className="block">
                  <span className="font-semibold text-slate-700">Category</span>
                  <select
                    value={draft.category || 'Regional Contractor'}
                    onChange={set('category')}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  >
                    <option>Major Civil Works</option>
                    <option>Specialist Engineering</option>
                    <option>Regional Contractor</option>
                    <option>Consultancy</option>
                  </select>
                </label>
              </div>

              <label className="block">
                <span className="font-semibold text-slate-700">Contact Person</span>
                <input
                  value={draft.contact_person || ''}
                  onChange={set('contact_person')}
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                />
              </label>

              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="font-semibold text-slate-700">Phone</span>
                  <input
                    value={draft.phone || ''}
                    onChange={set('phone')}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  />
                </label>
                <label className="block">
                  <span className="font-semibold text-slate-700">Email</span>
                  <input
                    type="email"
                    value={draft.email || ''}
                    onChange={set('email')}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  />
                </label>
              </div>

              <label className="block">
                <span className="font-semibold text-slate-700">Address</span>
                <input
                  value={draft.address || ''}
                  onChange={set('address')}
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                />
              </label>

              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="font-semibold text-slate-700">State</span>
                  <input
                    value={draft.state || ''}
                    onChange={set('state')}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  />
                </label>
                <label className="block">
                  <span className="font-semibold text-slate-700">Active</span>
                  <select
                    value={draft.active === false ? 'no' : 'yes'}
                    onChange={e => setDraft(prev => ({ ...prev, active: e.target.value === 'yes' }))}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  >
                    <option value="yes">Yes</option>
                    <option value="no">No (deactivate)</option>
                  </select>
                </label>
              </div>
            </div>

            {/* Footer */}
            <div className="px-4 py-3 border-t border-slate-200 flex items-center justify-between gap-2">
              <div>
                {selected && (
                  <button
                    onClick={remove}
                    disabled={busy || selected.active === false}
                    className="px-3 py-1.5 rounded-lg text-[11px] font-bold bg-rose-700 hover:bg-rose-800 text-white disabled:opacity-40 inline-flex items-center gap-1"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    {selected.active === false ? 'Deactivated' : 'Deactivate'}
                  </button>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={onClose}
                  className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700"
                >
                  Close
                </button>
                <button
                  onClick={save}
                  disabled={busy}
                  className="px-4 py-1.5 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white disabled:opacity-50 inline-flex items-center gap-1.5"
                >
                  <Save className="w-3.5 h-3.5" />
                  {busy ? 'Saving…' : selected ? 'Save Changes' : 'Create Contractor'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
''', encoding="utf-8")
    print(f"  Created {MANAGE.name}")

# ============================================================
# PATCH — ProjectModal.tsx
# ============================================================
print()
print("=" * 60)
print("PATCH: ProjectModal.tsx")
print("=" * 60)

text = MODAL.read_text(encoding="utf-8")

if "ManageContractorsModal" in text:
    print("  Already patched — skipping.")
else:
    # 1. Import
    old_import = "import { ContractorModal } from './ContractorModal.tsx';"
    if old_import in text:
        # Replace the old single-add modal with the full manager
        text = text.replace(
            old_import,
            "import { ManageContractorsModal } from './ManageContractorsModal.tsx';",
            1,
        )
        print("  Swapped ContractorModal import for ManageContractorsModal")
    else:
        # Fallback: add after api import
        old = "import { api } from '../../services/api.ts';"
        if old in text:
            text = text.replace(
                old,
                old + "\nimport { ManageContractorsModal } from './ManageContractorsModal.tsx';",
                1,
            )
            print("  Imported ManageContractorsModal")

    # 2. Rename state
    if "showContractorModal" in text and "showManageContractors" not in text:
        text = text.replace("showContractorModal", "showManageContractors")
        print("  Renamed showContractorModal -> showManageContractors")

    # 3. Replace old ContractorModal JSX with ManageContractorsModal
    import re
    old_jsx_pattern = r"<ContractorModal[\s\S]*?/>"
    match = re.search(old_jsx_pattern, text)
    if match:
        new_jsx = """<ManageContractorsModal
        isOpen={showManageContractors}
        onClose={() => setShowManageContractors(false)}
        onChanged={async () => {
          // Refresh the contractor list after any change
          try {
            const list = await api.getContractors();
            setContractorList(list || []);
          } catch (err) {
            console.error('Failed to refresh contractors:', err);
          }
        }}
      />"""
        text = text[:match.start()] + new_jsx + text[match.end():]
        print("  Replaced ContractorModal JSX with ManageContractorsModal")
    else:
        print("  WARNING: no <ContractorModal ... /> JSX found")

    # 4. Update the trigger button text
    old_btn = """                <button
                  type="button"
                  onClick={() => setShowManageContractors(true)}
                  className="mt-2 inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 hover:text-emerald-900"
                >
                  <span className="text-base leading-none">+</span>
                  Add New Contractor
                </button>"""
    new_btn = """                <button
                  type="button"
                  onClick={() => setShowManageContractors(true)}
                  className="mt-2 inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 hover:text-emerald-900"
                >
                  ⚙️ Manage Contractors
                </button>"""
    if old_btn in text:
        text = text.replace(old_btn, new_btn, 1)
        print("  Updated trigger button label to '⚙️ Manage Contractors'")
    else:
        # Loose match
        idx = text.find("Add New Contractor")
        if idx != -1:
            text = text.replace("Add New Contractor", "⚙️ Manage Contractors", 1)
            print("  Updated trigger button label (loose match)")

    MODAL.write_text(text, encoding="utf-8")

print()
print("=" * 60)
print("COMPLETE")
print("=" * 60)
print("""
Next:
  1. npx tsc --noEmit
  2. Restart Flask:
       Get-NetTCPConnection -LocalPort 5000 -State Listen |
         ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
       py -3.12 backend\\app.py
  3. Reload browser (Ctrl+Shift+R)
  4. Open Create New Project
  5. Click "⚙️ Manage Contractors" next to the dropdown
  6. Manage modal opens with full list + edit form
""")