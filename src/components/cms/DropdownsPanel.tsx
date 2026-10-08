import React, { useEffect, useState } from 'react';
import {
  Tag, MapPin, Plus, Trash2, Pencil, Check, X,
  ChevronDown, ChevronRight, RefreshCw, ListChecks
} from 'lucide-react';
import { api } from '../../services/api';

const LABELS: Record<string, string> = {
  hazard_categories: 'Hazard Categories',
  hazard_types: 'Specific Hazard Types',
  severities: 'Severity Levels',
  urgencies: 'Urgency Levels',
  reporter_types: 'Reporter Categories',
  priorities: 'Priorities',
  funding_sources: 'Funding Sources',
  departments: 'Departments',
  implementing_agencies: 'Implementing Agencies',
  inspection_stages: 'Inspection Stages',
  intervention_types: 'Intervention Types',
  project_categories: 'Project Categories',
};

export const DropdownsPanel: React.FC = () => {
  const [lists, setLists] = useState<Record<string, string[]>>({});
  const [states, setStates] = useState<Record<string, string[]>>({});
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const [listData, full] = await Promise.all([
        api.cmsRefListKeys(),
        api.cmsFullReferenceData(),
      ]);
      setLists(listData || {});
      setStates(full?.states_and_lgas || {});
    } catch (e: any) {
      alert(e.message || 'Failed to load reference data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) {
    return <div className="p-6 text-slate-400 text-sm">Loading dropdown data…</div>;
  }

  // Sort keys by predefined order, then alphabetically
  const orderedKeys = Object.keys(lists).sort((a, b) => {
    const order = Object.keys(LABELS);
    const ai = order.indexOf(a), bi = order.indexOf(b);
    if (ai === -1 && bi === -1) return a.localeCompare(b);
    if (ai === -1) return 1;
    if (bi === -1) return -1;
    return ai - bi;
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">Dropdown Management</h3>
          <p className="text-xs text-slate-400">
            Add, update and delete values used across every dropdown in the system.
          </p>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 text-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Reload
        </button>
      </div>

      {orderedKeys.map((key) => (
        <Section
          key={key}
          title={LABELS[key] || key}
          icon={<ListChecks className="w-4 h-4" />}
          count={lists[key].length}
        >
          <SimpleListEditor
            items={lists[key]}
            placeholder={`Add new ${LABELS[key] || key}…`}
            onAdd={async (name) => {
              await api.cmsRefListAdd(key, name);
              await load();
            }}
            onUpdate={async (oldName, newName) => {
              await api.cmsRefListUpdate(key, oldName, newName);
              await load();
            }}
            onDelete={async (name) => {
              await api.cmsRefListDelete(key, name);
              await load();
            }}
          />
        </Section>
      ))}

      {/* States & LGAs — special two-level editor */}
      <Section
        title="States & LGAs"
        icon={<MapPin className="w-4 h-4" />}
        count={Object.keys(states).length}
      >
        <div className="space-y-3">
          {Object.entries(states).map(([stateName, lgas]) => (
            <StateBlock
              key={stateName}
              stateName={stateName}
              lgas={lgas}
              onAddLga={async (name) => {
                await api.cmsAddLga(stateName, name);
                await load();
              }}
              onDeleteLga={async (name) => {
                await api.cmsDeleteLga(stateName, name);
                await load();
              }}
              onDeleteState={async () => {
                const _lgaCount = Array.isArray(lgas) ? (lgas as any[]).length : 0;
                if (!window.confirm(`Delete state "${stateName}" and all ${_lgaCount} of its LGAs?`)) return;
                await api.cmsDeleteState(stateName);
                await load();
              }}
            />
          ))}
          <AddInline
            placeholder="Add a new state (e.g. Lagos)"
            onAdd={async (name) => {
              await api.cmsAddState(name);
              await load();
            }}
          />
        </div>
      </Section>

      <div className="rounded-lg border border-amber-900/40 bg-amber-950/20 p-3 text-[11px] text-amber-200">
        Changes take effect immediately across the entire application. Every add, update or delete is audit-logged.
      </div>
    </div>
  );
};

// ==================================================================
// Section wrapper — collapsible card
// ==================================================================
const Section: React.FC<{
  title: string;
  icon: React.ReactNode;
  count?: number;
  children: React.ReactNode;
}> = ({ title, icon, count, children }) => {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-slate-800/30"
      >
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-100">
          {open ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
          {icon}
          {title}
          {typeof count === 'number' && (
            <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300">
              {count}
            </span>
          )}
        </div>
      </button>
      {open && <div className="px-4 pb-4">{children}</div>}
    </div>
  );
};

// ==================================================================
// Simple string-list editor
// ==================================================================
const SimpleListEditor: React.FC<{
  items: string[];
  placeholder?: string;
  onAdd: (name: string) => Promise<void>;
  onUpdate: (oldName: string, newName: string) => Promise<void>;
  onDelete: (name: string) => Promise<void>;
}> = ({ items, placeholder, onAdd, onUpdate, onDelete }) => {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editingValue, setEditingValue] = useState('');

  return (
    <div className="space-y-1">
      {items.map((item, i) => (
        <div key={item} className="flex items-center justify-between rounded-lg bg-slate-900 border border-slate-800 px-3 py-2">
          {editingIndex === i ? (
            <input
              autoFocus
              value={editingValue}
              onChange={(e) => setEditingValue(e.target.value)}
              className="flex-1 bg-slate-950 border border-slate-700 rounded px-2 py-1 text-sm text-slate-100"
              onKeyDown={(e) => {
                if (e.key === 'Enter') onUpdate(item, editingValue).then(() => setEditingIndex(null));
                else if (e.key === 'Escape') setEditingIndex(null);
              }}
            />
          ) : (
            <span className="text-sm text-slate-200">{item}</span>
          )}
          <div className="flex items-center gap-1 ml-2">
            {editingIndex === i ? (
              <>
                <button onClick={() => onUpdate(item, editingValue).then(() => setEditingIndex(null))} className="p-1 rounded text-emerald-400 hover:bg-slate-800" title="Save">
                  <Check className="w-3.5 h-3.5" />
                </button>
                <button onClick={() => setEditingIndex(null)} className="p-1 rounded text-slate-400 hover:bg-slate-800" title="Cancel">
                  <X className="w-3.5 h-3.5" />
                </button>
              </>
            ) : (
              <>
                <button onClick={() => { setEditingIndex(i); setEditingValue(item); }} className="p-1 rounded text-slate-400 hover:bg-slate-800 hover:text-slate-200" title="Edit">
                  <Pencil className="w-3.5 h-3.5" />
                </button>
                <button onClick={() => { if (window.confirm(`Delete "${item}"?`)) onDelete(item); }} className="p-1 rounded text-rose-400 hover:bg-rose-950/50" title="Delete">
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </>
            )}
          </div>
        </div>
      ))}
      <AddInline placeholder={placeholder || 'Add new…'} onAdd={onAdd} />
    </div>
  );
};

