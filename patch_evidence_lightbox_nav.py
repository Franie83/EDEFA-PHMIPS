"""
patch_evidence_lightbox_nav.py
Upgrades the single-image lightbox in FieldVisitList and InterventionPlanning
to a multi-image viewer with prev/next navigation and keyboard support.

Changes state from:
    activeMedia: Evidence | null
to:
    activeMedia: { images: Evidence[]; index: number } | null
"""
import pathlib

# =========================================================================
# PART 1 — FieldVisitList.tsx
# =========================================================================
fv = pathlib.Path("src/components/field/FieldVisitList.tsx")
src = fv.read_text(encoding="utf-8")
fv_changes = []

if "images: any[]; index: number" in src:
    print("FieldVisitList: already patched")
else:
    # 1a. New state type
    old_state = "  const [activeMedia, setActiveMedia] = useState<any | null>(null);\n"
    new_state = "  const [activeMedia, setActiveMedia] = useState<{ images: any[]; index: number } | null>(null);\n"
    if old_state not in src:
        print("FieldVisitList: state anchor NOT FOUND")
        raise SystemExit(1)
    src = src.replace(old_state, new_state, 1)
    fv_changes.append("state type upgraded to { images, index }")

    # 1b. Thumbnail click — capture the per-visit evidence list
    old_click = """                  {evidenceByVisit[visit.id].map((e: any) => (
                    <div
                      key={e.id}
                      onClick={() => setActiveMedia(e)}
"""
    new_click = """                  {evidenceByVisit[visit.id].map((e: any, __idx: number) => (
                    <div
                      key={e.id}
                      onClick={() => setActiveMedia({ images: evidenceByVisit[visit.id], index: __idx })}
"""
    if old_click not in src:
        print("FieldVisitList: thumbnail-click anchor NOT FOUND")
        raise SystemExit(1)
    src = src.replace(old_click, new_click, 1)
    fv_changes.append("thumbnail click passes images+index")

    # 1c. Replace the lightbox block
    old_lightbox = """      {/* Lightbox for evidence preview */}
      {activeMedia && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
          onClick={() => setActiveMedia(null)}
        >
          <div
            className="max-w-4xl w-full"
            onClick={(e) => e.stopPropagation()}
          >
            {activeMedia.media_type === 'photo' ? (
              <img
                src={activeMedia.file_url}
                alt={activeMedia.file_name}
                className="w-full max-h-[80vh] object-contain rounded-lg"
              />
            ) : (
              <video controls autoPlay className="w-full max-h-[80vh] rounded-lg">
                <source src={activeMedia.file_url} type="video/mp4" />
              </video>
            )}
            <div className="mt-3 text-center text-xs text-slate-300">
              <div className="font-semibold">{activeMedia.description || activeMedia.file_name}</div>
              {activeMedia.stage_tag && (
                <div className="text-[10px] uppercase tracking-wider mt-1 text-slate-400">
                  {activeMedia.stage_tag}
                </div>
              )}
              <button
                onClick={() => setActiveMedia(null)}
                className="mt-3 px-4 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
"""

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
            className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
            onClick={() => setActiveMedia(null)}
            onKeyDown={(e) => {
              if (e.key === 'Escape') setActiveMedia(null);
              else if (e.key === 'ArrowLeft') goPrev();
              else if (e.key === 'ArrowRight') goNext();
            }}
            tabIndex={0}
            ref={(el) => el && el.focus()}
          >
            <button
              onClick={(e) => { e.stopPropagation(); goPrev(); }}
              disabled={images.length <= 1}
              className="absolute left-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white disabled:opacity-30 disabled:cursor-not-allowed z-10"
              title="Previous (←)"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15 18l-6-6 6-6" /></svg>
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); goNext(); }}
              disabled={images.length <= 1}
              className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white disabled:opacity-30 disabled:cursor-not-allowed z-10"
              title="Next (→)"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18l6-6-6-6" /></svg>
            </button>

            <div
              className="max-w-4xl w-full relative"
              onClick={(e) => e.stopPropagation()}
            >
              {images.length > 1 && (
                <div className="absolute top-2 right-2 px-2.5 py-1 rounded-full bg-black/60 text-white text-[11px] font-semibold z-10">
                  {idx + 1} of {images.length}
                </div>
              )}
              {current.media_type === 'photo' ? (
                <img
                  src={current.file_url}
                  alt={current.file_name}
                  className="w-full max-h-[80vh] object-contain rounded-lg"
                />
              ) : (
                <video key={current.id} controls autoPlay className="w-full max-h-[80vh] rounded-lg">
                  <source src={current.file_url} type="video/mp4" />
                </video>
              )}
              <div className="mt-3 text-center text-xs text-slate-300">
                <div className="font-semibold">{current.description || current.file_name}</div>
                {current.stage_tag && (
                  <div className="text-[10px] uppercase tracking-wider mt-1 text-slate-400">
                    {current.stage_tag}
                  </div>
                )}
                <button
                  onClick={() => setActiveMedia(null)}
                  className="mt-3 px-4 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-xs"
                >
                  Close (Esc)
                </button>
              </div>
            </div>
          </div>
        );
      })()}
