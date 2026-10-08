import React, { useState } from 'react';
import { User, NotificationItem } from '../../types/index.ts';
import { DatabaseAdminControl } from '../auth/DatabaseAdminControl.tsx';
import {
  Bell,
  Shield,
  Globe,
  SlidersHorizontal,
  AlertTriangle
} from 'lucide-react';

interface HeaderProps {
  currentUser?: User | null;
  roles?: Array<{ id: string; name: string; description: string }>;
  onSwitchRole?: (roleId: string) => void;
  notifications?: NotificationItem[];
  onOpenNotifications?: () => void;
  activeModule?: string;
  onNavigate?: (module: string) => void;
  isPublicView?: boolean;
  onTogglePublicView?: () => void;
  onQuickReport?: () => void;
  currentRole?: string;
  onRoleChange?: (role: any) => void;
  unreadNotificationsCount?: number;
  onToggleNotifications?: () => void;
  onNewReportClick?: () => void;
  currentViewTitle?: string;
  onLogout?: () => void;
  onDatabaseCleared?: () => void;
  branding?: any;
}

// The 4 tier groups that mirror the login screen
const ROLE_TIERS: Array<{
  tier: string;
  label: string;
  roles: Array<{ id: string; name: string; description: string }>;
}> = [
  {
    tier: 'TIER_1_ADMIN',
    label: 'Super Admin',
    roles: [
      { id: 'SUPER_ADMIN', name: 'Super Administrator', description: 'Full system management and configuration' },
    ],
  },
  {
    tier: 'TIER_2_EXEC',
    label: 'Executive (Admin)',
    roles: [
      { id: 'EXECUTIVE', name: 'Management / Executive User', description: 'Executive dashboard, approvals, high-level planning' },
      { id: 'AUDITOR', name: 'Auditor', description: 'Read-only access to all registers and audit trails' },
    ],
  },
  {
    tier: 'TIER_3_DIRECTOR',
    label: 'Director',
    roles: [
      { id: 'COORDINATOR', name: 'Monitoring Coordinator', description: 'Project registration, inspection scheduling' },
      { id: 'INSPECTOR', name: 'Field Officer / Inspector', description: 'Field data collection, GPS, hazard reports' },
    ],
  },
  {
    tier: 'TIER_4_STAFF',
    label: 'Staff',
    roles: [
      { id: 'TECHNICAL_OFFICER', name: 'Verification / Technical Officer', description: 'Hazard verification, engineering assessments' },
      { id: 'PLANNING_OFFICER', name: 'Report / Planning Officer', description: 'Intervention planning, analytics, reports' },
    ],
  },
];

