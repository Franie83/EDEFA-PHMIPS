import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  Database,
  Download,
  RefreshCw,
  RotateCcw,
  Save,
  Trash2,
} from 'lucide-react';
import { api } from '../../services/api';

type Backup = { filename: string; size: number; created_at: string };

export const DatabasePanel: React.FC = () => {
  const [stats, setStats] = useState<Record<string, number>>({});
  const [backups, setBackups] = useState<Backup[]>([]);
  const [label, setLabel] = useState('');
  const [busy, setBusy] = useState<string | null>(null);

  const load = async () => {
    try {
      const [s, b] = await Promise.all([api.cmsDbStats(), api.cmsDbBackups()]);
      setStats(s);
      setBackups(b);
    } catch (e: any) {
      alert(e.message);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const run = async (key: string, fn: () => Promise<any>) => {
    setBusy(key);
    try {
      const res = await fn();
      await load();
      if (res?.snapshot) alert(`Done. Auto-snapshot: ${res.snapshot}`);
      else if (res?.filename) alert(`Snapshot created: ${res.filename}`);
      else alert('Done.');
    } catch (e: any) {
      alert(e.message);
    } finally {
      setBusy(null);
    }
  };

  const confirmFlush = () => {
    const ans = window.prompt(
      'This empties all operational data. Quick-access logins and settings are kept.\n\nType FLUSH to confirm:'
    );
    if (ans !== 'FLUSH') return;
    run('flush', () => api.cmsDbFlush());
  };

  const confirmReseed = () => {
    if (
      !window.confirm(
        'Overwrite all data with seed_data.json? A safety snapshot will be created first.'
      )
    )
      return;
    run('reseed', () => api.cmsDbReseed());
  };

  const snapshot = () => run('snap', () => api.cmsDbSnapshot(label || 'manual'));

  const rollback = (b: Backup) => {
    if (
      !window.confirm(
        `Rollback to "${b.filename}"? Current data will be snapshotted first, then overwritten.`
      )
    )
      return;
    run('rollback-' + b.filename, () => api.cmsDbRollback(b.filename));
  };

  const entities = Object.entries(stats).filter(([k]) => !k.startsWith('_'));

  return (
    <div className="p-6 space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white">Database Management</h3>
        <p className="text-xs text-slate-400">
          Flush, reseed, snapshot and rollback. Every destructive action creates a safety snapshot
          first.
        </p>
      </div>

      {/* Record Counts */}
      <section>
        <h4 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
          <Database className="w-4 h-4" /> Record Counts
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {entities.length === 0 ? (
            <div className="col-span-full text-slate-500 text-sm">No stats available.</div>
          ) : (
            entities.map(([k, v]) => (
              <div
                key={k}
                className="bg-slate-900/60 border border-slate-800 rounded-lg px-3 py-3"
              >
                <div className="text-xs text-slate-500 truncate">{k.replace(/_/g, ' ')}</div>
                <div className="text-xl font-semibold text-white mt-1">{v}</div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Danger Zone */}
      <section>
        <h4 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" /> Danger Zone
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <DangerCard
            title="Flush Database"
            description="Empty all operational data. Quick-access users, settings and branding are preserved."
            icon={<Trash2 className="w-4 h-4" />}
            actionLabel="Flush"
            loading={busy === 'flush'}
            onClick={confirmFlush}
          />
          <DangerCard
            title="Reseed from seed_data.json"
            description="Overwrite all data with the original seed dataset. A snapshot is created first."
            icon={<RefreshCw className="w-4 h-4" />}
            actionLabel="Reseed"
            loading={busy === 'reseed'}
            onClick={confirmReseed}
          />
        </div>
      </section>

      {/* Create Snapshot */}
      <section>
        <h4 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
          <Save className="w-4 h-4" /> Create Snapshot
        </h4>
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            className="cms-input flex-1"
            placeholder="Optional label (e.g. before-migration)"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
          />
          <button
            onClick={snapshot}
            disabled={busy === 'snap'}
            className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-sm disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" /> {busy === 'snap' ? 'Working…' : 'Snapshot'}
          </button>
        </div>
      </section>

      {/* Backups */}
      <section>
        <h4 className="text-sm font-medium text-slate-300 mb-3">
          Backups ({backups.length})
        </h4>
        <div className="border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-900/70 text-slate-400 text-xs">
              <tr>
                <th className="text-left px-4 py-3 font-medium">File</th>
                <th className="text-left px-4 py-3 font-medium">Created</th>
                <th className="text-right px-4 py-3 font-medium">Size</th>
                <th className="text-right px-4 py-3 font-medium">Action</th>
              </tr>
            </thead>
            <tbody>
              {backups.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-6 text-center text-slate-500">
                    No backups yet.
                  </td>
                </tr>
              ) : (
                backups.map((b) => (
                  <tr key={b.filename} className="border-t border-slate-800">
                    <td className="px-4 py-3 text-slate-300 font-mono text-xs break-all">
                      {b.filename}
                    </td>
                    <td className="px-4 py-3 text-slate-500 text-xs whitespace-nowrap">
                      {new Date(b.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-slate-400 text-xs text-right whitespace-nowrap">
                      {(b.size / 1024).toFixed(1)} KB
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => rollback(b)}
                        disabled={!!busy}
                        className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs border border-slate-700 text-amber-300 hover:bg-amber-950/40 disabled:opacity-50"
                      >
                        <RotateCcw className="w-3 h-3" /> Rollback
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

const DangerCard: React.FC<{
  title: string;
  description: string;
  icon: React.ReactNode;
  actionLabel: string;
  loading: boolean;
  onClick: () => void;
}> = ({ title, description, icon, actionLabel, loading, onClick }) => (
  <div className="bg-rose-950/20 border border-rose-900/40 rounded-xl p-4">
    <div className="flex items-start gap-3">
      <div className="text-rose-400 mt-0.5">{icon}</div>
      <div className="flex-1">
        <div className="text-sm font-medium text-rose-200">{title}</div>
        <p className="text-xs text-rose-300/70 mt-1">{description}</p>
        <button
          onClick={onClick}
          disabled={loading}
          className="mt-3 px-3 py-1.5 rounded-lg bg-rose-800/60 hover:bg-rose-700 text-white text-xs disabled:opacity-50"
        >
          {loading ? 'Working…' : actionLabel}
        </button>
      </div>
    </div>
  </div>
);