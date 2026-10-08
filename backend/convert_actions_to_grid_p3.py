"""
Add the action detail modal that opens when a card is clicked.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "action-detail-modal" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# Insert before the closing </div>
closing_candidates = [
    "\n    </div>\n  );\n};\n",
    "\n  </div>\n  );\n};\n",
    "\n    </div>\n  );\n};",
    "\n  );\n};",
]

insert_at = None
for cand in closing_candidates:
    idx = text.rfind(cand)
    if idx != -1:
        insert_at = idx
        break

if insert_at is None:
    raise SystemExit("Could not find closing pattern")

DETAIL_MODAL = '''
      {/* Action Detail Modal */}
      {selectedActionForDetail && (() => {
        const item = selectedActionForDetail;
        const evidenceFiles = (item as any).evidence_files || [];
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
          <div
            id="action-detail-modal"
            onClick={() => setSelectedActionForDetail(null)}
            className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4"
          >
            <div
              onClick={e => e.stopPropagation()}
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200 text-xs"
            >
              {/* Header */}
              <div className="px-5 py-4 bg-emerald-950 text-white flex items-start justify-between border-b border-emerald-900">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-[10px] text-emerald-300 bg-emerald-900 px-2 py-0.5 rounded">
                      {item.id}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${priorityColor}`}>
                      {item.priority}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${statusColor}`}>
                      {item.status}
                    </span>
                    {item.is_overdue && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-600 text-white animate-pulse">
                        OVERDUE
                      </span>
                    )}
                  </div>
                  <h2 className="text-base font-bold mt-2 max-w-xl">{item.title}</h2>
                </div>
                <button
                  onClick={() => setSelectedActionForDetail(null)}
                  className="p-1.5 rounded bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 shrink-0"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Body */}
              <div className="flex-1 overflow-y-auto p-5 space-y-4">
                {/* Description */}
                {item.description && (
                  <div>
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                      Description
                    </div>
                    <p className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                )}

                {/* Grid of details */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                      Assignment
                    </div>
                    <div className="space-y-1">
                      <div><strong>Person:</strong> {item.responsible_person || '—'}</div>
                      <div><strong>Organization:</strong> {item.responsible_organization || '—'}</div>
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                      Timeline
                    </div>
                    <div className="space-y-1">
                      <div><strong>Due:</strong> {item.due_date || '—'}</div>
                      {item.completion_date && (
                        <div><strong>Completed:</strong> {item.completion_date}</div>
                      )}
                      <div><strong>Created:</strong> {item.created_at?.slice(0, 10) || '—'}</div>
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 sm:col-span-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                        Progress
                      </span>
                      <span className="font-mono font-bold text-slate-800">
                        {item.progress_percentage}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 h-3 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          item.progress_percentage === 100 ? 'bg-emerald-600' : 'bg-emerald-500'
                        }`}
                        style={{ width: `${item.progress_percentage}%` }}
                      />
                    </div>
                  </div>

                  {/* Verification note */}
                  {item.verification_comments && (
                    <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 sm:col-span-2">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 mb-1">
                        Verification
                      </div>
                      <p className="text-emerald-900">{item.verification_comments}</p>
                      {item.verified_by && (
                        <div className="text-[11px] text-emerald-700 mt-1">
                          by {item.verified_by}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Evidence gallery */}
                <div>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                    <Paperclip className="w-3.5 h-3.5" />
                    Evidence ({evidenceFiles.length})
                  </div>
                  {evidenceFiles.length === 0 ? (
                    <div className="p-4 rounded-lg border border-dashed border-slate-300 text-center text-slate-400">
                      No evidence uploaded yet.
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {evidenceFiles.map((ev: any) => (
                        <button
                          key={ev.id}
                          onClick={() => setPreviewItem({ evidence: ev, action: item })}
                          className="group text-left rounded-lg border border-slate-200 bg-slate-50 hover:border-emerald-500 overflow-hidden"
                        >
                          {ev.media_type === 'photo' || ev.file_type?.startsWith('image') ? (
                            <img
                              src={ev.file_url}
                              alt={ev.file_name}
                              className="w-full h-24 object-cover"
                              onError={(e) => {
                                (e.target as HTMLImageElement).style.display = 'none';
                              }}
                            />
                          ) : (
                            <div className="w-full h-24 flex items-center justify-center bg-white">
                              <FileText className="w-8 h-8 text-slate-400" />
                            </div>
                          )}
                          <div className="p-2 text-[10px] text-slate-700 truncate">
                            {ev.file_name}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Footer — actions */}
              <div className="px-5 py-3 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-end gap-2">
                {item.status !== 'Completed' && item.status !== 'Verified' && (
                  <button
                    onClick={() => { setSelectedActionForDetail(null); openEvidenceModal(item); }}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-100 hover:bg-amber-200 text-amber-800 inline-flex items-center gap-1.5"
                  >
                    <Upload className="w-3.5 h-3.5" />
                    Upload Evidence
                  </button>
                )}
                {item.status !== 'Completed' && item.status !== 'Verified' && (
                  <button
                    onClick={() => { setSelectedActionForDetail(null); handleMarkCompleted(item); }}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-700 hover:bg-emerald-800 text-white"
                  >
                    Mark Completed
                  </button>
                )}
                {item.status === 'Completed' && (
                  <button
                    onClick={() => { setSelectedActionForDetail(null); handleVerifyClose(item); }}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-700 hover:bg-blue-800 text-white"
                  >
                    Verify & Close
                  </button>
                )}
                {canEditActionMetadata && (
                  <button
                    onClick={() => { setSelectedActionForDetail(null); openEditModal(item); }}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 inline-flex items-center gap-1.5"
                  >
                    <Pencil className="w-3.5 h-3.5" />
                    Edit
                  </button>
                )}
                {currentRole === 'SUPER_ADMIN' && (
                  <button
                    onClick={() => { setSelectedActionForDetail(null); handleDeleteAction(item); }}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-100 hover:bg-rose-200 text-rose-800 inline-flex items-center gap-1.5"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Delete
                  </button>
                )}
                <button
                  onClick={() => setSelectedActionForDetail(null)}
                  className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-100"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        );
      })()}
'''

text = text[:insert_at] + DETAIL_MODAL + text[insert_at:]
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Added action detail modal")