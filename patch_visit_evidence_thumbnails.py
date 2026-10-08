import pathlib

p = pathlib.Path("src/components/field/FieldVisitList.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add Camera + Play to lucide imports
old_import = """import {
  Search,
  MapPin,
  Calendar,
  User,
  ClipboardList,
  Filter,
  X,
  RotateCcw,
} from 'lucide-react';"""
new_import = """import {
  Search,
  MapPin,
  Calendar,
  User,
  ClipboardList,
  Filter,
  X,
  RotateCcw,
  Camera,
  Video,
} from 'lucide-react';"""
if old_import in src:
    src = src.replace(old_import, new_import)
    changes.append("added Camera + Video icons")

# 2. Add evidenceList prop to interface
old_iface = """interface FieldVisitListProps {
  visits: SiteVisit[];
  projects: Project[];
  onOpenLogModal: () => void;
}"""
new_iface = """interface FieldVisitListProps {
  visits: SiteVisit[];
  projects: Project[];
  onOpenLogModal: () => void;
  evidenceList?: any[];
}"""
if old_iface in src:
    src = src.replace(old_iface, new_iface)
    changes.append("added evidenceList prop to interface")

# 3. Destructure evidenceList
old_dest = """export const FieldVisitList: React.FC<FieldVisitListProps> = ({
  visits = [],
  projects = [],
  onOpenLogModal,
}) => {"""
new_dest = """export const FieldVisitList: React.FC<FieldVisitListProps> = ({
  visits = [],
  projects = [],
  onOpenLogModal,
  evidenceList = [],
}) => {"""
if old_dest in src:
    src = src.replace(old_dest, new_dest)
    changes.append("destructured evidenceList")

# 4. Add state for lightbox
old_state = """  const [filterDateFrom, setFilterDateFrom] = useState<string>('');
  const [filterDateTo, setFilterDateTo] = useState<string>('');"""
new_state = """  const [filterDateFrom, setFilterDateFrom] = useState<string>('');
  const [filterDateTo, setFilterDateTo] = useState<string>('');
  const [activeMedia, setActiveMedia] = useState<any | null>(null);"""
if old_state in src:
    src = src.replace(old_state, new_state)
    changes.append("added activeMedia state for lightbox")

# 5. Add a helper to get evidence for a visit — insert right before the return statement
# We'll find the "return (" that starts the component's JSX and insert before it
# Since we don't know exact line, use a marker
marker = "  return (\n    <div id=\"field-visit-list-module\""
helper = """  // Group evidence by visit_id
  const evidenceByVisit = (evidenceList || []).reduce((acc: any, e: any) => {
    if (!e?.visit_id) return acc;
    if (!acc[e.visit_id]) acc[e.visit_id] = [];
    acc[e.visit_id].push(e);
    return acc;
  }, {});

  return (
    <div id="field-visit-list-module\""""
if marker in src:
    src = src.replace(marker, helper, 1)
    changes.append("added evidenceByVisit helper")

# 6. Insert the evidence thumbnail strip inside each visit card
# Find the closing of each visit card — the pattern is the officer comment block + closing divs
# We'll insert just before the final </div> of the card's outer wrapper.
# The last content in the card is `{visit.officer_comments && (...)}` then closes.
old_tail = """            {visit.officer_comments && (
              <div className="text-[11px] text-slate-500 italic border-t border-slate-100 pt-2">
                Officer comment: "{visit.officer_comments}"
              </div>
            )}
          </div>
        ))}"""
new_tail = """            {visit.officer_comments && (
              <div className="text-[11px] text-slate-500 italic border-t border-slate-100 pt-2">
                Officer comment: "{visit.officer_comments}"
              </div>
            )}

            {/* Evidence thumbnail strip */}
            {evidenceByVisit[visit.id]?.length > 0 && (
              <div className="pt-2 border-t border-slate-100">
                <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mb-1.5 flex items-center gap-1">
                  <Camera className="w-3 h-3" /> Evidence ({evidenceByVisit[visit.id].length})
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {evidenceByVisit[visit.id].map((e: any) => (
                    <div
                      key={e.id}
                      onClick={() => setActiveMedia(e)}
                      className="relative w-16 h-16 rounded-md overflow-hidden border border-slate-200 bg-slate-100 cursor-pointer group"
                      title={e.description || e.file_name}
                    >
                      {e.media_type === 'photo' ? (
                        <img
                          src={e.file_url}
                          alt={e.file_name}
                          className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                        />
                      ) : e.media_type === 'video' ? (
                        <div className="w-full h-full flex items-center justify-center bg-slate-900">
                          <Video className="w-5 h-5 text-amber-400" />
                        </div>
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-slate-200">
                          <Camera className="w-5 h-5 text-slate-500" />
                        </div>
                      )}
                      {e.stage_tag && (
                        <span
                          className={`absolute bottom-0 inset-x-0 text-center text-[8px] font-bold uppercase tracking-wider py-0.5 ${
                            e.stage_tag === 'before'
                              ? 'bg-rose-600/90 text-white'
                              : e.stage_tag === 'during'
                              ? 'bg-amber-600/90 text-white'
                              : e.stage_tag === 'after'
                              ? 'bg-emerald-600/90 text-white'
                              : 'bg-slate-700/90 text-white'
                          }`}
                        >
                          {e.stage_tag}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}"""
if old_tail in src:
    src = src.replace(old_tail, new_tail)
    changes.append("inserted evidence thumbnail strip per visit card")
else:
    changes.append("card tail pattern NOT FOUND — need manual insertion")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)

opens = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")