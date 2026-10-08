import React from 'react';
import { NotificationItem } from '../../types/index.ts';
import { X, CheckCheck, AlertTriangle, Info, Bell, ArrowRight } from 'lucide-react';

interface NotificationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  notifications: NotificationItem[];
  onMarkRead: (id: string) => void;
  onNavigate: (module: string, recordId?: string) => void;
}

export const NotificationDrawer: React.FC<NotificationDrawerProps> = ({
  isOpen,
  onClose,
  notifications,
  onMarkRead,
  onNavigate
}) => {
  if (!isOpen) return null;

  return (
    <div id="notifications-modal-overlay" className="fixed inset-0 z-50 overflow-hidden bg-slate-900/60 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-md bg-white h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
        <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between bg-emerald-950 text-white">
          <div className="flex items-center space-x-2">
            <Bell className="w-5 h-5 text-amber-400" />
            <h3 className="font-bold text-base">System Notifications</h3>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-800 text-emerald-100">
              {notifications.length}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-emerald-300 hover:text-white hover:bg-emerald-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {notifications.length === 0 ? (
            <div className="text-center py-12 text-slate-400">
              <CheckCheck className="w-10 h-10 mx-auto mb-2 text-slate-300" />
              <p className="text-sm">No new notifications</p>
            </div>
          ) : (
            notifications.map(n => (
              <div
                key={n.id}
                id={`notif-card-${n.id}`}
                className={`p-3.5 rounded-lg border text-sm transition-all ${
                  n.read
                    ? 'bg-slate-50 border-slate-200 text-slate-600'
                    : n.priority === 'CRITICAL'
                    ? 'bg-rose-50/80 border-rose-200 text-rose-950'
                    : 'bg-emerald-50/70 border-emerald-200 text-emerald-950'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2 font-semibold">
                    {n.priority === 'CRITICAL' ? (
                      <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                    ) : (
                      <Info className="w-4 h-4 text-emerald-600 shrink-0" />
                    )}
                    <span className="text-xs">{n.title}</span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {new Date(n.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <p className="mt-1 text-xs leading-relaxed text-slate-700">{n.message}</p>
                <div className="mt-2 pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px]">
                  {!n.read && (
                    <button
                      onClick={() => onMarkRead(n.id)}
                      className="text-emerald-700 hover:text-emerald-900 font-medium"
                    >
                      Mark as read
                    </button>
                  )}
                  {n.link && (
                    <button
                      onClick={() => {
                        onMarkRead(n.id);
                        onClose();
                        if (n.category === 'HAZARD') onNavigate('hazards');
                        else if (n.category === 'ACTION') onNavigate('actions');
                        else if (n.category === 'INTERVENTION') onNavigate('planning');
                        else onNavigate('dashboard');
                      }}
                      className="ml-auto inline-flex items-center text-emerald-700 hover:text-emerald-950 font-semibold"
                    >
                      <span>Open Record</span>
                      <ArrowRight className="w-3 h-3 ml-1" />
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
