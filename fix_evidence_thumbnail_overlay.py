import pathlib

p = pathlib.Path("src/components/public/PublicTrackPage.tsx")
src = p.read_text(encoding="utf-8")

# The current evidence card renders the filename as part of the layout, not just on hover.
# Find the current map block and replace with one that hides the label by default.

old = """                    {result.evidence.map((e: any) => (
                      <div
                        key={e.id}
                        onClick={() => setActiveMedia(e)}
                        className="relative rounded-lg overflow-hidden border border-slate-700 bg-slate-900 cursor-pointer group"
                      >
                        {e.media_type === 'photo' ? (
                          <img src={e.file_url} alt={e.file_name} className="w-full h-24 object-cover group-hover:scale-105 transition-transform" />
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
                    ))}"""

new = """                    {result.evidence.map((e: any) => (
                      <div
                        key={e.id}
                        onClick={() => setActiveMedia(e)}
                        className="relative rounded-lg overflow-hidden border border-slate-700 bg-slate-900 cursor-pointer group"
                        title={e.file_name}
                      >
                        {e.media_type === 'photo' ? (
                          <img src={e.file_url} alt={e.file_name} className="w-full h-24 object-cover group-hover:scale-105 transition-transform" />
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
                        {/* Show description or filename only on hover */}
                        <div className="absolute inset-x-0 bottom-0 bg-black/80 px-2 py-1 text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity truncate">
                          {e.description || e.file_name}
                        </div>
                      </div>
                    ))}"""

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Fixed evidence thumbnail — filename now shows only on hover")
else:
    print("Evidence thumbnail block NOT FOUND — pattern may differ")