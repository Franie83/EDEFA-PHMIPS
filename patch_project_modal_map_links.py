"""
patch_project_modal_map_links.py
1. Makes Sites cards fully clickable → onNavigateToMap(lat, lng)
2. Makes Inspections cards clickable → onNavigateToMap(gps_latitude, gps_longitude)
3. Replaces Monitoring tab body with <BeforeAfterMonitoring> scoped to this project
   (with the milestone list kept as a sub-tab)
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

# --- 1. Add import for BeforeAfterMonitoring -------------------------------
import_anchor = "import { api } from '../../services/api.ts';\n"
if import_anchor not in src:
    print("api import anchor NOT FOUND")
    raise SystemExit(1)
src = src.replace(
    import_anchor,
    "import { BeforeAfterMonitoring } from '../monitoring/BeforeAfterMonitoring.tsx';\n" + import_anchor,
    1,
)
changes.append("imported BeforeAfterMonitoring")

# --- 2. Add monitoring sub-tab state ---------------------------------------
state_anchor = "  const [activeTab, setActiveTab] = useState<'overview' | 'sites' | 'inspections' | 'monitoring'>('overview');\n"
if state_anchor not in src:
    print("activeTab state anchor NOT FOUND — run the tabs patch first")
    raise SystemExit(1)
src = src.replace(
    state_anchor,
    state_anchor
    + "  const [monitoringSubTab, setMonitoringSubTab] = useState<'milestones' | 'before_after'>('milestones');\n",
    1,
)
changes.append("added monitoringSubTab state")

# --- 3. Sites tab: make each site card clickable ---------------------------
site_card_anchor = """                      <div key={s.id} className="p-3 rounded-lg border border-slate-200 bg-slate-50 space-y-2">
"""
if site_card_anchor not in src:
    print("Site card anchor NOT FOUND")
    raise SystemExit(1)

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
src = src.replace(site_card_anchor, site_card_new, 1)
changes.append("made site cards clickable")

# --- 4. Inspections tab: make each visit card clickable --------------------
visit_card_anchor = """                  <div key={v.id} className="p-3 rounded-lg border border-slate-200 bg-slate-50 space-y-1">
"""
if visit_card_anchor not in src:
    print("Visit card anchor NOT FOUND")
    raise SystemExit(1)

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
                    title="Click to view location on map"
                  >
"""
src = src.replace(visit_card_anchor, visit_card_new, 1)
changes.append("made inspection cards clickable")

# --- 5. Monitoring tab: replace body with sub-tab + BeforeAfterMonitoring --
# Find the monitoring body between the summary tiles and the closing of monitoring conditional.
# After the tabs patch, the structure is:
#   {activeTab === 'monitoring' && (
#     <>
#       {/* Monitoring summary */}
#       <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
#         ... 5 tiles ...
#       </div>
#       {/* Milestones Schedule */}
#       <div>
#         ...
#       </div>
#     </>
#   )}
# We'll insert a sub-tab toggle just after the summary grid, and wrap
# the milestones block and a new BeforeAfter panel in conditionals.

# 5a. Insert the sub-tab toggle right after the summary grid's closing </div>
summary_close_anchor = """                  <div className="text-lg font-black text-rose-900">{milestoneStats.by.Delayed}</div>
                </div>
              </div>
"""
if summary_close_anchor not in src:
    print("Monitoring summary closing anchor NOT FOUND")
    raise SystemExit(1)

summary_close_new = summary_close_anchor + """
              {/* Monitoring sub-tab toggle */}
              <div className="flex gap-1 border-b border-slate-200">
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
src = src.replace(summary_close_anchor, summary_close_new, 1)
changes.append("added monitoring sub-tab toggle")

# 5b. Wrap the milestones schedule block in {monitoringSubTab === 'milestones' && (...)}
# After the tabs patch, the milestones schedule starts with:
#     <div>
#       <div className="flex items-center justify-between mb-2">
#         <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
#           Project Contract Milestones ({allMilestones.length})
milestones_block_anchor = """          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
                Project Contract Milestones ({allMilestones.length})
"""
if milestones_block_anchor not in src:
    print("Milestones block anchor NOT FOUND")
    raise SystemExit(1)

milestones_wrapped = """          {monitoringSubTab === 'milestones' && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
                Project Contract Milestones ({allMilestones.length})
"""
src = src.replace(milestones_block_anchor, milestones_wrapped, 1)
changes.append("wrapped milestones block in sub-tab conditional")

# 5c. Close milestones block and add Before/After panel.
# The milestones block ends right before '{/* Linked Field Visits */}' — but with our
# tabs patch, monitoring closes with '            </>\n          )}\n\n          {activeTab === 'inspections' && ('
# So we anchor on the closing of the monitoring fragment.
monitoring_close_anchor = """            </>
          )}

          {activeTab === 'inspections' && (
"""
if monitoring_close_anchor not in src:
    print("Monitoring close anchor NOT FOUND — run tabs patch first")
    raise SystemExit(1)

monitoring_close_new = """          </>
          )}

          {monitoringSubTab === 'before_after' && (
            <div className="rounded-lg border border-slate-200 overflow-hidden">
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
# Only replace the FIRST occurrence (monitoring close).
src = src.replace(monitoring_close_anchor, monitoring_close_new, 1)
changes.append("inserted Before/After panel and closed milestones sub-tab")

# The milestones sub-tab conditional opened with {monitoringSubTab === 'milestones' && (
# We need to close that before the Before/After panel. Add a closing )} right after
# the milestones block's final </div>, which sits right before the new Before/After panel.
# Since we can't easily anchor that without seeing the exact close, use a structural anchor:
# the milestones block closes with:
#       ))}
            </div>
          </div>
# followed by (new) our Before/After panel.
# Safer: match on "          )}\n\n          {monitoringSubTab === 'before_after'" — no.
# Instead: after the tabs patch, the milestone close is:
#   "            </div>\n          </div>\n\n          {/* Linked Field Visits */}"
# — but tabs patch inserted the sub-tab toggle above, so structure differs.
# Defer to a follow-up if unresolved.
if "          )}\n\n          {monitoringSubTab === 'before_after'" in src:
    src = src.replace(
        "          )}\n\n          {monitoringSubTab === 'before_after'",
        "            </div>\n          </div>\n          )}\n\n          {monitoringSubTab === 'before_after'",
        1,
    )
    changes.append("closed milestones sub-tab conditional")
else:
    changes.append("WARNING: could not auto-close milestones sub-tab — may need manual fix")

p.write_text(src, encoding="utf-8")

print("Changes:")
for c in changes:
    print(" -", c)

opens = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")