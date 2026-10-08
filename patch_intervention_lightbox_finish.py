"""
patch_intervention_lightbox_finish.py
Finishes the multi-image lightbox upgrade for InterventionPlanning.tsx.
The file has blank lines between JSX attributes; anchors are matched literally.
"""
import pathlib

p = pathlib.Path("src/components/interventions/InterventionPlanning.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# --- 1. Thumbnail click: pass images + index --------------------------------
# Exact bytes from lines 1602-1606 (note the blank lines between attributes):
old_click = """                {allEvidence.map((e: any) => (

                  <div

                    key={e.id}

                    onClick={() => setActiveMedia(e)}
"""
new_click = """                {allEvidence.map((e: any, __idx: number) => (

                  <div

                    key={e.id}

                    onClick={() => setActiveMedia({ images: allEvidence, index: __idx })}
"""
if old_click not in src:
    print("click anchor NOT FOUND")
    raise SystemExit(1)
src = src.replace(old_click, new_click, 1)
changes.append("thumbnail click now passes {images, index}")

# --- 2. Replace the lightbox block -----------------------------------------
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
    print("lightbox anchor NOT FOUND")
    raise SystemExit(1)
src = src.replace(old_lb, new_lb, 1)
changes.append("lightbox replaced with multi-image viewer + prev/next")

p.write_text(src, encoding="utf-8")

print("Changes:")
for c in changes:
    print(" -", c)

opens = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")