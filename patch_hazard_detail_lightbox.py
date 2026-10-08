"""
patch_hazard_detail_lightbox.py
Upgrades HazardDetailModal's single-image lightbox to a multi-image viewer
with prev/next navigation, keyboard support, counter, and video handling.
Same pattern as FieldVisitList and InterventionPlanning.
"""
import pathlib

p = pathlib.Path("src/components/hazards/HazardDetailModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# --- 1. Upgrade state type ---------------------------------------------------
old_state = "  const [activeMedia, setActiveMedia] = useState<Evidence | null>(null);\n"
new_state = "  const [activeMedia, setActiveMedia] = useState<{ images: Evidence[]; index: number } | null>(null);\n"
if old_state not in src:
    print("State anchor NOT FOUND")
    raise SystemExit(1)
src = src.replace(old_state, new_state, 1)
changes.append("upgraded activeMedia to { images, index }")

# --- 2. Thumbnail click: pass full list + index ------------------------------
# Current: onClick={() => setActiveMedia(ev)}
# New:     onClick={() => setActiveMedia({ images: h.evidence_files, index: idx })}
old_click = """                {h.evidence_files.map(ev => (
                  <div
                    key={ev.id}
                    onClick={() => setActiveMedia(ev)}
"""
new_click = """                {h.evidence_files.map((ev, __idx) => (
                  <div
                    key={ev.id}
                    onClick={() => setActiveMedia({ images: h.evidence_files || [], index: __idx })}
"""
if old_click not in src:
    print("Thumbnail click anchor NOT FOUND")
    raise SystemExit(1)
src = src.replace(old_click, new_click, 1)
changes.append("thumbnail click now passes { images, index }")

# --- 3. Replace the lightbox block ------------------------------------------
# Match the whole lightbox from `{activeMedia && (` to its final `)}`.
# We anchor on the specific beginning and reconstruct the entire block.
old_lightbox = """      {/* Lightbox / Media Viewer Modal */}
      {activeMedia && (
        <div
          onClick={() => setActiveMedia(null)}
          className="fixed inset-0 z-60 bg-black/80 flex items-center justify-center p-4"
        >
          <div
            onClick={e => e.stopPropagation()}
"""
# Find the lightbox and replace everything up to the final closing of the block.
# Simpler: use a regex that captures from `{activeMedia && (` to the matching
# `\n      )}\n` before `    </div>\n  );\n};` or end-of-file.
import re

# Locate the lightbox block start
start_marker = """      {/* Lightbox / Media Viewer Modal */}
      {activeMedia && (
"""
idx = src.find(start_marker)
if idx < 0:
    print("Lightbox start NOT FOUND")
    raise SystemExit(1)

# Find end: the lightbox closes with `      )}\n` at column 6, and the next
# non-empty line starts with `    </div>` (closing the root modal) or similar.
# Search from the start index for the pattern `\n      )}\n` where the line
# before is `        </div>\n` (closing the inner wrapper div).
search_from = idx + len(start_marker)
end_pattern = re.compile(r"\n      \)\}\n(?=\s*\n?\s*</div>|\s*\n?\s*\))")
m_end = end_pattern.search(src, search_from)
if not m_end:
    print("Lightbox end NOT FOUND")
    raise SystemExit(1)

lightbox_start = idx
lightbox_end = m_end.end()   # includes the trailing newline

new_lightbox = """      {/* Multi-image evidence lightbox with prev/next */}
      {activeMedia && (() => {
        const images = activeMedia.images || [];
        const idx = activeMedia.index || 0;
        const current = images[idx];
        if (!current) return null;
        const goPrev = () => setActiveMedia({ images, index: (idx - 1 + images.length) % images.length });
        const goNext = () => setActiveMedia({ images, index: (idx + 1) % images.length });
        return (
          <div
            className="fixed inset-0 z-[60] bg-black/85 flex items-center justify-center p-4"
            onClick={() => setActiveMedia(null)}
            onKeyDown={(e) => {
              if (e.key === 'Escape') setActiveMedia(null);
              else if (e.key === 'ArrowLeft') goPrev();
              else if (e.key === 'ArrowRight') goNext();
            }}
            tabIndex={0}
            ref={(el) => el && el.focus()}
          >
            <div
              onClick={e => e.stopPropagation()}
              className="bg-slate-900 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden border border-slate-700"
            >
              <div className="flex items-center justify-between border-b border-slate-700 px-4 py-3">
                <div className="min-w-0 flex-1">
                  <h3 className="font-bold text-sm text-white truncate">{current.file_name}</h3>
                  {current.description && (
                    <p className="text-xs text-slate-400 truncate">{current.description}</p>
                  )}
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  {images.length > 1 && (
                    <span className="px-2.5 py-1 rounded-full bg-black/60 text-white text-[11px] font-semibold">
                      {idx + 1} of {images.length}
                    </span>
                  )}
                  <button
                    onClick={() => setActiveMedia(null)}
                    className="p-1 rounded bg-slate-800 text-slate-300 hover:text-white"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="relative flex-1 flex items-center justify-center bg-black/50 min-h-[300px]">
                {images.length > 1 && (
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); goPrev(); }}
                    className="absolute left-3 top-1/2 -translate-y-1/2 p-2.5 rounded-full bg-white/10 hover:bg-white/25 text-white z-10"
                    title="Previous (←)"
                  >
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M15 18l-6-6 6-6" /></svg>
                  </button>
                )}
                {current.media_type === 'photo' ? (
                  <img src={current.file_url} alt={current.file_name} className="max-h-[65vh] w-auto object-contain" />
                ) : (
                  <video key={current.id} controls autoPlay className="max-h-[65vh] w-full">
                    <source src={current.file_url} type="video/mp4" />
                    Your browser does not support HTML5 video.
                  </video>
                )}
                {images.length > 1 && (
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); goNext(); }}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-2.5 rounded-full bg-white/10 hover:bg-white/25 text-white z-10"
                    title="Next (→)"
                  >
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M9 18l6-6-6-6" /></svg>
                  </button>
                )}
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400 px-4 py-3 border-t border-slate-700">
                <span>Uploaded by {current.uploader_name} on {current.upload_date}</span>
                {current.gps_latitude != null && (
                  <span className="font-mono">
                    GPS: {current.gps_latitude.toFixed(5)}, {current.gps_longitude?.toFixed(5)}
                  </span>
                )}
              </div>
            </div>
          </div>
        );
      })()}
"""

src = src[:lightbox_start] + new_lightbox + src[lightbox_end:]
changes.append("replaced single-image lightbox with multi-image viewer")

p.write_text(src, encoding="utf-8")

print("Changes:")
for c in changes:
    print(" -", c)

o, c = src.count("{"), src.count("}")
print(f"\nHazardDetailModal.tsx brace balance: {'OK' if o == c else f'MISMATCH ({o} vs {c})'}")