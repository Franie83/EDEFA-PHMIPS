"""
patch_project_modal_map_links_v2.py
1. Sites cards clickable → map
2. Inspections cards clickable → map
3. Monitoring tab gets sub-tabs: Milestones | Before/After
   Before/After reuses <BeforeAfterMonitoring> scoped to this project.
"""
import pathlib

p = pathlib.Path("src/components/projects/ProjectDetailModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# --- Guard -----------------------------------------------------------------
if "BeforeAfterMonitoring" in src:
    print("Already patched — nothing to do.")
    print(f"Brace balance: {'OK' if src.count('{') == src.count('}') else 'MISMATCH'}")
    raise SystemExit(0)

# --- 1. Import BeforeAfterMonitoring ---------------------------------------
api_import = "import { api } from '../../services/api.ts';\n"
if api_import not in src:
    print("api import NOT FOUND")
    raise SystemExit(1)
src = src.replace(
    api_import,
    "import { BeforeAfterMonitoring } from '../monitoring/BeforeAfterMonitoring.tsx';\n" + api_import,
    1,
)
changes.append("imported BeforeAfterMonitoring")

# --- 2. Add monitoringSubTab state -----------------------------------------
state_anchor = "  const [activeTab, setActiveTab] = useState<'overview' | 'sites' | 'inspections' | 'monitoring'>('overview');\n"
if state_anchor not in src:
    print("activeTab anchor NOT FOUND")
    raise SystemExit(1)
src = src.replace(
    state_anchor,
    state_anchor + "  const [monitoringSubTab, setMonitoringSubTab] = useState<'milestones' | 'before_after'>('milestones');\n",
    1,
)
changes.append("added monitoringSubTab state")

# --- 3. Sites tab: make each card clickable --------------------------------
site_card_old = """                      <div key={s.id} className="p-3 rounded-lg border border-slate-200 bg-slate-50 space-y-2">
"""
site_card_new = """                      <div
                        key={s.id}
                        onClick={() => {
                          if (s.latitude != null && s.longitude != null) {
                            onClose();
                            onNavigateToMap(Number(s.latitude), Number(s.longitude));
                          }
                        }}
                        className="p-3 rounded-lg border border-slate-200 bg-slate-50 space-y-2 cursor-pointer hover:border-emerald-500 hover:shadow-md transition-all"
                        title={s.latitude != null ? 'Click to view on map' : ''}
                      >
"""
if site_card_old not in src:
    print("Site card anchor NOT FOUND")
    raise SystemExit(1)
src = src.replace(site_card_old, site_card_new, 1)
changes.append("made site cards clickable")

# --- 4. Inspections tab: make each visit card clickable --------------------
visit_card_old = """                  <div key={v.id} className="p-3 rounded-lg border border-slate-200 bg-slate-50 space-y-1">
"""
visit_card_new = """                  <div
                    key={v.id}
                    onClick={() => {
                      const lat = (v as any).gps_latitude ?? (v as any).latitude;
                      const lng = (v as any).gps_longitude ?? (v as any).longitude;
                      if (lat != null && lng != null) {
                        onClose();
                        onNavigateToMap(Number(lat), Number(lng));
                      }
                    }}
                    className="p-3 rounded-lg border border-slate-200 bg-slate-50 space-y-1 cursor-pointer hover:border-emerald-500 hover:shadow-md transition-all"
                    title={(v as any).gps_latitude != null ? 'Click to view location on map' : ''}
                  >
"""
if visit_card_old not in src:
    print("Visit card anchor NOT FOUND")
    raise SystemExit(1)
src = src.replace(visit_card_old, visit_card_new, 1)
changes.append("made inspection cards clickable")

# --- 5. Monitoring tab: add sub-tab toggle after summary grid --------------
# The summary grid ends with the Delayed tile's closing </div>, then </div>
# (grid close). We anchor on the exact Delayed tile tail.
summary_tail_old = """                <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-center">
                  <div className="text-[10px] uppercase text-rose-700 font-bold">Delayed</div>
                  <div className="text-lg font-black text-rose-900">{milestoneStats.by.Delayed}</div>
                </div>
              </div>
"""
if summary_tail_old not in src:
    print("Summary grid tail NOT FOUND")
    raise SystemExit(1)

summary_tail_new = summary_tail_old + """
              {/* Monitoring sub-tab toggle */}
              <div className="flex gap-1 border-b border-slate-200 mt-3">
                <button
                  type="button"
                  onClick={() => setMonitoringSubTab('milestones')}
                  className={`px-3 py-1.5 text-xs font-semibold border-b-2 transition-colors ${
                    monitoringSubTab === 'milestones'
                      ? 'border-emerald-600 text-emerald-800'
                      : 'border-transparent text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Milestones ({milestoneStats.total})
                </button>
                <button
                  type="button"
                  onClick={() => setMonitoringSubTab('before_after')}
                  className={`px-3 py-1.5 text-xs font-semibold border-b-2 transition-colors ${
                    monitoringSubTab === 'before_after'
                      ? 'border-emerald-600 text-emerald-800'
                      : 'border-transparent text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Before / After
                </button>
              </div>
"""
src = src.replace(summary_tail_old, summary_tail_new, 1)
changes.append("added monitoring sub-tab toggle")

# --- 6. Wrap milestones block in {monitoringSubTab === 'milestones' && (...)}
milestones_open_old = """          {/* Milestones Schedule */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
                Project Contract Milestones ({allMilestones.length})
"""
if milestones_open_old not in src:
    print("Milestones open anchor NOT FOUND")
    raise SystemExit(1)
milestones_open_new = """          {monitoringSubTab === 'milestones' && (
          <>
          {/* Milestones Schedule */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
                Project Contract Milestones ({allMilestones.length})
"""
src = src.replace(milestones_open_old, milestones_open_new, 1)
changes.append("opened milestones sub-tab conditional")

# --- 7. Close milestones sub-tab + insert Before/After panel ---------------
# Anchor: the monitoring tab's closing `</>` followed by `)}` before the
# inspections tab. From grep, that's around line 511-513.
monitoring_close_old = """            </>
          )}

          {activeTab === 'inspections' && (
"""
if monitoring_close_old not in src:
    print("Monitoring close anchor NOT FOUND")
    raise SystemExit(1)

monitoring_close_new = """            </>
          )}

          {monitoringSubTab === 'before_after' && (
            <div className="rounded-lg border border-slate-200 overflow-hidden mt-3">
              <BeforeAfterMonitoring
                projects={[project]}
                evidenceList={(project as any).evidence_files || []}
              />
            </div>
          )}

            </>
          )}

          {activeTab === 'inspections' && (
"""
src = src.replace(monitoring_close_old, monitoring_close_new, 1)
changes.append("inserted Before/After panel + closed milestones sub-tab")

# --- 8. Close the milestones sub-tab fragment itself -----------------------
# The milestones sub-tab opened with `{monitoringSubTab === 'milestones' && (\n          <>`
# Its content ends where the original monitoring `</>` closes. We need to close
# the milestones fragment (</>) and the conditional ())} right before the new
# Before/After block.
# Anchor: '          )}\n\n          {monitoringSubTab === \'before_after\''
milestones_close_old = """          )}

          {monitoringSubTab === 'before_after' && (
"""
if milestones_close_old not in src:
    print("Milestones close anchor NOT FOUND")
    raise SystemExit(1)
milestones_close_new = """          </>
          )}

          {monitoringSubTab === 'before_after' && (
"""
src = src.replace(milestones_close_old, milestones_close_new, 1)
changes.append("closed milestones sub-tab fragment")

p.write_text(src, encoding="utf-8")

print("Changes:")
for c in changes:
    print(" -", c)

opens = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")