// ==================================================================
// Add-inline input
// ==================================================================
const AddInline: React.FC<{
  placeholder: string;
  onAdd: (name: string) => Promise<void>;
}> = ({ placeholder, onAdd }) => {
  const [value, setValue] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    const v = value.trim();
    if (!v) return;
    setBusy(true);
    try {
      await onAdd(v);
      setValue('');
    } catch (e: any) {
      alert(e.message || 'Failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex gap-2 mt-2">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && submit()}
        placeholder={placeholder}
        className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-600"
      />
      <button onClick={submit} disabled={busy || !value.trim()} className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-xs font-medium disabled:opacity-50">
        <Plus className="w-3.5 h-3.5" /> Add
      </button>
    </div>
  );
};

// ==================================================================
// State block
// ==================================================================
const StateBlock: React.FC<{
  stateName: string;
  lgas: string[];
  onAddLga: (name: string) => Promise<void>;
  onDeleteLga: (name: string) => Promise<void>;
  onDeleteState: () => Promise<void>;
}> = ({ stateName, lgas, onAddLga, onDeleteLga, onDeleteState }) => {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60">
      <div className="flex items-center justify-between px-3 py-2">
        <button onClick={() => setOpen(!open)} className="flex items-center gap-2 text-sm font-medium text-slate-100 hover:text-emerald-300">
          {open ? <ChevronDown className="w-3.5 h-3.5 text-slate-400" /> : <ChevronRight className="w-3.5 h-3.5 text-slate-400" />}
          {stateName}
          <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-400">
  {Array.isArray(lgas) ? lgas.length : 0} LGAs
</span>
        </button>
        <button onClick={onDeleteState} className="p-1 rounded text-rose-400 hover:bg-rose-950/50" title="Delete state">
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
      {open && (
        <div className="border-t border-slate-800 p-3 space-y-1">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 mb-2">
            {lgas.map((lga) => (
              <div key={lga} className="flex items-center justify-between rounded bg-slate-950 border border-slate-800 px-2 py-1.5">
                <span className="text-xs text-slate-300">{lga}</span>
                <button onClick={() => { if (window.confirm(`Delete LGA "${lga}" from ${stateName}?`)) onDeleteLga(lga); }} className="p-1 rounded text-rose-400 hover:bg-rose-950/50">
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
          <AddInline placeholder={`Add LGA under ${stateName}`} onAdd={onAddLga} />
        </div>
      )}
    </div>
  );
};