"""
    if old_lightbox not in src:
        print("FieldVisitList: lightbox block anchor NOT FOUND")
        raise SystemExit(1)
    src = src.replace(old_lightbox, new_lightbox, 1)
    fv_changes.append("replaced single-image lightbox with multi-image viewer")

    fv.write_text(src, encoding="utf-8")

# =========================================================================
# PART 2 — InterventionPlanning.tsx (same treatment)
# =========================================================================
ip = pathlib.Path("src/components/interventions/InterventionPlanning.tsx")
src = ip.read_text(encoding="utf-8")
ip_changes = []

if "images: any[]; index: number" in src:
    print("InterventionPlanning: already patched")
else:
    # 2a. State
    old_state = "  const [activeMedia, setActiveMedia] = React.useState<any | null>(null);\n"
    new_state = "  const [activeMedia, setActiveMedia] = React.useState<{ images: any[]; index: number } | null>(null);\n"
    if old_state not in src:
        print("InterventionPlanning: state anchor NOT FOUND — skipping")
    else:
        src = src.replace(old_state, new_state, 1)
        ip_changes.append("state type upgraded")

        # 2b. Thumbnail click — need to see the surrounding map to know what list to capture.
        #     From the grep, the map is over `allEvidence` (or similar). We match the loose anchor:
        old_click = """                    key={e.id}
                    onClick={() => setActiveMedia(e)}
"""
        new_click = """                    key={e.id}
                    onClick={() => setActiveMedia({ images: allEvidence, index: allEvidence.findIndex((x: any) => x.id === e.id) })}
"""
        if old_click not in src:
            print("InterventionPlanning: thumbnail-click anchor NOT FOUND — skipping click update")
        else:
            src = src.replace(old_click, new_click, 1)
            ip_changes.append("thumbnail click passes images+index")

        # 2c. Lightbox block — match the grep'd shape
        old_lb = """      {activeMedia && (
        <div
          onClick={(e) => { e.stopPropagation(); setActiveMedia(null); }}
          className="fixed inset-0 z-[60] bg-black/90 flex items-center justify-center p-4"
        >
          <img src={activeMedia.file_url} alt={activeMedia.file_name} className="max-w-full max-h-[85vh] rounded-lg object-contain" />
        </div>
      )}
"""
        new_lb = """      {activeMedia && (() => {
        const images = activeMedia.images || [];
        const idx = activeMedia.index || 0;
        const current = images[idx];
        if (!current) return null;
        const goPrev = () => setActiveMedia({ images, index: (idx - 1 + images.length) % images.length });
        const goNext = () => setActiveMedia({ images, index: (idx + 1) % images.length });
        return (
          <div
            onClick={(e) => { e.stopPropagation(); setActiveMedia(null); }}
            onKeyDown={(e) => {
              if (e.key === 'Escape') setActiveMedia(null);
              else if (e.key === 'ArrowLeft') goPrev();
              else if (e.key === 'ArrowRight') goNext();
            }}
            tabIndex={0}
            ref={(el) => el && el.focus()}
            className="fixed inset-0 z-[60] bg-black/90 flex items-center justify-center p-4"
          >
            <button
              onClick={(e) => { e.stopPropagation(); goPrev(); }}
              disabled={images.length <= 1}
              className="absolute left-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white disabled:opacity-30 disabled:cursor-not-allowed"
              title="Previous (←)"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15 18l-6-6 6-6" /></svg>
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); goNext(); }}
              disabled={images.length <= 1}
              className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white disabled:opacity-30 disabled:cursor-not-allowed"
              title="Next (→)"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18l6-6-6-6" /></svg>
            </button>
            {images.length > 1 && (
              <div className="absolute top-3 right-3 px-2.5 py-1 rounded-full bg-black/70 text-white text-[11px] font-semibold">
                {idx + 1} of {images.length}
              </div>
            )}
            <img
              src={current.file_url}
              alt={current.file_name}
              className="max-w-full max-h-[85vh] rounded-lg object-contain"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        );
      })()}
"""
        if old_lb not in src:
            print("InterventionPlanning: lightbox anchor NOT FOUND — skipping")
        else:
            src = src.replace(old_lb, new_lb, 1)
            ip_changes.append("replaced lightbox with multi-image viewer")
            ip.write_text(src, encoding="utf-8")

print("FieldVisitList changes:")
for c in fv_changes:
    print(" -", c)
print("InterventionPlanning changes:")
for c in ip_changes:
    print(" -", c)

for label, s in [("FieldVisitList", fv.read_text(encoding="utf-8")),
                 ("InterventionPlanning", ip.read_text(encoding="utf-8"))]:
    o, c = s.count("{"), s.count("}")
    print(f"{label} brace balance: {'OK' if o == c else f'MISMATCH ({o} vs {c})'}")