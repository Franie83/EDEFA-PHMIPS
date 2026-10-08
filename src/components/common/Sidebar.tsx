import React from 'react';
import {
  LayoutDashboard, AlertTriangle, FolderGit2, MapPin, CheckSquare, Compass, CheckCircle, FileSpreadsheet,
  LineChart, History, ChevronRight, Settings
} from 'lucide-react';
import { canAccess } from '../../types/tiers';

interface SidebarProps {
  activeModule?: string;
  onSelectModule?: (moduleId: string) => void;
  currentView?: string;
  onViewChange?: (view: string) => void;
  collapsed?: boolean;
  pendingVerificationsCount?: number;
  activeProjectsCount?: number;
  hazardsCount?: number;
  isMobileOpen?: boolean;
  setIsMobileOpen?: (open: boolean) => void;
  currentRole?: string;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  category: string;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard', label: 'Executive Dashboard',          icon: LayoutDashboard, category: 'OVERVIEW' },
  { id: 'hazards',   label: 'Hazard Reports',               icon: AlertTriangle,   category: 'OVERVIEW' },
  { id: 'projects',  label: 'Projects Register',            icon: FolderGit2,      category: 'OVERVIEW' },
  { id: 'actions',   label: 'Actions & Follow-up',          icon: CheckCircle,     category: 'OVERVIEW' },

  { id: 'reports',   label: 'Comprehensive Reports',        icon: FileSpreadsheet, category: 'INTELLIGENCE' },
  { id: 'analytics', label: 'Analytics & Decision Support', icon: LineChart,       category: 'INTELLIGENCE' },

  { id: 'audit',     label: 'Audit Logs & Compliance',      icon: History,         category: 'GOVERNANCE' },
  { id: 'cms',       label: 'Content Management',           icon: Settings,        category: 'GOVERNANCE' }
];

export const Sidebar: React.FC<SidebarProps> = ({
  activeModule,
  onSelectModule,
  currentView,
  onViewChange,
  pendingVerificationsCount = 0,
  activeProjectsCount = 0,
  hazardsCount = 0,
  isMobileOpen = false,
  setIsMobileOpen,
  currentRole
}) => {
  const current = currentView || activeModule || 'dashboard';

  // Filter items by current role. 'cms' is Super Admin only.
  const visibleItems = NAV_ITEMS.filter(item => {
    if (item.id === 'cms') return currentRole === 'SUPER_ADMIN';
    return canAccess(item.id, currentRole);
  });

  const handleSelect = (id: string) => {
    let target = id;
    if (id === 'field_visits') target = 'visits';
    if (id === 'planning') target = 'interventions';
    if (id === 'audit_trail') target = 'audit';

    if (onViewChange) onViewChange(target);
    if (onSelectModule) onSelectModule(target);
    if (setIsMobileOpen) setIsMobileOpen(false);
  };

  const categories = Array.from(new Set(visibleItems.map(i => i.category)));

  return (
    <aside
      id="ef-app-sidebar"
      className={`w-64 bg-slate-900 text-slate-200 border-r border-slate-800 flex flex-col shrink-0 min-h-[calc(100vh-4rem)] select-none transition-all ${
        isMobileOpen ? 'block fixed inset-y-0 left-0 z-50 shadow-2xl' : 'hidden md:flex'
      }`}
    >
      <div className="p-3 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
        <div>
          <div className="text-[11px] font-bold tracking-wider text-emerald-400 uppercase font-mono">
            System Modules
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Ecological Lifecycle Platform
          </div>
        </div>
        {setIsMobileOpen && isMobileOpen && (
          <button
            onClick={() => setIsMobileOpen(false)}
            className="md:hidden text-slate-400 hover:text-white p-1"
          >
            ✕
          </button>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-4">
        {categories.map(cat => {
          const items = visibleItems.filter(i => i.category === cat);
          return (
            <div key={cat} className="space-y-1">
              <div className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-400/80">
                {cat}
              </div>
              {items.map(item => {
                const Icon = item.icon;
                const isActive = current === item.id;

                let badgeCount = 0;
                if (item.id === 'hazards')  badgeCount = hazardsCount;
                if (item.id === 'projects') badgeCount = activeProjectsCount;

                return (
                  <button
                    key={item.id}
                    id={`sidebar-nav-${item.id}`}
                    onClick={() => handleSelect(item.id)}
                    className={`w-full flex items-center justify-between px-2.5 py-2 rounded-md text-xs font-medium transition-colors cursor-pointer ${
                      isActive
                        ? 'bg-emerald-700 text-white font-semibold shadow-sm'
                        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                    }`}
                  >
                    <div className="flex items-center space-x-2.5 truncate">
                      <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-amber-300' : 'text-slate-400'}`} />
                      <span className="truncate">{item.label}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      {badgeCount > 0 && (
                        <span className="px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                          {badgeCount}
                        </span>
                      )}
                      {isActive && <ChevronRight className="w-3.5 h-3.5 text-emerald-300 shrink-0 ml-1" />}
                    </div>
                  </button>
                );
              })}
            </div>
          );
        })}
      </nav>

      <div className="p-3 border-t border-slate-800 bg-slate-950/40 text-[11px] text-slate-400">
        <div className="flex items-center justify-between">
          <span className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-slate-300 font-medium">Database Online</span>
          </span>
          <span className="font-mono text-[10px] text-slate-400">EPO-SEC-2026</span>
        </div>
      </div>
    </aside>
  );
};