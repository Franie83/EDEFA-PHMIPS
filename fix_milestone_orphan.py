import pathlib

p = pathlib.Path("src/components/projects/ProjectDetailModal.tsx")
src = p.read_text(encoding="utf-8")

# The orphaned block left behind after the row's closing </div>
orphan = """                  </div>
                    <div>
                      <div className="font-semibold text-slate-900">{m.title}</div>
                      <div className="text-[10px] text-slate-500">Target Date: {m.due_date}</div>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        m.status === 'Completed'
                          ? 'bg-emerald-100 text-emerald-800'
                          : m.status === 'In Progress'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-slate-100 text-slate-600'
                      }`}>
                        {m.status} ({m.progress_percentage}%)
                      </span>
                    </div>
                  </div>
                ))"""

replacement = """                  </div>
                ))"""

if orphan in src:
    src = src.replace(orphan, replacement)
    p.write_text(src, encoding="utf-8")
    print("Removed orphaned JSX block")
else:
    # Try a slightly looser version
    import re
    # Match from "                    <div>\n" (indented 20 spaces) that starts the orphan
    pattern = re.compile(
        r'\n\s{20}<div>\s*\n\s*<div className="font-semibold text-slate-900">\{m\.title\}</div>.*?\n\s*</div>\n\s*\}\)\)',
        re.DOTALL
    )
    new_src, n = pattern.subn("\n                ))", src)
    if n:
        p.write_text(new_src, encoding="utf-8")
        print(f"Removed orphaned block via regex ({n} match)")
    else:
        print("Pattern not found. Showing context:")
        print(src[src.find("m.status === 'Completed'"):src.find("m.status === 'Completed'")+800])

# Sanity check braces
print(f"\nBrace balance: {'OK' if src.count('{') == src.count('}') else 'MISMATCH'}")