import React, { useEffect, useState } from 'react';
import { Search, UserPlus, Edit2, Ban, Check, Trash2, KeyRound } from 'lucide-react';
import { api } from '../../services/api';

type CmsUser = {
  id: string;
  name: string;
  username: string;
  email: string;
  role: string;
  role_title?: string;
  department?: string;
  phone?: string;
  active: boolean;
  quick_access?: boolean;
  created_at?: string;
};

const ROLE_OPTIONS = [
  'PUBLIC_USER',
  'SUPER_ADMIN',
  'EXECUTIVE',
  'AUDITOR',
  'COORDINATOR',
  'INSPECTOR',
  'TECHNICAL_OFFICER',
  'PLANNING_OFFICER',
];

export const UserManagementPanel: React.FC = () => {
  const [users, setUsers] = useState<CmsUser[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<CmsUser | null>(null);
  const [creating, setCreating] = useState(false);
  const [resetFor, setResetFor] = useState<CmsUser | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      setUsers(await api.cmsUsers());
    } catch (e: any) {
      alert(e.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = users.filter((u) => {
    if (!query) return true;
    const q = query.toLowerCase();
    return (
      u.name?.toLowerCase().includes(q) ||
      u.username?.toLowerCase().includes(q) ||
      u.email?.toLowerCase().includes(q) ||
      u.role?.toLowerCase().includes(q)
    );
  });

  const toggleSuspend = async (u: CmsUser) => {
    const verb = u.active ? 'Suspend' : 'Reactivate';
    if (!window.confirm(`${verb} ${u.name || u.username}?`)) return;
    try {
      await api.cmsSuspendUser(u.id);
      load();
    } catch (e: any) {
      alert(e.message);
    }
  };

  const remove = async (u: CmsUser) => {
    if (!window.confirm(`Permanently delete ${u.name || u.username}? This cannot be undone.`)) return;
    try {
      await api.cmsDeleteUser(u.id);
      load();
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">User Management</h3>
          <p className="text-xs text-slate-400">
            Create, edit, suspend or delete users. New users default to{' '}
            <span className="text-emerald-400">PUBLIC_USER</span>.
          </p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search users…"
              className="cms-input pl-9 w-64"
            />
          </div>
          <button
            onClick={() => setCreating(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-xs font-medium"
          >
            <UserPlus className="w-3.5 h-3.5" /> Add User
          </button>
        </div>
      </div>

      <div className="border border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-900/70 text-slate-400 text-xs">
            <tr>
              <th className="text-left px-4 py-3 font-medium">Name</th>
              <th className="text-left px-4 py-3 font-medium">Username</th>
              <th className="text-left px-4 py-3 font-medium">Email</th>
              <th className="text-left px-4 py-3 font-medium">Role</th>
              <th className="text-left px-4 py-3 font-medium">Status</th>
              <th className="text-right px-4 py-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-500">
                  Loading…
                </td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-500">
                  No users match.
                </td>
              </tr>
            ) : (
              filtered.map((u) => (
                <tr key={u.id} className="border-t border-slate-800 hover:bg-slate-900/40">
                  <td className="px-4 py-3 text-slate-200">{u.name || '—'}</td>
                  <td className="px-4 py-3 text-slate-400 font-mono text-xs">{u.username}</td>
                  <td className="px-4 py-3 text-slate-400 text-xs">{u.email || '—'}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-emerald-300 border border-slate-700">
                      {u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {u.active ? (
                      <span className="inline-flex items-center gap-1 text-emerald-400 text-xs">
                        <Check className="w-3 h-3" /> Active
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-rose-400 text-xs">
                        <Ban className="w-3 h-3" /> Suspended
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-1">
                      <IconBtn title="Edit" onClick={() => setEditing(u)}>
                        <Edit2 className="w-3.5 h-3.5" />
                      </IconBtn>
                      <IconBtn title="Reset password" onClick={() => setResetFor(u)}>
                        <KeyRound className="w-3.5 h-3.5" />
                      </IconBtn>
                      <IconBtn
                        title={u.active ? 'Suspend' : 'Reactivate'}
                        onClick={() => toggleSuspend(u)}
                      >
                        {u.active ? <Ban className="w-3.5 h-3.5" /> : <Check className="w-3.5 h-3.5" />}
                      </IconBtn>
                      <IconBtn title="Delete" danger onClick={() => remove(u)}>
                        <Trash2 className="w-3.5 h-3.5" />
                      </IconBtn>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {creating && (
        <UserModal
          onClose={() => setCreating(false)}
          onSaved={() => {
            setCreating(false);
            load();
          }}
        />
      )}
      {editing && (
        <UserModal
          user={editing}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
            load();
          }}
        />
      )}
      {resetFor && <ResetPasswordModal user={resetFor} onClose={() => setResetFor(null)} />}
    </div>
  );
};

const IconBtn: React.FC<{
  title: string;
  danger?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}> = ({ title, danger, onClick, children }) => (
  <button
    title={title}
    onClick={onClick}
    className={`p-1.5 rounded hover:bg-slate-800 ${
      danger ? 'text-rose-400 hover:bg-rose-950/50' : 'text-slate-400 hover:text-slate-200'
    }`}
  >
    {children}
  </button>
);

const UserModal: React.FC<{
  user?: CmsUser;
  onClose: () => void;
  onSaved: () => void;
}> = ({ user, onClose, onSaved }) => {
  const [form, setForm] = useState({
    name: user?.name || '',
    username: user?.username || '',
    email: user?.email || '',
    phone: user?.phone || '',
    role: user?.role || 'PUBLIC_USER',
    password: '',
  });
  const [saving, setSaving] = useState(false);

  const save = async () => {
    setSaving(true);
    try {
      if (user) {
        const payload: any = { ...form };
        if (!payload.password) delete payload.password;
        await api.cmsUpdateUser(user.id, payload);
      } else {
        await api.cmsCreateUser(form);
      }
      onSaved();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal title={user ? 'Edit User' : 'Add User'} onClose={onClose}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <F label="Full name">
          <input
            className="cms-input"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </F>
        <F label="Username">
          <input
            className="cms-input"
            value={form.username}
            disabled={!!user}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
          />
        </F>
        <F label="Email">
          <input
            type="email"
            className="cms-input"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </F>
        <F label="Phone">
          <input
            className="cms-input"
            value={form.phone}
            onChange={(e) => setForm({ ...form, phone: e.target.value })}
          />
        </F>
        <F label="Role">
          <select
            className="cms-input"
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
          >
            {ROLE_OPTIONS.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </F>
        <F label={user ? 'New password (leave blank to keep)' : 'Password'}>
          <input
            type="password"
            className="cms-input"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </F>
      </div>
      <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-slate-800">
        <button
          onClick={onClose}
          className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300 text-sm hover:bg-slate-800"
        >
          Cancel
        </button>
        <button
          onClick={save}
          disabled={saving}
          className="px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-sm disabled:opacity-50"
        >
          {saving ? 'Saving…' : 'Save'}
        </button>
      </div>
    </Modal>
  );
};

const ResetPasswordModal: React.FC<{ user: CmsUser; onClose: () => void }> = ({
  user,
  onClose,
}) => {
  const [pw, setPw] = useState('');
  const [saving, setSaving] = useState(false);
  const submit = async () => {
    setSaving(true);
    try {
      await api.cmsResetPassword(user.id, pw);
      alert('Password updated');
      onClose();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setSaving(false);
    }
  };
  return (
    <Modal title={`Reset password — ${user.name || user.username}`} onClose={onClose}>
      <F label="New password (min 6 characters)">
        <input
          type="password"
          className="cms-input"
          value={pw}
          onChange={(e) => setPw(e.target.value)}
        />
      </F>
      <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-slate-800">
        <button
          onClick={onClose}
          className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300 text-sm hover:bg-slate-800"
        >
          Cancel
        </button>
        <button
          onClick={submit}
          disabled={saving || pw.length < 6}
          className="px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-sm disabled:opacity-50"
        >
          {saving ? 'Saving…' : 'Set Password'}
        </button>
      </div>
    </Modal>
  );
};

const Modal: React.FC<{
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}> = ({ title, onClose, children }) => (
  <div
    className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
    onClick={onClose}
  >
    <div
      className="bg-slate-950 border border-slate-800 rounded-xl max-w-2xl w-full p-6"
      onClick={(e) => e.stopPropagation()}
    >
      <h3 className="text-white font-semibold mb-5">{title}</h3>
      {children}
    </div>
  </div>
);

const F: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <label className="block">
    <span className="block text-xs font-medium text-slate-400 mb-1.5">{label}</span>
    {children}
  </label>
);