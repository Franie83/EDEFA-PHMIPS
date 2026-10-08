import pathlib
import re

p = pathlib.Path("src/components/public/PublicTrackPage.tsx")
src = p.read_text(encoding="utf-8")

# Replace the entire "Photographic Evidence" section with a clean version
pattern = re.compile(
    r"\{/\* Evidence gallery \*/\}.*?\{/\* Intervention \*/\}",
    re.DOTALL
)

replacement = '''{/* Evidence gallery */}
              {result.evidence && result.evidence.length > 0 && (
                <div className="rounded-lg bg-slate-800 border border-slate-700 p-4">
                  <div className="text-[10px] uppercase tracking-wider text-slate-400 mb-3 font-bold flex items-center gap-1.5">
                    <Camera className="w-3 h-3" /> Photographic Evidence ({result.evidence.length})
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {result.evidence.map((e: any) => (
                      <div
                        key={e.id}
                        onClick={() => setActiveMedia(e)}
                        className="relative rounded-lg overflow-hidden border border-slate-700 bg-slate-900 cursor-pointer group"
                        title={e.description || e.file_name}
                      >
                        {e.media_type === 'photo' ? (
                          <img
                            src={e.file_url}
                            alt={e.description || e.file_name}
                            className="w-full h-24 object-cover group-hover:scale-105 transition-transform"
                          />
                        ) : (
                          <div className="w-full h-24 flex items-center justify-center bg-slate-800">
                            <Video className="w-8 h-8 text-slate-500" />
                          </div>
                        )}
                        {e.stage_tag && (
                          <span className={`absolute top-1 left-1 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider border ${STAGE_COLORS[e.stage_tag] || STAGE_COLORS.evidence}`}>
                            {e.stage_tag}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Intervention */}'''

new_src, n = pattern.subn(replacement, src)

if n > 0:
    p.write_text(new_src, encoding="utf-8")
    print(f"Replaced evidence gallery ({n} match)")
else:
    print("Pattern not found — paste the current evidence gallery block:")
    print("  Get-Content src\\components\\public\\PublicTrackPage.tsx | Select-Object -Skip 175 -First 45")