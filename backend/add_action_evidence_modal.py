"""
1. Add api.uploadActionEvidence to api.ts
2. Insert evidence gallery, upload modal, and preview lightbox into ActionTracking.tsx
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
API_TS = ROOT / "src" / "services" / "api.ts"
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

# ============================================================
# 1. api.ts
# ============================================================
print("=" * 60)
print("PATCH 1: src/services/api.ts")
print("=" * 60)

api_text = API_TS.read_text(encoding="utf-8")

if "uploadActionEvidence" in api_text:
    print("  Already present — skipping.")
else:
    anchor = "  deleteAction: (id: string) => request<{ success: boolean; deleted_id: string }>(`/actions/${id}`, {"
    if anchor not in api_text:
        raise SystemExit("deleteAction anchor not found in api.ts")
    new_method = '''  uploadActionEvidence: (id: string, data: any) =>
    request<{ success: boolean; evidence: any; action: ActionItem }>(`/actions/${id}/evidence`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  deleteAction: (id: string) => request<{ success: boolean; deleted_id: string }>(`/actions/${id}`, {'''
    api_text = api_text.replace(anchor, new_method, 1)
    API_TS.write_text(api_text, encoding="utf-8")
    print("  Added api.uploadActionEvidence")

# ============================================================
# 2. ActionTracking.tsx — evidence gallery + modals
# ============================================================
print()
print("=" * 60)
print("PATCH 2: ActionTracking.tsx")
print("=" * 60)

text = TARGET.read_text(encoding="utf-8")

if "evidence-gallery" in text:
    print("  Already patched — skipping.")
    raise SystemExit(0)

# 2a — Insert evidence gallery block inside each action card, just before the closing action-buttons div
# Find the "Verification Note" or similar anchor, and insert after the info grid
anchor = 'className="pt-2 border-t border-slate-100 flex items-center justify-between"'
idx = text.find(anchor)
if idx == -1:
    raise SystemExit("Could not find the actions button row anchor in the card")

# Walk back to find the enclosing <div
container_start = text.rfind("<div", 0, idx)

EVIDENCE_GALLERY = '''{/* Evidence gallery */}
            {(item as any).evidence_files?.length > 0 && (
              <div id="evidence-gallery" className="pt-2 border-t border-slate-100">
                <div className="text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Paperclip className="w-3.5 h-3.5" />
                  Evidence ({(item as any).evidence_files.length})
                </div>
                <div className="flex flex-wrap gap-2">
                  {(item as any).evidence_files.map((ev: any) => (
                    <button
                      key={ev.id}
                      onClick={() => setPreviewItem({ evidence: ev, action: item })}
                      className="group flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 hover:border-emerald-500 transition"
                      title="Click to preview"
                    >
                      {ev.media_type === 'photo' || ev.file_type?.startsWith('image') ? (
                        <img
                          src={ev.file_url}
                          alt={ev.file_name}
                          className="w-8 h-8 rounded object-cover"
                          onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                        />
                      ) : (
                        <FileText className="w-4 h-4 text-slate-500" />
                      )}
                      <span className="text-[11px] text-slate-700 font-medium truncate max-w-[160px]">
                        {ev.file_name}
                      </span>
                      <ExternalLink className="w-3 h-3 text-slate-400 group-hover:text-emerald-600" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            '''

text = text[:container_start] + EVIDENCE_GALLERY + text[container_start:]
print("  Inserted evidence gallery in each card")

# 2b — Add "Upload Evidence" button in the button row
marker = '''{canEditActionMetadata && ('''
if marker in text:
    # Insert upload button before Edit
    upload_btn = '''{item.status !== 'Verified' && item.status !== 'Closed' && (
                  <button
                    onClick={() => openEvidenceModal(item)}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-100 hover:bg-amber-200 text-amber-800 inline-flex items-center gap-1.5"
                    title="Upload completion evidence"
                  >
                    <Upload className="w-3.5 h-3.5" />
                    Upload Evidence
                  </button>
                )}
                {canEditActionMetadata && ('''
    text = text.replace(marker, upload_btn, 1)
    print("  Inserted Upload Evidence button")

# 2c — Gate the Edit button by role
old_edit = '''<button
                  onClick={() => openEditModal(item)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 inline-flex items-center gap-1.5"
                  title="Edit this action"
                >
                  <Pencil className="w-3.5 h-3.5" />
                  Edit
                </button>'''
new_edit = '''{canEditActionMetadata && (
                  <button
                    onClick={() => openEditModal(item)}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 inline-flex items-center gap-1.5"
                    title="Edit this action"
                  >
                    <Pencil className="w-3.5 h-3.5" />
                    Edit
                  </button>
                )}'''
if old_edit in text:
    text = text.replace(old_edit, new_edit, 1)
    print("  Gated Edit button by role")

# 2d — Gate the Delete button by role (Super Admin only)
old_del = '''<button
                  onClick={() => handleDeleteAction(item)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-100 hover:bg-rose-200 text-rose-800 inline-flex items-center gap-1.5"
                  title="Delete this action"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Delete
                </button>'''
new_del = '''{currentRole === 'SUPER_ADMIN' && (
                  <button
                    onClick={() => handleDeleteAction(item)}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-100 hover:bg-rose-200 text-rose-800 inline-flex items-center gap-1.5"
                    title="Delete this action (Super Admin only)"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Delete
                  </button>
                )}'''
if old_del in text:
    text = text.replace(old_del, new_del, 1)
    print("  Gated Delete button to Super Admin")

# 2e — Insert the evidence upload modal + preview lightbox before the closing </div>
closing = "\n    </div>\n  );\n};"
if closing not in text:
    closing = "\n  );\n};"
    if closing not in text:
        raise SystemExit("Could not find component closing")

MODALS = '''
      {/* Evidence Upload Modal */}
      {evidenceForAction && (
        <div className="fixed inset-0 z-[60] overflow-y-auto bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200 text-xs">
            <div className="px-5 py-4 bg-emerald-950 text-white flex items-center justify-between border-b border-emerald-900">
              <div>
                <h2 className="text-sm font-bold">Upload Completion Evidence</h2>
                <p className="text-[11px] text-emerald-300">
                  For action {evidenceForAction.id} — {evidenceForAction.title}
                </p>
              </div>
              <button
                onClick={() => setEvidenceForAction(null)}
                className="p-1 rounded bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-5 space-y-3">
              {evidenceError && (
                <div className="rounded-lg bg-rose-50 border border-rose-200 text-rose-800 p-2.5">
                  {evidenceError}
                </div>
              )}
              <label className="block">
                <span className="font-semibold text-slate-700">Choose file (image or PDF)</span>
                <input
                  type="file"
                  accept="image/*,application/pdf"
                  onChange={handleEvidenceFilePick}
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                />
              </label>
              {evidenceFile && (
                <div className="rounded-lg border border-slate-200 p-3 bg-slate-50">
                  <div className="text-[11px] text-slate-600 mb-2">
                    <strong>{evidenceFileName}</strong> — {evidenceFileType}
                  </div>
                  {evidenceFileType.startsWith('image') && (
                    <img
                      src={evidenceFile}
                      alt="preview"
                      className="max-h-48 rounded object-contain mx-auto"
                    />
                  )}
                </div>
              )}
              <label className="block">
                <span className="font-semibold text-slate-700">Description</span>
                <textarea
                  value={evidenceDescription}
                  onChange={e => setEvidenceDescription(e.target.value)}
                  rows={2}
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 resize-y"
                  placeholder="What does this evidence show?"
                />
              </label>
            </div>
            <div className="px-5 py-3 border-t border-slate-200 flex items-center justify-end gap-2">
              <button
                onClick={() => setEvidenceForAction(null)}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={submitEvidence}
                disabled={evidenceBusy || !evidenceFile}
                className="px-5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white disabled:opacity-50 inline-flex items-center gap-1.5"
              >
                <Upload className="w-4 h-4" />
                {evidenceBusy ? 'Uploading…' : 'Upload Evidence'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Evidence Preview Lightbox */}
      {previewItem && (
        <div
          onClick={() => setPreviewItem(null)}
          className="fixed inset-0 z-[70] bg-black/80 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto"
        >
          <div
            onClick={e => e.stopPropagation()}
            className="bg-white rounded-xl max-w-3xl w-full p-5 space-y-4 my-8"
          >
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">{previewItem.evidence.file_name}</h3>
                <p className="text-[11px] text-slate-500">
                  {previewItem.action.id} — {previewItem.action.title}
                </p>
              </div>
              <button
                onClick={() => setPreviewItem(null)}
                className="p-1 rounded hover:bg-slate-100 text-slate-500"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* File preview */}
            <div className="rounded-lg bg-slate-900 flex items-center justify-center min-h-[280px] max-h-[60vh] overflow-hidden">
              {previewItem.evidence.media_type === 'photo'
                || previewItem.evidence.file_type?.startsWith('image') ? (
                <img
                  src={previewItem.evidence.file_url}
                  alt={previewItem.evidence.file_name}
                  className="max-h-[60vh] w-auto object-contain"
                />
              ) : previewItem.evidence.file_type === 'application/pdf' ? (
                <iframe
                  src={previewItem.evidence.file_url}
                  className="w-full h-[60vh]"
                  title={previewItem.evidence.file_name}
                />
              ) : (
                <div className="text-white text-center p-6">
                  <FileText className="w-12 h-12 mx-auto text-slate-500 mb-2" />
                  <p className="text-sm">Preview not available</p>
                  <a
                    href={previewItem.evidence.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 inline-block text-amber-400 hover:text-amber-300 underline text-xs"
                  >
                    Download file
                  </a>
                </div>
              )}
            </div>

            {/* Action & evidence details */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px]">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <div className="font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Action
                </div>
                <div><strong>ID:</strong> {previewItem.action.id}</div>
                <div><strong>Priority:</strong> {previewItem.action.priority}</div>
                <div><strong>Status:</strong> {previewItem.action.status}</div>
                <div><strong>Due:</strong> {previewItem.action.due_date}</div>
                {previewItem.action.completion_date && (
                  <div><strong>Completed:</strong> {previewItem.action.completion_date}</div>
                )}
                <div><strong>Assignee:</strong> {previewItem.action.responsible_person}</div>
                <div><strong>Organization:</strong> {previewItem.action.responsible_organization}</div>
                <div><strong>Progress:</strong> {previewItem.action.progress_percentage}%</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <div className="font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Evidence
                </div>
                <div><strong>Uploaded:</strong> {previewItem.evidence.upload_date}</div>
                <div><strong>By:</strong> {previewItem.evidence.uploader_name}</div>
                <div><strong>Type:</strong> {previewItem.evidence.media_type}</div>
                {previewItem.evidence.gps_latitude && (
                  <div>
                    <strong>GPS:</strong>{' '}
                    <span className="font-mono">
                      {previewItem.evidence.gps_latitude?.toFixed(5)},{' '}
                      {previewItem.evidence.gps_longitude?.toFixed(5)}
                    </span>
                  </div>
                )}
                {previewItem.evidence.description && (
                  <div className="mt-1 italic text-slate-600">
                    "{previewItem.evidence.description}"
                  </div>
                )}
              </div>
            </div>

            <div className="text-right">
              <a
                href={previewItem.evidence.file_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-xs text-emerald-700 hover:text-emerald-900 font-semibold"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                Open in new tab
              </a>
            </div>
          </div>
        </div>
      )}

'''

text = text.replace(closing, MODALS + closing, 1)
print("  Inserted evidence upload modal + preview lightbox")

TARGET.write_text(text, encoding="utf-8")
print()
print(f"Patched {TARGET.name}")