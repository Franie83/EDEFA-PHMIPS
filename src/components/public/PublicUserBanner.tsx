import React from 'react';
import { LogOut, ShieldCheck, User } from 'lucide-react';

interface Props {
  currentUser?: any;
  onSignOut?: () => void;
}

export const PublicUserBanner: React.FC<Props> = ({ currentUser, onSignOut }) => {
  if (!currentUser) {
    return (
      <div className="w-full bg-slate-900 border-b border-slate-800 text-slate-300">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-2 flex items-center justify-between text-xs">
          <span className="flex items-center gap-2">
            <User className="w-3.5 h-3.5 text-slate-500" />
            Browsing as guest — reporting anonymously
          </span>
          <button
            onClick={() => {
              window.history.pushState({}, '', '/');
              window.dispatchEvent(new PopStateEvent('popstate'));
            }}
            className="text-emerald-400 hover:text-emerald-300 font-semibold"
          >
            Sign in
          </button>
        </div>
      </div>
    );
  }

  const initials = (currentUser.name || currentUser.username || 'PU')
    .split(' ')
    .map((s: string) => s[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <div className="w-full bg-emerald-950 border-b border-emerald-800 text-emerald-100">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-2 flex items-center justify-between text-xs">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-8 h-8 rounded-full bg-emerald-800 border border-emerald-700 flex items-center justify-center text-[10px] font-bold text-emerald-100">
            {initials}
          </div>
          <div className="min-w-0">
            <div className="font-semibold text-emerald-50 truncate">
              {currentUser.name || currentUser.username}
            </div>
            <div className="flex items-center gap-1.5 text-[10px] text-emerald-300">
              <ShieldCheck className="w-3 h-3" />
              <span className="uppercase tracking-wider font-mono">
                {currentUser.role || 'PUBLIC_USER'}
              </span>
            </div>
          </div>
        </div>
        {onSignOut && (
          <button
            onClick={onSignOut}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-900 hover:bg-emerald-800 border border-emerald-700 text-emerald-100 font-medium"
          >
            <LogOut className="w-3.5 h-3.5" />
            Sign out
          </button>
        )}
      </div>
    </div>
  );
};