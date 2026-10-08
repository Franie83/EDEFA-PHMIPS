import React, { useState, useEffect } from 'react';
import { ShieldCheck, LogIn, KeyRound, AlertTriangle, Search, UserPlus, X } from 'lucide-react';
import { api, LoginGroup } from '../../services/api';

interface LoginScreenProps {
  onLogin: (user: any) => void;
}

export const LoginScreen: React.FC<LoginScreenProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [groups, setGroups] = useState<LoginGroup[]>([]);
  const [loadingGroups, setLoadingGroups] = useState(true);
  const [showSignup, setShowSignup] = useState(false);

  useEffect(() => {
    api.getLoginGroups()
      .then(setGroups)
      .catch(err => console.warn('Failed to load login groups:', err))
      .finally(() => setLoadingGroups(false));
  }, []);

  const submit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    setBusy(true);
    setError('');
    try {
      const r = await api.login(username, password);
      onLogin(r.user);
    } catch (e: any) {
      setError(e.message || 'Login failed');
    } finally {
      setBusy(false);
    }
  };

  const quickLogin = async (role: string) => {
    setBusy(true);
    setError('');
    try {
      const r = await api.quickLogin(role);
      onLogin(r.user);
    } catch (e: any) {
      setError(e.message || 'Quick login failed');
    } finally {
      setBusy(false);
    }
  };

  const goToPublicReport = () => {
    window.history.pushState({}, '', '/public/report');
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const goToTrack = () => {
    window.history.pushState({}, '', '/public/track');
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-6">
        {/* LEFT: Password login */}
        <div className="rounded-2xl bg-emerald-950 border border-emerald-800 p-7 shadow-2xl">
          <div className="flex items-center gap-3 mb-7">
            <div className="w-12 h-12 rounded-xl bg-emerald-800 flex items-center justify-center">
              <ShieldCheck className="w-7 h-7 text-emerald-300" />
            </div>
            <div>
              <h1 className="font-black text-xl">EDEFA-PHMIPS</h1>
              <p className="text-xs text-emerald-300">Ecological Fund Project & Hazard Management</p>
            </div>
          </div>

          <h2 className="text-2xl font-bold">Sign in</h2>
          <p className="text-sm text-emerald-200 mt-1 mb-6">
            Use your authorized account to access the central database.
          </p>

          <form onSubmit={submit} className="space-y-4">
            <label className="block text-xs font-semibold text-emerald-200">
              Username
              <input
                value={username}
                onChange={e => setUsername(e.target.value)}
                className="mt-1 w-full rounded-lg bg-emerald-900 border border-emerald-700 px-3 py-2.5 outline-none"
                autoComplete="username"
              />
            </label>
            <label className="block text-xs font-semibold text-emerald-200">
              Password
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="mt-1 w-full rounded-lg bg-emerald-900 border border-emerald-700 px-3 py-2.5 outline-none"
                autoComplete="current-password"
              />
            </label>
            {error && (
              <div className="rounded-lg bg-rose-950 border border-rose-800 text-rose-200 text-xs p-3">{error}</div>
            )}
            <button
              disabled={busy || !username || !password}
              className="w-full rounded-lg bg-emerald-500 disabled:opacity-50 text-emerald-950 font-bold py-2.5 flex items-center justify-center gap-2"
            >
              <LogIn className="w-4 h-4" />
              {busy ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          {/* Sign-up CTA */}
          <div className="mt-4 text-center text-xs text-emerald-300">
            No account yet?{' '}
            <button
              onClick={() => setShowSignup(true)}
              className="font-semibold text-amber-300 hover:text-amber-200 underline underline-offset-2"
            >
              Create account
            </button>{' '}
            and start reporting hazards.
          </div>

          {/* Public portal links */}
          <div className="mt-6 pt-6 border-t border-emerald-800/60">
            <div className="text-[11px] font-bold tracking-wider text-emerald-300 uppercase mb-3">
              Public services — no login required
            </div>
            <div className="grid sm:grid-cols-2 gap-2">
              <button
                onClick={goToPublicReport}
                className="text-left rounded-lg border border-amber-700/60 bg-amber-950/40 hover:bg-amber-900/50 p-3 transition"
              >
                <div className="flex items-center gap-2 text-amber-200 font-semibold text-sm">
                  <AlertTriangle className="w-4 h-4" /> Report a Hazard
                </div>
                <div className="text-[10px] text-amber-300/70 mt-1">Submit anonymously, get a tracking code</div>
              </button>
              <button
                onClick={goToTrack}
                className="text-left rounded-lg border border-slate-700 bg-slate-800/60 hover:bg-slate-700/60 p-3 transition"
              >
                <div className="flex items-center gap-2 text-slate-200 font-semibold text-sm">
                  <Search className="w-4 h-4" /> Track a Report
                </div>
                <div className="text-[10px] text-slate-400 mt-1">Enter your tracking code to check status</div>
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT: Grouped quick access */}
        <div className="rounded-2xl bg-slate-900 border border-slate-700 p-7 shadow-2xl">
          <div className="flex items-center gap-2 mb-2">
            <KeyRound className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-bold">Quick access</h2>
          </div>
          <p className="text-xs text-slate-400 mb-5">
            Development/demo accounts grouped by permission tier.
          </p>

          {loadingGroups && <div className="text-xs text-slate-500">Loading accounts…</div>}

          <div className="space-y-4">
            {groups.map(group => (
              <div key={group.tier}>
                <div className="text-[10px] font-bold uppercase tracking-wider text-amber-400 mb-2 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                  {group.label}
                </div>
                <div className="grid sm:grid-cols-2 gap-2">
                  {group.members.map(m => (
                    <button
                      key={m.username}
                      onClick={() => quickLogin(m.role)}
                      disabled={busy}
                      className="text-left rounded-xl border border-slate-700 bg-slate-800 hover:border-emerald-600 p-3 disabled:opacity-50 transition"
                    >
                      <div className="font-semibold text-sm truncate">{m.name || m.role}</div>
                      <div className="text-[10px] text-slate-400 mt-1 font-mono truncate">{m.username}</div>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-5 rounded-lg bg-amber-950/40 border border-amber-900 p-3 text-[11px] text-amber-200">
            Quick-access accounts are preserved when the Super Administrator empties application data.
          </div>
        </div>
      </div>

      {showSignup && (
        <SignUpModal
          onClose={() => setShowSignup(false)}
          onSuccess={(newUsername) => {
            setShowSignup(false);
            setUsername(newUsername);
            setPassword('');
            setError('');
            alert(
              'Account created! You can now sign in with the password you chose.\n\n' +
              'Your account starts with the PUBLIC_USER role — an administrator can upgrade it later.'
            );
          }}
        />
      )}
    </div>
  );
};

// ==================================================================
// Sign-up modal
// ==================================================================
interface SignUpModalProps {
  onClose: () => void;
  onSuccess: (username: string) => void;
}

const SignUpModal: React.FC<SignUpModalProps> = ({ onClose, onSuccess }) => {
  const [form, setForm] = useState({
    name: '',
    username: '',
    email: '',
    phone: '',
    password: '',
    confirm: '',
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.confirm) {
      setError('Passwords do not match');
      return;
    }
    if (form.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    if (!form.username.trim() || !form.email.trim()) {
      setError('Username and email are required');
      return;
    }

    setBusy(true);
    try {
      await api.publicSignup({
        name: form.name.trim(),
        username: form.username.trim().toLowerCase(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        phone: form.phone.trim(),
      });
      onSuccess(form.username.trim().toLowerCase());
    } catch (e: any) {
      setError(e.message || 'Sign-up failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 overflow-y-auto"
      onClick={onClose}
    >
      <form
        onSubmit={submit}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-lg rounded-2xl bg-emerald-950 border border-emerald-800 p-7 shadow-2xl my-8"
      >
        <div className="flex items-start justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-emerald-800 flex items-center justify-center">
              <UserPlus className="w-6 h-6 text-emerald-300" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Create account</h2>
              <p className="text-xs text-emerald-300">
                Register as a public user to report hazards
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg text-emerald-300 hover:bg-emerald-900"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-3">
          <Field label="Full name (optional)">
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full rounded-lg bg-emerald-900 border border-emerald-700 px-3 py-2.5 outline-none text-white"
              autoComplete="name"
            />
          </Field>

          <Field label="Username *">
            <input
              required
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              className="w-full rounded-lg bg-emerald-900 border border-emerald-700 px-3 py-2.5 outline-none text-white"
              autoComplete="username"
            />
          </Field>

          <Field label="Email *">
            <input
              required
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full rounded-lg bg-emerald-900 border border-emerald-700 px-3 py-2.5 outline-none text-white"
              autoComplete="email"
            />
          </Field>

          <Field label="Phone (optional)">
            <input
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              className="w-full rounded-lg bg-emerald-900 border border-emerald-700 px-3 py-2.5 outline-none text-white"
              autoComplete="tel"
            />
          </Field>

          <div className="grid sm:grid-cols-2 gap-3">
            <Field label="Password * (min 6 chars)">
              <input
                required
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="w-full rounded-lg bg-emerald-900 border border-emerald-700 px-3 py-2.5 outline-none text-white"
                autoComplete="new-password"
              />
            </Field>
            <Field label="Confirm password *">
              <input
                required
                type="password"
                value={form.confirm}
                onChange={(e) => setForm({ ...form, confirm: e.target.value })}
                className="w-full rounded-lg bg-emerald-900 border border-emerald-700 px-3 py-2.5 outline-none text-white"
                autoComplete="new-password"
              />
            </Field>
          </div>
        </div>

        {error && (
          <div className="mt-4 rounded-lg bg-rose-950 border border-rose-800 text-rose-200 text-xs p-3">
            {error}
          </div>
        )}

        <div className="mt-5 rounded-lg bg-amber-950/40 border border-amber-900 p-3 text-[11px] text-amber-200">
          New accounts start with the <span className="font-semibold">PUBLIC_USER</span> role. You
          can report hazards and track reports. An administrator can upgrade your access at any
          time.
        </div>

        <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-emerald-800">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-emerald-700 text-emerald-200 text-sm hover:bg-emerald-900"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={busy}
            className="px-5 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-emerald-950 font-bold text-sm disabled:opacity-50"
          >
            {busy ? 'Creating…' : 'Create account'}
          </button>
        </div>
      </form>
    </div>
  );
};

const Field: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <label className="block text-xs font-semibold text-emerald-200">
    {label}
    <div className="mt-1">{children}</div>
  </label>
);