"""
patch_project_detail_tabs.py  (v2 — anchored on JSX comments)
Adds Overview / Sites / Inspections / Monitoring tabs to ProjectDetailModal.tsx
"""
import pathlib

p = pathlib.Path("src/components/projects/ProjectDetailModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# --- 0. Guard -------------------------------------------------------------
if "'overview' | 'sites' | 'inspections' | 'monitoring'" in src:
    print("Already patched — nothing to do.")
    print(f"Brace balance: {'OK' if src.count('{') == src.count('}') else 'MISMATCH'}")
    raise SystemExit(0)

# --- 1. Add tab state -----------------------------------------------------
anchor = "  const [savingMilestones, setSavingMilestones] = useState(false);\n"
if anchor not in src:
    print("State anchor NOT FOUND")
    raise SystemExit(1)
src = src.replace(
    anchor,
    anchor
    + "  const [activeTab, setActiveTab] = useState<'overview' | 'sites' | 'inspections' | 'monitoring'>('overview');\n",
    1,
)
changes.append("added activeTab state")

# --- 2. Derived helpers, inserted before 'return (' -----------------------
derived = r"""
  // --- Derived helpers for the tabbed layout ---
  const projectSites: any[] = (() => {
    if (Array.isArray((project as any).sites) && (project as any).sites.length > 0) {
      return (project as any).sites;
    }
    const visits: any[] = Array.isArray((project as any).site_visits) ? (project as any).site_visits : [];
    const seen = new Map<string, any>();
    for (const v of visits) {
      const key = v.site_id || v.site_name || v.id;
      if (!key || seen.has(key)) continue;
      seen.set(key, {
        id: v.site_id || key,
        name: v.site_name || v.purpose || 'Unnamed site',
        community: v.community,
        lga: v.lga,
        state: v.state,
        latitude: v.latitude,
        longitude: v.longitude,
      });
    }
    return Array.from(seen.values());
  })();

  const visitsForSite = (siteId: string) =>
    (Array.isArray((project as any).site_visits) ? (project as any).site_visits : [])
      .filter((v: any) => v.site_id === siteId);

  const milestoneStats = (() => {
    const total = allMilestones.length;
    const by = { Pending: 0, 'In Progress': 0, Completed: 0, Delayed: 0 } as Record<string, number>;
    let pctSum = 0;
    for (const m of allMilestones) {
      by[m.status] = (by[m.status] || 0) + 1;
      pctSum += Number(m.progress_percentage) || 0;
    }
    return { total, by, avg: total ? Math.round(pctSum / total) : 0 };
  })();

"""
ret_anchor = "  return (\n    <div id=\"project-detail-modal\""
if ret_anchor not in src:
    print("return( anchor NOT FOUND")
    raise SystemExit(1)
src = src.replace(ret_anchor, derived + ret_anchor, 1)
changes.append("inserted derived helpers")

# --- 3. Body open: replace '{/* Modal Body */}' header div with tab bar + wrapper
body_anchor = """        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-slate-700">
"""
if body_anchor not in src:
    print("Modal Body anchor NOT FOUND")
    raise SystemExit(1)

new_body_open = """        {/* Tab Bar */}
        <div className="flex border-b border-slate-200 px-2 bg-slate-50 shrink-0">
          {([
            ['overview',    'Overview',    null],
            ['sites',       'Sites',       projectSites.length || null],
            ['inspections', 'Inspections', (project as any).site_visits?.length || null],
            ['monitoring',  'Monitoring',  milestoneStats.total || null],
          ] as const).map(([key, label, count]) => (
            <button
              key={key as string}
              type="button"
              onClick={() => setActiveTab(key as any)}
              className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
                activeTab === key
                  ? 'border-emerald-600 text-emerald-800 bg-white'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              {label}
              {count ? <span className="ml-1.5 text-[10px] text-slate-400">({count})</span> : null}
            </button>
          ))}
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-slate-700">
          {activeTab === 'overview' && (
            <>

"""
src = src.replace(body_anchor, new_body_open, 1)
changes.append("inserted tab bar + opened Overview fragment")

# --- 4. Close Overview + open Monitoring, right before '{/* Milestones Schedule */}'
milestones_anchor = """          {/* Milestones Schedule */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
                Project Contract Milestones ({allMilestones.length})
"""
if milestones_anchor not in src:
    print("Milestones anchor NOT FOUND")
    raise SystemExit(1)

monitoring_open = """            </>
          )}

          {activeTab === 'sites' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
                  Project Sites ({projectSites.length})
                </h4>
                {canLogVisit && (
                  <button
                    type="button"
                    onClick={() => { onClose(); onLogVisitClick(project); }}
                    className="px-2.5 py-1 rounded text-xs font-semibold bg-emerald-700 text-white hover:bg-emerald-800 inline-flex items-center"
                  >
                    <ClipboardList className="w-3.5 h-3.5 mr-1" />
                    Log Visit
                  </button>
                )}
              </div>
              {projectSites.length === 0 ? (
                <div className="p-4 text-center bg-slate-50 rounded-lg text-slate-400 text-xs">
                  No sites registered for this project yet.
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {projectSites.map((s: any) => {
                    const siteVisits = visitsForSite(s.id);
                    return (
                      <div key={s.id} className="p-3 rounded-lg border border-slate-200 bg-slate-50 space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="font-bold text-slate-900 text-sm">{s.name}</div>
                            <div className="text-[11px] text-slate-500">
                              {[s.community, s.lga, s.state].filter(Boolean).join(' · ')}
                            </div>
                          </div>
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                            {siteVisits.length} visit{siteVisits.length === 1 ? '' : 's'}
                          </span>
                        </div>
                        {s.latitude != null && s.longitude != null && (
                          <button
                            type="button"
                            onClick={() => { onClose(); onNavigateToMap(Number(s.latitude), Number(s.longitude)); }}
                            className="text-[10px] font-semibold text-emerald-700 hover:text-emerald-900 inline-flex items-center"
                          >
                            <MapPin className="w-3 h-3 mr-1" />
                            {Number(s.latitude).toFixed(5)}, {Number(s.longitude).toFixed(5)}
                          </button>
                        )}
                        {siteVisits.length > 0 && (
                          <div className="pt-2 border-t border-slate-200 space-y-1">
                            {siteVisits.slice(0, 3).map((v: any) => (
                              <div key={v.id} className="text-[10px] text-slate-600">
                                <span className="font-mono">{v.visit_date}</span> — {v.officer_name} ({v.progress_percentage}%)
                              </div>
                            ))}
                            {siteVisits.length > 3 && (
                              <div className="text-[10px] text-slate-400 italic">
                                +{siteVisits.length - 3} more — see Inspections tab
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {activeTab === 'monitoring' && (
            <>
              {/* Monitoring summary */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-center">
                  <div className="text-[10px] uppercase text-emerald-700 font-bold">Overall</div>
                  <div className="text-lg font-black text-emerald-900">{milestoneStats.avg}%</div>
                </div>
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-center">
                  <div className="text-[10px] uppercase text-slate-600 font-bold">Pending</div>
                  <div className="text-lg font-black text-slate-800">{milestoneStats.by.Pending}</div>
                </div>
                <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-center">
                  <div className="text-[10px] uppercase text-blue-700 font-bold">In Progress</div>
                  <div className="text-lg font-black text-blue-900">{milestoneStats.by['In Progress']}</div>
                </div>
                <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-center">
                  <div className="text-[10px] uppercase text-emerald-700 font-bold">Completed</div>
                  <div className="text-lg font-black text-emerald-900">{milestoneStats.by.Completed}</div>
                </div>
                <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-center">
                  <div className="text-[10px] uppercase text-rose-700 font-bold">Delayed</div>
                  <div className="text-lg font-black text-rose-900">{milestoneStats.by.Delayed}</div>
                </div>
              </div>

          {/* Milestones Schedule */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
                Project Contract Milestones ({allMilestones.length})
"""

src = src.replace(milestones_anchor, monitoring_open, 1)
changes.append("closed Overview + inserted Sites panel + opened Monitoring")

# --- 5. Close Monitoring + open Inspections, before '{/* Linked Field Visits */}'
visits_anchor = """          {/* Linked Field Visits */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
                Field Inspection Visits ({project.site_visits?.length || 0})
"""
if visits_anchor not in src:
    print("Field Visits anchor NOT FOUND")
    raise SystemExit(1)

inspections_open = """            </>
          )}

          {activeTab === 'inspections' && (
          <>
          {/* Linked Field Visits */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
                Field Inspection Visits ({project.site_visits?.length || 0})
"""
src = src.replace(visits_anchor, inspections_open, 1)
changes.append("closed Monitoring + opened Inspections")

# --- 6. Close Inspections fragment at end of body, before modal-body </div>
#     The body ends with: '            )}\n          </div>\n        </div>\n\n        {/* Footer */}'
body_close = """            )}
          </div>
        </div>

        {/* Footer */}
"""
if body_close not in src:
    print("Body close anchor NOT FOUND")
    raise SystemExit(1)

new_body_close = """            )}
          </div>
          </>
          )}
        </div>

        {/* Footer */}
"""
src = src.replace(body_close, new_body_close, 1)
changes.append("closed Inspections fragment + closed body")

p.write_text(src, encoding="utf-8")

print("Changes:")
for c in changes:
    print(" -", c)

opens = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")