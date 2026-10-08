import pathlib

p = pathlib.Path("src/components/public/PublicTrackPage.tsx")
src = p.read_text(encoding="utf-8")

old = """                  {/* Progress bar */}
                  <div className="pt-2">
                    <div className="flex items-center justify-between text-[11px] mb-1">
                      <span className="text-emerald-400">Physical progress</span>
                      <span className="font-mono text-emerald-100 font-bold">
                        {result.project.actual_percentage || 0}%
                      </span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden border border-emerald-900/40">
                      <div
                        className="h-full bg-emerald-500 transition-all"
                        style={{ width: `${Math.min(100, result.project.actual_percentage || 0)}%` }}
                      />
                    </div>
                    <div className="text-[10px] text-emerald-400/70 mt-1">
                      Planned: {result.project.planned_percentage || 0}%
                    </div>
                  </div>"""

new = """                  {/* Progress bar — only shown once the project is approved (Active / Delayed / Completed) */}
                  {['Active', 'Delayed', 'Completed'].includes(result.project.status) ? (
                    <div className="pt-2">
                      <div className="flex items-center justify-between text-[11px] mb-1">
                        <span className="text-emerald-400">Physical progress</span>
                        <span className="font-mono text-emerald-100 font-bold">
                          {result.project.actual_percentage || 0}%
                        </span>
                      </div>
                      <div className="h-2 bg-slate-800 rounded-full overflow-hidden border border-emerald-900/40">
                        <div
                          className="h-full bg-emerald-500 transition-all"
                          style={{ width: `${Math.min(100, result.project.actual_percentage || 0)}%` }}
                        />
                      </div>
                      <div className="text-[10px] text-emerald-400/70 mt-1">
                        Planned: {result.project.planned_percentage || 0}%
                      </div>
                    </div>
                  ) : (
                    <div className="pt-2 rounded bg-amber-950/30 border border-amber-900/40 px-3 py-2">
                      <div className="text-[10px] text-amber-300">
                        ⏳ Physical progress will be tracked once the project is approved and work begins.
                      </div>
                    </div>
                  )}"""

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Progress block gated by project status")
else:
    print("Progress block pattern NOT FOUND — paste the current block")