import pathlib
import re

p = pathlib.Path("src/components/interventions/InterventionPlanning.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# ---------- 1. Change the outer wrapper from space-y-3 to a responsive grid ----------
old_wrapper = '''      {/* Interventions Register Grid */}
      <div className="space-y-3">
        {filteredInterventions.length === 0 && ('''
new_wrapper = '''      {/* Interventions Register Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredInterventions.length === 0 && ('''
if old_wrapper in src:
    src = src.replace(old_wrapper, new_wrapper)
    changes.append("outer wrapper → responsive grid")
else:
    changes.append("outer wrapper pattern NOT FOUND")

# ---------- 2. Replace the entire card block with the compact square version ----------
# Locate the start and end of the map callback body and replace

pattern = re.compile(
    r"\{filteredInterventions\.map\(item => \{.*?\n        \}\)\}",
    re.DOTALL
)

new_card = '''{filteredInterventions.map(item => {
          const linkedHazard = hazards.find(h => h.id === item.hazard_id);
          const status = (item as any).approval_status;
          const isDirectorPending = status === 'Proposed' || status === 'Rejected' || !status;
          const isExecutivePending = status === 'Director Approved';
          const isFullyApproved = status === 'Executive Approved';

          return (
            <div
              key={item.id}
              id={`intervention-row-${item.id}`}
              onClick={() => setSelectedIntervention(item)}
              className="aspect-square bg-white rounded-xl border border-slate-200 p-4 shadow-xs hover:border-emerald-500 hover:shadow-lg transition-all flex flex-col text-xs cursor-pointer"
              title="Click to view full details"
            >
              {/* Top: ID + status badges */}
              <div className="flex flex-wrap items-center gap-1.5 mb-2">
                <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                  {item.id}
                </span>
                <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                  item.priority === 'CRITICAL' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'
                }`}>
                  {item.priority}
                </span>
                {isDirectorPending && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-100 text-amber-800">
                    Awaiting Director
                  </span>
                )}
                {isExecutivePending && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-blue-100 text-blue-800">
                    Awaiting Executive
                  </span>
                )}
                {isFullyApproved && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-100 text-emerald-800">
                    ✓ Approved
                  </span>
                )}
                {status === 'Rejected' && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-100 text-rose-800">
                    Rejected
                  </span>
                )}
              </div>

              {/* Middle: title + linked hazard */}
              <div className="flex-1 min-h-0 overflow-hidden">
                <h3 className="font-bold text-slate-900 text-sm leading-tight line-clamp-3 mb-1.5">
                  {item.title}
                </h3>
                {linkedHazard && (
                  <p className="text-[10px] text-slate-500 line-clamp-2">
                    <span className="text-slate-400">Hazard:</span>{' '}
                    {linkedHazard.title}
                    {linkedHazard.community && <span className="text-slate-400"> · {linkedHazard.community}</span>}
                  </p>
                )}
              </div>

              {/* Bottom: cost + action */}
              <div className="pt-2 border-t border-slate-100">
                <div className="flex items-end justify-between mb-2">
                  <div>
                    <div className="text-[9px] text-slate-400 uppercase tracking-wider">Est. Cost</div>
                    <div className="font-mono text-sm font-black text-slate-900 leading-tight">
                      ₦{(item.estimated_cost_ngn / 1e6).toFixed(1)}M
                    </div>
                  </div>
                  {isFullyApproved && item.project_id && (
                    <span className="text-[9px] text-emerald-700 font-semibold">
                      {item.project_id}
                    </span>
                  )}
                </div>

                {/* Action button (compact) */}
                <div onClick={(e) => e.stopPropagation()}>
                  {isFullyApproved && !item.project_id && (
                    <button
                      onClick={() => {
                        setProjectSourceIntervention(item);
                        setIsProjectModalOpen(true);
                      }}
                      className="w-full px-2 py-1.5 rounded-lg text-[10px] font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center justify-center gap-1"
                    >
                      <FolderGit2 className="w-3 h-3" />
                      Create Project
                    </button>
                  )}
                  {item.project_id && (
                    <button
                      onClick={() => {
                        window.dispatchEvent(new CustomEvent('navigate-view', { detail: 'projects' }));
                      }}
                      className="w-full px-2 py-1.5 rounded-lg text-[10px] font-bold bg-slate-700 hover:bg-slate-600 text-white inline-flex items-center justify-center gap-1"
                    >
                      <FolderGit2 className="w-3 h-3" />
                      View Project
                    </button>
                  )}
                  {(canDirectorApprove && isDirectorPending) && (
                    <div className="flex gap-1">
                      <button
                        onClick={() => handleDirectorApprove(item.id)}
                        disabled={approvalBusy === item.id}
                        className="flex-1 px-2 py-1.5 rounded-lg text-[10px] font-bold bg-emerald-700 hover:bg-emerald-800 text-white disabled:opacity-50"
                      >
                        {approvalBusy === item.id ? '…' : 'Approve'}
                      </button>
                      <button
                        onClick={() => handleReject(item.id)}
                        disabled={approvalBusy === item.id}
                        className="px-2 py-1.5 rounded-lg text-[10px] font-bold bg-rose-700 hover:bg-rose-800 text-white disabled:opacity-50"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                  {(canExecutiveApprove && isExecutivePending) && (
                    <div className="flex gap-1">
                      <button
                        onClick={() => handleExecutiveApprove(item.id)}
                        disabled={approvalBusy === item.id}
                        className="flex-1 px-2 py-1.5 rounded-lg text-[10px] font-bold bg-blue-700 hover:bg-blue-800 text-white disabled:opacity-50"
                      >
                        {approvalBusy === item.id ? '…' : 'Executive Approve'}
                      </button>
                      <button
                        onClick={() => handleReject(item.id)}
                        disabled={approvalBusy === item.id}
                        className="px-2 py-1.5 rounded-lg text-[10px] font-bold bg-rose-700 hover:bg-rose-800 text-white disabled:opacity-50"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}'''

new_src, n = pattern.subn(new_card, src)

if n > 0:
    src = new_src
    changes.append(f"card block replaced ({n} match)")
else:
    changes.append("card block pattern NOT FOUND — need manual fix")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)

# Sanity
opens = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")