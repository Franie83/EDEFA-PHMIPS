"""
Replace the current list render with a grid + list toggle.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "action-card-grid" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# Find the section from "{/* Action cards list */}" to the closing of that map
marker = "{/* Action cards list */}"
start = text.find(marker)
if start == -1:
    raise SystemExit("Action cards list marker not found")

# Find the end of the map block — walk forward counting <div> depth
pos = start + len(marker)
depth = 0
opened = False
end = None
while pos < len(text):
    if text.startswith("<div", pos) and (pos + 4 >= len(text) or text[pos+4] in " \t\n>"):
        depth += 1
        opened = True
        pos += 4
        continue
    if text.startswith("</div>", pos):
        depth -= 1
        pos += len("</div>")
        if opened and depth == 0:
            end = pos
            break
        continue
    pos += 1

if end is None:
    raise SystemExit("Could not find end of action cards block")

GRID_VIEW = '''{/* Action cards grid/list */}
      <div>
        {/* View mode toggle */}
        <div className="flex items-center justify-between mb-3">
          <div className="text-[11px] text-slate-500">
            Showing <strong className="text-slate-700">{filteredActions.length}</strong> of{' '}
            <strong className="text-slate-700">{totalActions}</strong> directives
          </div>
          <div className="flex items-center gap-1 bg-white border border-slate-200 rounded-lg p-0.5">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                viewMode === 'grid' ? 'bg-emerald-700 text-white' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                viewMode === 'list' ? 'bg-emerald-700 text-white' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              List
            </button>
          </div>
        </div>

        {/* Grid view — square cards */}
        {viewMode === 'grid' && (
          <div
            id="action-card-grid"
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
          >
            {filteredActions.map(item => {
              const evidenceCount = ((item as any).evidence_files || []).length;
              const priorityColor =
                item.priority === 'CRITICAL' ? 'bg-rose-100 text-rose-800' :
                item.priority === 'HIGH' ? 'bg-amber-100 text-amber-800' :
                item.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                'bg-emerald-100 text-emerald-800';
              const statusColor =
                item.status === 'Verified' ? 'bg-teal-100 text-teal-800' :
                item.status === 'Completed' ? 'bg-blue-100 text-blue-800' :
                item.status === 'Overdue' ? 'bg-rose-100 text-rose-800' :
                item.status === 'In Progress' ? 'bg-indigo-100 text-indigo-800' :
                'bg-slate-100 text-slate-700';
              return (
                <button
                  key={item.id}
                  id={`action-card-${item.id}`}
                  onClick={() => setSelectedActionForDetail(item)}
                  className={`group text-left aspect-square rounded-xl border-2 transition-all p-4 flex flex-col justify-between ${
                    item.is_overdue
                      ? 'bg-rose-50/40 border-rose-300 hover:border-rose-500 hover:shadow-lg'
                      : 'bg-white border-slate-200 hover:border-emerald-500 hover:shadow-lg'
                  }`}
                >
                  {/* Header: ID + priority */}
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                        {item.id}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${priorityColor}`}>
                        {item.priority}
                      </span>
                    </div>

                    {/* Status */}
                    <div className="flex flex-wrap items-center gap-1">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${statusColor}`}>
                        {item.status}
                      </span>
                      {item.is_overdue && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-600 text-white animate-pulse">
                          OVERDUE
                        </span>
                      )}
                    </div>

                    {/* Title */}
                    <h3 className="font-bold text-slate-900 text-sm leading-snug line-clamp-3">
                      {item.title}
                    </h3>
                  </div>

                  {/* Progress bar */}
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-[10px] text-slate-500">
                      <span>Progress</span>
                      <span className="font-mono font-bold text-slate-800">
                        {item.progress_percentage}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          item.progress_percentage === 100 ? 'bg-emerald-600' : 'bg-emerald-500'
                        }`}
                        style={{ width: `${item.progress_percentage}%` }}
                      />
                    </div>
                  </div>

                  {/* Footer: assignee + evidence + due */}
                  <div className="space-y-1.5 text-[10px] text-slate-600 border-t border-slate-100 pt-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="truncate" title={item.responsible_person}>
                        👤 {item.responsible_person || '—'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between gap-2">
                      <span className={item.is_overdue ? 'text-rose-700 font-bold' : ''}>
                        📅 {item.due_date}
                      </span>
                      {evidenceCount > 0 && (
                        <span className="text-emerald-700 font-semibold">
                          📎 {evidenceCount}
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* List view — original card layout (same as before, kept for power users) */}
        {viewMode === 'list' && (
          <div className="space-y-3">
            {filteredActions.map(item => (
              <button
                key={item.id}
                id={`action-row-${item.id}`}
                onClick={() => setSelectedActionForDetail(item)}
                className="w-full text-left bg-white rounded-xl border border-slate-200 p-4 shadow-xs hover:border-emerald-500 transition-colors text-xs space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-2">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                        {item.id}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        item.priority === 'CRITICAL' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {item.priority}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700">
                        {item.status}
                      </span>
                      {item.is_overdue && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-600 text-white animate-pulse">
                          OVERDUE
                        </span>
                      )}
                    </div>
                    <h3 className="font-bold text-slate-900 text-sm mt-1">{item.title}</h3>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 block font-semibold">Due Date</span>
                    <span className={`font-mono text-xs font-bold ${item.is_overdue ? 'text-rose-600' : 'text-slate-800'}`}>
                      {item.due_date}
                    </span>
                  </div>
                </div>
                <p className="text-slate-700 leading-relaxed">{item.description}</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-600 bg-slate-50 p-2.5 rounded-lg">
                  <div><strong>Assigned To:</strong> {item.responsible_person}</div>
                  <div><strong>Organization:</strong> {item.responsible_organization}</div>
                </div>
                <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-500">Progress:</span>
                    <span className="font-bold text-emerald-800">{item.progress_percentage}%</span>
                  </div>
                  <span className="text-[11px] text-emerald-700 font-semibold group-hover:underline">
                    Click to view details →
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>'''

text = text[:start] + GRID_VIEW + text[end:]
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Replaced list with grid + list toggle")
print("  Cards open detail modal on click")