export const Header: React.FC<HeaderProps> = ({
  currentUser,
  onSwitchRole,
  notifications = [],
  onOpenNotifications,
  isPublicView = false,
  onTogglePublicView,
  onQuickReport,
  currentRole,
  onRoleChange,
  unreadNotificationsCount,
  onToggleNotifications,
  onNewReportClick,
  onLogout,
  onDatabaseCleared,
  branding
}) => {
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);
  const unreadCount =
    unreadNotificationsCount !== undefined
      ? unreadNotificationsCount
      : (notifications || []).filter(n => !n.read).length;

  const handleNotificationsClick = onOpenNotifications || onToggleNotifications || (() => {});
  const handleReportClick = onQuickReport || onNewReportClick || (() => {});

  const handleRoleSelect = (roleId: string) => {
    if (onSwitchRole) onSwitchRole(roleId);
    if (onRoleChange) onRoleChange(roleId);
    setRoleDropdownOpen(false);
  };

  // Find the tier label for the current role
  const currentTierLabel = (() => {
    const role = currentRole || currentUser?.role;
    if (!role) return '';
    for (const t of ROLE_TIERS) {
      if (t.roles.some(r => r.id === role)) return t.label;
    }
    return '';
  })();

  // Branding with safe fallbacks
  const appName = branding?.app_name || 'EDEFA-PHMIPS';
  const appTagline = branding?.app_tagline || 'Edo State Ecological Fund Agency - Project, Hazard & Intervention System';
  const logoUrl = branding?.logo_url || '';

  return (
    <header id="ef-app-header" className="bg-emerald-950 text-white border-b border-emerald-900 sticky top-0 z-40 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Identity */}
          <div className="flex items-center space-x-3">
            {logoUrl ? (
              <img
                src={logoUrl}
                alt={appName}
                className="w-11 h-11 rounded-lg bg-emerald-900 border border-emerald-700 shadow-inner object-contain p-0.5"
              />
            ) : (
              <div className="flex items-center justify-center w-11 h-11 rounded-lg bg-emerald-900 border border-emerald-700 shadow-inner">
                <div className="text-center font-black leading-tight text-emerald-400">
                  <span className="block text-[11px] uppercase tracking-wider font-mono">EDO</span>
                  <span className="block text-[10px] text-amber-400 font-serif font-bold">EFA</span>
                </div>
              </div>
            )}
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold tracking-tight text-base sm:text-lg text-emerald-50">
                  {appName}
                </span>
                <span className="hidden md:inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-800 text-emerald-200 border border-emerald-700">
                  Edo State Database v3.2
                </span>
              </div>
              <p className="hidden sm:block text-[11px] text-emerald-300 font-medium truncate max-w-md">
                {appTagline}
              </p>
            </div>
          </div>

          {/* Right Header Actions */}
          <div className="flex items-center space-x-3">
            {/* Quick Report Button */}
            <button
              id="header-quick-report-btn"
              onClick={handleReportClick}
              className="inline-flex items-center px-3 py-1.5 rounded-md text-xs font-semibold bg-amber-500 hover:bg-amber-400 text-emerald-950 transition-colors shadow-sm cursor-pointer"
              title="Report Potential Ecological Hazard"
            >
              <AlertTriangle className="w-4 h-4 mr-1 text-emerald-950" />
              <span className="hidden sm:inline">Report Hazard</span>
              <span className="sm:hidden">Report</span>
            </button>

            {/* Public Portal Switcher */}
            {onTogglePublicView && (
              <button
                id="header-public-portal-toggle"
                onClick={onTogglePublicView}
                className={`inline-flex items-center px-3 py-1.5 rounded-md text-xs font-medium border transition-colors cursor-pointer ${
                  isPublicView
                    ? 'bg-amber-400/20 text-amber-200 border-amber-400/50'
                    : 'bg-emerald-900/80 hover:bg-emerald-800 text-emerald-200 border-emerald-700'
                }`}
              >
                <Globe className="w-3.5 h-3.5 mr-1.5" />
                <span className="hidden md:inline">{isPublicView ? 'Return to Management' : 'Citizen Public Portal'}</span>
                <span className="md:hidden">Public</span>
              </button>
            )}

            {/* Notifications Bell */}
            <button
              id="header-notifications-bell"
              onClick={handleNotificationsClick}
              className="relative p-2 rounded-lg bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 transition-colors cursor-pointer"
              aria-label="View system notifications"
            >
              <Bell className="w-4 h-4" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white ring-2 ring-emerald-950">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Active User & Role Switcher */}
            <div className="relative">
              <button
                id="header-role-switcher-btn"
                onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
                className="flex items-center space-x-2 p-1.5 rounded-lg bg-emerald-900/70 hover:bg-emerald-800 border border-emerald-700/60 text-left transition-colors cursor-pointer"
              >
                <div className="w-7 h-7 rounded-full bg-emerald-700 flex items-center justify-center text-xs font-bold text-emerald-100 uppercase">
                  {currentUser?.name?.slice(0, 2) || (currentRole ? currentRole.slice(0, 2) : 'AD')}
                </div>
                <div className="hidden lg:block text-left pr-1">
                  <div className="text-xs font-semibold text-emerald-100 truncate max-w-[140px]">
                    {currentUser?.name || (currentRole === 'SUPER_ADMIN' ? 'Super Administrator' : 'Authorized Officer')}
                  </div>
                  <div className="text-[10px] text-amber-300 font-mono">
                    {currentRole || currentUser?.role || 'SUPER_ADMIN'}
                  </div>
                </div>
                <SlidersHorizontal className="w-3.5 h-3.5 text-emerald-400" />
              </button>

              {roleDropdownOpen && (
                <div
                  id="header-role-dropdown"
                  className="absolute right-0 mt-2 w-80 rounded-lg bg-emerald-900 border border-emerald-700 shadow-xl py-2 z-50"
                >
                  {/* Current user header */}
                  <div className="px-3 py-2 border-b border-emerald-800">
                    <p className="text-[11px] font-medium text-emerald-300 uppercase tracking-wider">
                      Switch Role (Role-Based Access)
                    </p>
                    <p className="text-xs text-emerald-100 font-semibold mt-0.5">
                      {currentUser?.role_title || (currentRole ? currentRole.replace(/_/g, ' ') : 'Administrator')}
                    </p>
                    <p className="text-[11px] text-emerald-400">{currentUser?.department || 'Operations Management'}</p>
                    {currentTierLabel && (
                      <p className="text-[10px] text-amber-300 mt-0.5 uppercase tracking-wider font-bold">
                        {currentTierLabel}
                      </p>
                    )}
                  </div>

                  {/* Super Admin tools */}
                  {currentRole === 'SUPER_ADMIN' && (
                    <div className="border-b border-emerald-800 py-2 px-2">
                      <div className="px-1 pb-1 text-[10px] uppercase tracking-wider text-rose-300 font-bold">Super Administrator</div>
                      <DatabaseAdminControl onCleared={onDatabaseCleared} />
                    </div>
                  )}

                  {/* Grouped roles by tier */}
                  <div className="py-1 max-h-96 overflow-y-auto">
                    {ROLE_TIERS.map((tier, idx) => (
                      <div key={tier.tier} className={idx > 0 ? 'mt-2' : ''}>
                        <div className="px-3 pt-2 pb-1 text-[10px] uppercase tracking-wider font-bold text-amber-400 flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                          {tier.label}
                        </div>
                        {tier.roles.map(r => {
                          const isActive = currentRole === r.id || currentUser?.role === r.id;
                          return (
                            <button
                              key={r.id}
                              onClick={() => handleRoleSelect(r.id)}
                              className={`w-full text-left px-3 py-2 text-xs flex items-start space-x-2 hover:bg-emerald-800/80 transition-colors cursor-pointer ${
                                isActive ? 'bg-emerald-800 text-amber-300 font-medium' : 'text-emerald-200'
                              }`}
                            >
                              <Shield className={`w-3.5 h-3.5 mt-0.5 shrink-0 ${isActive ? 'text-amber-400' : 'text-emerald-400'}`} />
                              <div className="min-w-0">
                                <div className="font-semibold truncate">{r.name}</div>
                                <div className="text-[10px] text-emerald-300 opacity-80 truncate">{r.description}</div>
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    ))}
                  </div>

                  {/* Sign out */}
                  {onLogout && (
                    <div className="border-t border-emerald-800 p-2">
                      <button
                        onClick={onLogout}
                        className="w-full rounded-lg bg-emerald-950 hover:bg-rose-950/70 text-xs text-rose-200 px-3 py-2 text-left"
                      >
                        Sign out
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};