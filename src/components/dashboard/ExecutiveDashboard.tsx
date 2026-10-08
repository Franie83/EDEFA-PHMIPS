import React from 'react';
import { DashboardStats } from '../../types/index.ts';
import {
  FolderGit2,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldAlert,
  MapPin,
  ClipboardCheck,
  Compass,
  FileText,
  Activity,
  ArrowUpRight,
  TrendingUp,
  Map as MapIcon,
  ChevronRight,
  DollarSign
} from 'lucide-react';

interface ExecutiveDashboardProps {
  stats: DashboardStats | null;
  onNavigate: (module: string, filter?: any) => void;
  onQuickReport: () => void;
}

export const ExecutiveDashboard: React.FC<ExecutiveDashboardProps> = ({
  stats,
  onNavigate,
  onQuickReport
}) => {
  if (!stats) {
    return (
      <div className="p-8 text-center text-slate-500">
        <Activity className="w-8 h-8 animate-spin mx-auto mb-2 text-emerald-600" />
        <p>Loading executive database statistics...</p>
      </div>
    );
  }

  const kpis = stats?.kpis || {} as any;
  const charts = stats?.charts || {};

  // Defensive defaults — every field is guaranteed to exist below
  const hazardsByCategory = charts.hazardsByCategory || {};
  const hazardsBySeverity = charts.hazardsBySeverity || {};
  const hazardsByState = charts.hazardsByState || {};
  const hazardsByLga = charts.hazardsByLga || {};
  const monthlyReports = charts.monthlyReports || charts.monthlyActivity || [];
  const resolvedVsUnresolved = charts.resolvedVsUnresolved || { resolved: 0, unresolved: 0 };

  return (
    <div id="executive-dashboard-view" className="space-y-6 pb-12">
      {/* Top Banner & Quick Actions */}
      <div className="bg-gradient-to-r from-emerald-950 via-emerald-900 to-slate-900 rounded-xl p-5 text-white shadow-lg border border-emerald-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-amber-500 text-emerald-950 uppercase tracking-wider">
              Executive Decision Intelligence
            </span>
            <span className="text-xs text-emerald-300">Updated Real-Time</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black tracking-tight text-white mt-1">
            Edo State Ecological Fund Agency (EDEFA) Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-emerald-200/90 max-w-2xl mt-0.5">
            Real-time monitoring of ecological hazards, gully erosion, flood interventions, field inspections, and Edo State resource allocations.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            id="dash-report-btn"
            onClick={onQuickReport}
            className="px-3.5 py-2 rounded-lg text-xs font-bold bg-amber-500 hover:bg-amber-400 text-emerald-950 transition-colors shadow-sm inline-flex items-center"
          >
            <AlertTriangle className="w-4 h-4 mr-1.5" />
            Report Hazard
          </button>
          <button
            id="dash-gen-report-btn"
            onClick={() => onNavigate('reports')}
            className="px-3.5 py-2 rounded-lg text-xs font-semibold bg-emerald-800 hover:bg-emerald-700 text-white border border-emerald-600 transition-colors shadow-sm inline-flex items-center"
          >
            <FileText className="w-4 h-4 mr-1.5 text-amber-300" />
            Generate Report
          </button>
          <button
            id="dash-open-map-btn"
            onClick={() => onNavigate('map')}
            className="px-3.5 py-2 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors shadow-sm inline-flex items-center"
          >
            <MapIcon className="w-4 h-4 mr-1.5 text-emerald-400" />
            GIS Map
          </button>
        </div>
      </div>

      {/* 14 Executive Metric KPI Cards */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            System Key Performance Indicators (14 Critical Metrics)
          </h2>
          <span className="text-xs text-slate-400">Click any card to drill down</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-3">
          {/* Total Projects */}
          <div
            id="kpi-total-projects"
            onClick={() => onNavigate('projects')}
            className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs hover:border-emerald-500 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase">Total Projects</span>
              <FolderGit2 className="w-4 h-4 text-emerald-600 group-hover:translate-x-0.5 transition-transform" />
            </div>
            <div className="text-2xl font-black text-slate-900 mt-1">{kpis.totalProjects}</div>
            <div className="text-[10px] text-emerald-700 font-medium mt-0.5">
              ₦{((kpis.totalApprovedProjectFunding || 0) / 1e9).toFixed(1)}B Approved
            </div>
          </div>

          {/* Active Projects */}
          <div
            id="kpi-active-projects"
            onClick={() => onNavigate('projects')}
            className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs hover:border-emerald-500 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase">Active Projects</span>
              <Activity className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-2xl font-black text-emerald-700 mt-1">{kpis.activeProjects}</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Civil works underway</div>
          </div>

          {/* Completed Projects */}
          <div
            id="kpi-completed-projects"
            onClick={() => onNavigate('projects')}
            className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs hover:border-emerald-500 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase">Completed Projects</span>
              <CheckCircle2 className="w-4 h-4 text-teal-600" />
            </div>
            <div className="text-2xl font-black text-teal-800 mt-1">{kpis.completedProjects}</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Handed over & verified</div>
          </div>

          {/* Total Sites */}
          <div
            id="kpi-total-sites"
            onClick={() => onNavigate('sites')}
            className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs hover:border-emerald-500 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase">Total Sites</span>
              <MapPin className="w-4 h-4 text-indigo-600" />
            </div>
            <div className="text-2xl font-black text-slate-900 mt-1">{kpis.totalSites}</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Georeferenced locations</div>
          </div>

          {/* Site Visits */}
          <div
            id="kpi-site-visits"
            onClick={() => onNavigate('field_visits')}
            className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs hover:border-emerald-500 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase">Site Visits</span>
              <ClipboardCheck className="w-4 h-4 text-blue-600" />
            </div>
            <div className="text-2xl font-black text-blue-700 mt-1">{kpis.totalSiteVisits}</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Logged with GPS & photos</div>
          </div>

          {/* Total Hazard Reports */}
          <div
            id="kpi-total-hazards"
            onClick={() => onNavigate('hazards')}
            className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs hover:border-amber-500 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase">Total Hazard Reports</span>
              <AlertTriangle className="w-4 h-4 text-amber-600" />
            </div>
            <div className="text-2xl font-black text-slate-900 mt-1">{kpis.totalHazards}</div>
            <div className="text-[10px] text-slate-500 mt-0.5">In database register</div>
          </div>

          {/* Unverified Hazards */}
          <div
            id="kpi-unverified-hazards"
            onClick={() => onNavigate('hazards')}
            className="p-3.5 rounded-lg bg-amber-50/70 border border-amber-200 shadow-xs hover:border-amber-400 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-amber-800">
              <span className="text-[11px] font-semibold uppercase">Unverified Hazards</span>
              <Clock className="w-4 h-4 text-amber-700" />
            </div>
            <div className="text-2xl font-black text-amber-900 mt-1">{kpis.unverifiedHazards}</div>
            <div className="text-[10px] text-amber-700 mt-0.5">Awaiting technical check</div>
          </div>

          {/* Verified Hazards */}
          <div
            id="kpi-verified-hazards"
            onClick={() => onNavigate('hazards')}
            className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs hover:border-emerald-500 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase">Verified Hazards</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-2xl font-black text-emerald-800 mt-1">{kpis.verifiedHazards}</div>
            <div className="text-[10px] text-emerald-700 mt-0.5">Confirmed ecological risk</div>
          </div>

          {/* Critical Hazards */}
          <div
            id="kpi-critical-hazards"
            onClick={() => onNavigate('hazards')}
            className="p-3.5 rounded-lg bg-rose-50 border border-rose-200 shadow-xs hover:border-rose-400 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-rose-800">
              <span className="text-[11px] font-bold uppercase">Critical Hazards</span>
              <ShieldAlert className="w-4 h-4 text-rose-600 animate-pulse" />
            </div>
            <div className="text-2xl font-black text-rose-900 mt-1">{kpis.criticalHazards}</div>
            <div className="text-[10px] text-rose-700 font-semibold mt-0.5">Immediate attention</div>
          </div>

          {/* High Priority Hazards */}
          <div
            id="kpi-high-hazards"
            onClick={() => onNavigate('hazards')}
            className="p-3.5 rounded-lg bg-orange-50/70 border border-orange-200 shadow-xs hover:border-orange-400 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-orange-800">
              <span className="text-[11px] font-semibold uppercase">High Priority</span>
              <TrendingUp className="w-4 h-4 text-orange-600" />
            </div>
            <div className="text-2xl font-black text-orange-900 mt-1">{kpis.highHazards}</div>
            <div className="text-[10px] text-orange-700 mt-0.5">Urgent intervention</div>
          </div>

          {/* Awaiting Intervention */}
          <div
            id="kpi-awaiting-intervention"
            onClick={() => onNavigate('planning')}
            className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs hover:border-indigo-500 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase">Awaiting Intervention</span>
              <Compass className="w-4 h-4 text-indigo-600" />
            </div>
            <div className="text-2xl font-black text-indigo-900 mt-1">{kpis.awaitingIntervention}</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Assessed & prioritized</div>
          </div>

          {/* Active Interventions */}
          <div
            id="kpi-active-interventions"
            onClick={() => onNavigate('planning')}
            className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs hover:border-emerald-500 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase">Active Interventions</span>
              <Activity className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-2xl font-black text-emerald-800 mt-1">{kpis.activeInterventions}</div>
            <div className="text-[10px] text-emerald-700 mt-0.5">Funding & works ongoing</div>
          </div>

          {/* Completed Interventions */}
          <div
            id="kpi-completed-interventions"
            onClick={() => onNavigate('planning')}
            className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs hover:border-teal-500 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase">Completed</span>
              <CheckCircle2 className="w-4 h-4 text-teal-600" />
            </div>
            <div className="text-2xl font-black text-teal-800 mt-1">{kpis.completedInterventions}</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Remediated & protected</div>
          </div>

          {/* Outstanding Actions */}
          <div
            id="kpi-outstanding-actions"
            onClick={() => onNavigate('actions')}
            className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs hover:border-rose-500 cursor-pointer transition-all hover:shadow-md group"
          >
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase">Pending Actions</span>
              <Clock className="w-4 h-4 text-rose-500" />
            </div>
            <div className="text-2xl font-black text-slate-900 mt-1">{kpis.outstandingActions}</div>
            <div className="text-[10px] text-rose-600 font-semibold mt-0.5">
              {kpis.overdueActions} Overdue
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Hazards by Category */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Hazards by Ecological Category
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">Distribution</span>
          </div>
          <div className="space-y-2.5">
            {Object.entries(hazardsByCategory).map(([cat, count]) => {
              const numCount = Number(count);
              const pct = Math.round((numCount / (kpis.totalHazards || 1)) * 100);
              return (
                <div key={cat} className="text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-slate-800 truncate max-w-[200px]">{cat}</span>
                    <span className="text-slate-600 font-mono font-medium">{count} ({pct}%)</span>
                  </div>
                  <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-600 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
            {Object.keys(hazardsByCategory).length === 0 && (
              <div className="text-xs text-slate-400 text-center py-6">No hazard category data yet.</div>
            )}
          </div>
        </div>

        {/* Hazards by Severity & Status */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Risk Classification & Severity
              </h3>
              <span className="text-[11px] text-slate-400 font-mono">Priority</span>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="p-3 rounded-lg bg-rose-50 border border-rose-200">
                <div className="text-[10px] font-bold text-rose-700 uppercase">Critical (Immediate)</div>
                <div className="text-xl font-black text-rose-900 mt-1">{hazardsBySeverity.CRITICAL || 0}</div>
              </div>
              <div className="p-3 rounded-lg bg-orange-50 border border-orange-200">
                <div className="text-[10px] font-bold text-orange-700 uppercase">High (Priority)</div>
                <div className="text-xl font-black text-orange-900 mt-1">{hazardsBySeverity.HIGH || 0}</div>
              </div>
              <div className="p-3 rounded-lg bg-amber-50 border border-amber-200">
                <div className="text-[10px] font-bold text-amber-700 uppercase">Medium (Planned)</div>
                <div className="text-xl font-black text-amber-900 mt-1">{hazardsBySeverity.MEDIUM || 0}</div>
              </div>
              <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200">
                <div className="text-[10px] font-bold text-emerald-700 uppercase">Low (Monitoring)</div>
                <div className="text-xl font-black text-emerald-900 mt-1">{hazardsBySeverity.LOW || 0}</div>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100">
            <div className="flex items-center justify-between text-xs text-slate-600 mb-1">
              <span>Resolution Pipeline:</span>
              <span className="font-semibold text-slate-800">
                {resolvedVsUnresolved.resolved} Resolved / {resolvedVsUnresolved.unresolved} In Progress
              </span>
            </div>
            <div className="w-full bg-amber-200 h-2.5 rounded-full overflow-hidden flex">
              <div
                className="bg-emerald-600 h-full"
                style={{ width: `${(resolvedVsUnresolved.resolved / (kpis.totalHazards || 1)) * 100}%` }}
                title="Resolved"
              ></div>
              <div
                className="bg-amber-500 h-full"
                style={{ width: `${(resolvedVsUnresolved.unresolved / (kpis.totalHazards || 1)) * 100}%` }}
                title="Unresolved / Active"
              ></div>
            </div>
          </div>
        </div>

        {/* Geographic Hotspots by State & LGA */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Edo State Vulnerability Hotspots
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">18 LGAs</span>
          </div>
          <div className="space-y-3">
            <div>
              <div className="text-[11px] font-bold text-slate-500 uppercase mb-1.5">State & LGA Distribution</div>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(hazardsByState).map(([st, count]) => (
                  <span
                    key={st}
                    className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 border border-slate-200 text-slate-800"
                  >
                    <span className="font-semibold">{st}</span>
                    <span className="ml-1.5 px-1.5 py-0.2 rounded bg-emerald-800 text-white font-mono text-[10px]">
                      {count}
                    </span>
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100">
              <div className="text-[11px] font-bold text-slate-500 uppercase mb-1.5">High-Density LGAs</div>
              <div className="space-y-1 text-xs">
                {Object.entries(hazardsByLga).slice(0, 4).map(([lga, count]) => (
                  <div key={lga} className="flex items-center justify-between py-0.5 text-slate-700">
                    <span className="truncate">{lga}</span>
                    <span className="font-mono font-semibold text-slate-900">{count} reports</span>
                  </div>
                ))}
                {Object.keys(hazardsByLga).length === 0 && (
                  <div className="text-slate-400 text-center py-3">No LGA data yet.</div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Monthly Monitoring & Reporting Trend */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
        <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Monitoring Activity & Hazard Reporting Monthly Trajectory (2026)
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">Field inspections conducted vs hazards submitted</p>
          </div>
          <div className="flex items-center space-x-3 text-xs">
            <span className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-xs bg-amber-500"></span>
              <span className="text-slate-600 font-medium">Hazard Submissions</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-xs bg-emerald-600"></span>
              <span className="text-slate-600 font-medium">Field Inspections</span>
            </span>
          </div>
        </div>

        <div className="grid grid-cols-6 gap-3 pt-2">
          {monthlyReports.map((item: any) => (
            <div key={item.month} className="text-center">
              <div className="flex items-end justify-center space-x-2 h-28 mb-2">
                {/* Reports Bar */}
                <div
                  className="w-5 bg-amber-500 rounded-t-sm transition-all duration-300 relative group"
                  style={{ height: `${Math.min(100, Math.max(12, (item.reports || 0) * 7))}%` }}
                >
                  <span className="absolute -top-5 left-1/2 -translate-x-1/2 text-[10px] font-mono font-bold text-amber-700">
                    {item.reports || 0}
                  </span>
                </div>
                {/* Inspections Bar */}
                <div
                  className="w-5 bg-emerald-700 rounded-t-sm transition-all duration-300 relative group"
                  style={{ height: `${Math.min(100, Math.max(12, (item.visits || 0) * 7))}%` }}
                >
                  <span className="absolute -top-5 left-1/2 -translate-x-1/2 text-[10px] font-mono font-bold text-emerald-800">
                    {item.visits || 0}
                  </span>
                </div>
              </div>
              <span className="text-[11px] font-medium text-slate-600 block truncate">{item.month}</span>
            </div>
          ))}
          {monthlyReports.length === 0 && (
            <div className="col-span-6 text-xs text-slate-400 text-center py-6">No monthly activity recorded yet.</div>
          )}
        </div>
      </div>
    </div>
  );
};