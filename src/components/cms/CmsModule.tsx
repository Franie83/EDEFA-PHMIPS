import React, { useState } from 'react';
import { Palette, Users, Database, ListChecks } from 'lucide-react';
import { BrandingPanel } from './BrandingPanel.tsx';
import { UserManagementPanel } from './UserManagementPanel.tsx';
import { DatabasePanel } from './DatabasePanel.tsx';
import { DropdownsPanel } from './DropdownsPanel.tsx';

type Tab = 'branding' | 'users' | 'dropdowns' | 'database';

export const CmsModule: React.FC = () => {
  const [tab, setTab] = useState<Tab>('branding');

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'branding', label: 'Branding', icon: <Palette className="w-4 h-4" /> },
    { id: 'users', label: 'Users', icon: <Users className="w-4 h-4" /> },
    { id: 'dropdowns', label: 'Dropdowns', icon: <ListChecks className="w-4 h-4" /> },
    { id: 'database', label: 'Database', icon: <Database className="w-4 h-4" /> },
  ];

  return (
    <div className="min-h-full bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
      <div className="border-b border-slate-800 px-6 py-4 bg-slate-900/60">
        <h2 className="text-xl font-semibold text-white">Content Management System</h2>
        <p className="text-xs text-slate-500 mt-1">
          Super Administrator access only — branding, user accounts, dropdowns and database lifecycle.
        </p>
        <div className="flex gap-1 mt-4">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition cursor-pointer ${
                tab === t.id
                  ? 'bg-emerald-900/40 text-emerald-200 border border-emerald-800/60'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
              }`}
            >
              {t.icon}
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-y-auto">
        {tab === 'branding' && <BrandingPanel />}
        {tab === 'users' && <UserManagementPanel />}
        {tab === 'dropdowns' && <DropdownsPanel />}
        {tab === 'database' && <DatabasePanel />}
      </div>
    </div>
  );
};