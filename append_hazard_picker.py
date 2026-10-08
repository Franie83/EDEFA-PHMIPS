import pathlib

picker_code = '''
// ==================================================================
// Hazard Picker — appears before the intervention form
// Only shows hazards that are verified + assessed + no existing intervention
// ==================================================================
const HazardPickerModal: React.FC<{
  hazards: Hazard[];
  interventions: Intervention[];
  onClose: () => void;
  onPick: (h: Hazard) => void;
}> = ({ hazards = [], interventions = [], onClose, onPick }) => {
  const [q, setQ] = React.useState('');

  const hasIntervention = (hid: string) =>
    (interventions || []).some((i: any) => i.hazard_id === hid);

  const eligible = (hazards || []).filter((h: any) => {
    if (!h.verified_by) return false;
    if (!h.assessment) return false;
    if (h.recommended_intervention) return false;
    if (h.status === 'Rejected/Invalid') return false;
    if (hasIntervention(h.id)) return false;
    return true;
  });

  const filtered = eligible.filter((h: any) => {
    if (!q) return true;
    const lower = q.toLowerCase();
    return (
      String(h.id || '').toLowerCase().includes(lower) ||
      String(h.title || '').toLowerCase().includes(lower) ||
      String(h.community || '').toLowerCase().includes(lower) ||
      String(h.lga || '').toLowerCase().includes(lower)
    );
  });

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[88vh] flex flex-col overflow-hidden border border-slate-200"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-4 bg-emerald-950 text-white flex items-center justify-between border-b border-emerald-900">
          <div className="flex items-center space-x-3">
            <Compass className="w-6 h-6 text-amber-300" />
            <div>
              <h2 className="text-base font-bold">Select a Hazard for Intervention</h2>
              <p className="text-[11px] text-emerald-300">
                Only verified and assessed hazards with no existing intervention are listed.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 border-b border-slate-100">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search by ID, title, community, LGA…"
              className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 text-xs"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {filtered.length === 0 ? (
            <div className="text-center py-10">
              <AlertCircle className="w-10 h-10 mx-auto text-slate-300 mb-2" />
              <p className="text-sm text-slate-600 font-medium">
                {eligible.length === 0
                  ? 'No hazards are ready for intervention planning.'
                  : 'No hazards match your search.'}
              </p>
              {eligible.length === 0 && (
                <p className="text-xs text-slate-500 mt-2 max-w-md mx-auto">
                  A hazard must be <strong>verified</strong> and <strong>assessed</strong> before
                  an intervention can be planned. It must also not already have an intervention.
                </p>
              )}
            </div>
          ) : (
            filtered.map((h: any) => (
              <button
                key={h.id}
                onClick={() => onPick(h)}
                className="w-full text-left bg-white border border-slate-200 rounded-xl p-4 hover:border-emerald-500 hover:shadow-md transition-all text-xs"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                      {h.id}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        h.severity === 'CRITICAL'
                          ? 'bg-rose-100 text-rose-800'
                          : h.severity === 'HIGH'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {h.severity}
                    </span>
                    {h.assessment?.calculated_priority_score && (
                      <span className="text-[10px] text-emerald-700 font-bold">
                        Score: {h.assessment.calculated_priority_score}/100
                      </span>
                    )}
                  </div>
                  <span className="text-emerald-700 font-semibold text-[11px]">
                    Plan intervention →
                  </span>
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-0.5">{h.title}</h3>
                <p className="text-[11px] text-slate-500">
                  {h.community}, {h.lga} — {h.state}
                </p>
              </button>
            ))
          )}
        </div>

        <div className="px-6 py-3 border-t border-slate-100 bg-slate-50 flex items-center justify-between text-[11px] text-slate-500">
          <span>
            {filtered.length} eligible hazard{filtered.length === 1 ? '' : 's'}
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-800 font-semibold"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};
'''

p = pathlib.Path("src/components/interventions/InterventionPlanning.tsx")
src = p.read_text(encoding="utf-8")

if "const HazardPickerModal: React.FC" in src:
    print("HazardPickerModal is already defined — no change needed.")
else:
    # Make sure imports exist
    needed_icons = ["Search", "X", "AlertCircle"]
    missing = [i for i in needed_icons if i not in src]
    if missing:
        print(f"WARNING: these icons are missing from imports: {missing}")
        print("Open the file and check the lucide-react import block.")
    # Append the component
    src = src.rstrip() + "\n" + picker_code
    p.write_text(src, encoding="utf-8")
    print(f"Appended HazardPickerModal to {p}")
    print(f"File now {len(src)} chars")