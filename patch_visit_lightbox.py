import pathlib

p = pathlib.Path("src/components/field/FieldVisitList.tsx")
src = p.read_text(encoding="utf-8")

# Find the very last "</div>\n  );\n};" in the file (end of FieldVisitList component)
# We insert the lightbox just before the outer closing div

marker = """      </div>
    </div>
  );
};"""
lightbox = """      </div>
    </div>

      {/* Lightbox for evidence preview */}
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
    </div>
  );
};"""

if marker in src and "Lightbox for evidence preview" not in src:
    src = src.replace(marker, lightbox, 1)
    p.write_text(src, encoding="utf-8")
    print("Inserted lightbox for evidence preview")
else:
    print("Lightbox marker NOT FOUND or already present")