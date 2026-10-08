import pathlib

p = pathlib.Path("src/components/interventions/InterventionPlanning.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add state for the detail modal
old_state = """  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [projectSourceIntervention, setProjectSourceIntervention] = useState<any | null>(null);"""
new_state = """  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [projectSourceIntervention, setProjectSourceIntervention] = useState<any | null>(null);
  const [selectedIntervention, setSelectedIntervention] = useState<any | null>(null);"""
if old_state in src and "selectedIntervention" not in src:
    src = src.replace(old_state, new_state)
    changes.append("added selectedIntervention state")

# 2. Make the card row clickable + add cursor-pointer + group
old_card = """            <div
              key={item.id}
              id={`intervention-row-${item.id}`}
              className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs hover:border-emerald-500 transition-colors space-y-3 text-xs"
            >"""
new_card = """            <div
              key={item.id}
              id={`intervention-row-${item.id}`}
              onClick={() => setSelectedIntervention(item)}
              className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs hover:border-emerald-500 hover:shadow-md transition-all space-y-3 text-xs cursor-pointer"
              title="Click to view full details"
            >"""
if old_card in src:
    src = src.replace(old_card, new_card)
    changes.append("made card clickable")

# 3. Stop propagation on the two action button groups so approve/reject don't trigger the modal
# Wrap the wrapper <div className="pt-2 border-t ..."> with onClick stopPropagation
old_wrap = """                <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center justify-end gap-2">
                  {canDirectorApprove && isDirectorPending && ("""
new_wrap = """                <div
                  className="pt-2 border-t border-slate-100 flex flex-wrap items-center justify-end gap-2"
                  onClick={(e) => e.stopPropagation()}
                >
                  {canDirectorApprove && isDirectorPending && ("""
if old_wrap in src:
    src = src.replace(old_wrap, new_wrap)
    changes.append("stop propagation on approval buttons wrapper")

# 4. Also stop propagation on the Create Project button block
old_cp = """                  {isFullyApproved && (
                    <button
                      onClick={() => {
                        setProjectSourceIntervention(item);
                        setIsProjectModalOpen(true);
                      }}
                      className="px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center gap-1.5"
                    >
                      <FolderGit2 className="w-3.5 h-3.5" />
                      Create Project
                    </button>
                  )}"""
new_cp = """                  {isFullyApproved && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setProjectSourceIntervention(item);
                        setIsProjectModalOpen(true);
                      }}
                      className="px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center gap-1.5"
                    >
                      <FolderGit2 className="w-3.5 h-3.5" />
                      Create Project
                    </button>
                  )}"""
if old_cp in src:
    src = src.replace(old_cp, new_cp)
    changes.append("stop propagation on Create Project button")

# 5. Render the detail modal at the bottom — after the ProjectModal block, before the closing </div>
old_footer = """      {/* Step 2: intervention form, prefilled with the picked hazard */}
      <InterventionModal"""
new_footer = """      {/* Intervention detail modal */}
      {selectedIntervention && (
        <InterventionDetailModal
          intervention={selectedIntervention}
          hazard={hazards.find((h: any) => h.id === selectedIntervention.hazard_id) || null}
          project={projects.find((p: any) => p.id === selectedIntervention.project_id) || null}
          currentUser={currentUser}
          onClose={() => setSelectedIntervention(null)}
          onDirectorApprove={async (id) => {
            setSelectedIntervention(null);
            await handleDirectorApprove(id);
          }}
          onExecutiveApprove={async (id) => {
            setSelectedIntervention(null);
            await handleExecutiveApprove(id);
          }}
          onReject={async (id) => {
            setSelectedIntervention(null);
            await handleReject(id);
          }}
          onCreateProject={(iv) => {
            setSelectedIntervention(null);
            setProjectSourceIntervention(iv);
            setIsProjectModalOpen(true);
          }}
          canDirectorApprove={canDirectorApprove}
          canExecutiveApprove={canExecutiveApprove}
        />
      )}

      {/* Step 2: intervention form, prefilled with the picked hazard */}
      <InterventionModal"""
if old_footer in src:
    src = src.replace(old_footer, new_footer, 1)
    changes.append("rendered InterventionDetailModal")

# 6. Append the InterventionDetailModal component at the bottom of the file
component_code = '''

// ==================================================================
// Intervention Detail Modal — full preview before approval
// ==================================================================
const InterventionDetailModal: React.FC<{
  intervention: any;
  hazard: any | null;
  project: any | null;
  currentUser: any;
  canDirectorApprove: boolean;
  canExecutiveApprove: boolean;
  onClose: () => void;
  onDirectorApprove: (id: string) => Promise<void>;
  onExecutiveApprove: (id: string) => Promise<void>;
  onReject: (id: string) => Promise<void>;
  onCreateProject: (iv: any) => void;
}> = ({
  intervention,
  hazard,
  project,
  currentUser,
  canDirectorApprove,
  canExecutiveApprove,
  onClose,
  onDirectorApprove,
  onExecutiveApprove,
  onReject,
  onCreateProject,
}) => {
  const [hazardEvidence, setHazardEvidence] = React.useState<any[]>([]);
  const [projectEvidence, setProjectEvidence] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [activeMedia, setActiveMedia] = React.useState<any | null>(null);
  const [busy, setBusy] = React.useState(false);

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const all = await api.getEvidence();
        if (cancelled) return;
        if (hazard?.id) {
          setHazardEvidence(
            (all || []).filter((e: any) => e.hazard_id === hazard.id && e.media_type === 'photo')
          );
        }
        if (project?.id) {
          setProjectEvidence(
            (all || []).filter((e: any) => e.project_id === project.id && e.media_type === 'photo')
          );
        }
      } catch (err) {
        console.warn('Failed to load evidence:', err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [hazard?.id, project?.id]);

  const status = intervention.approval_status;
  const isDirectorPending = status === 'Proposed' || status === 'Rejected' || !status;
  const isExecutivePending = status === 'Director Approved';
  const isFullyApproved = status === 'Executive Approved';

  const wrap = async (fn: (id: string) => Promise<void>) => {
    setBusy(true);
    try {
      await fn(intervention.id);
    } finally {
      setBusy(false);
    }
  };

  const allEvidence = [...hazardEvidence, ...projectEvidence];

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200 text-xs"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 bg-emerald-950 text-white flex items-start justify-between border-b border-emerald-900">
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="px-2 py-0.5 rounded font-mono font-bold bg-emerald-800 text-amber-300 text-[11px]">
                {intervention.id}
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  intervention.priority === 'CRITICAL'
                    ? 'bg-rose-100 text-rose-800'
                    : 'bg-amber-100 text-amber-800'
                }`}
              >
                {intervention.priority} PRIORITY
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  isFullyApproved
                    ? 'bg-emerald-100 text-emerald-800'
                    : isExecutivePending
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-amber-100 text-amber-800'
                }`}
              >
                {isFullyApproved
                  ? '✓ Fully Approved'
                  : isExecutivePending
                  ? 'Awaiting Executive Approval'
                  : 'Awaiting Director Approval'}
              </span>
            </div>
            <h2 className="text-base font-bold text-white">{intervention.title}</h2>
            {hazard && (
              <p className="text-[11px] text-emerald-300 mt-1">
                Linked hazard: <span className="font-semibold">{hazard.title}</span> ({hazard.community}, {hazard.state})
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200"
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {/* Engineering scope */}
          <Section title="Engineering Scope">
            <div className="space-y-2">
              <div className="text-slate-700">{intervention.estimated_scope || intervention.technical_description || '—'}</div>
              {intervention.technical_description && intervention.technical_description !== intervention.estimated_scope && (
                <div className="mt-2 pt-2 border-t border-slate-100">
                  <div className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-1">Technical Findings</div>
                  <div className="text-slate-600">{intervention.technical_description}</div>
                </div>
              )}
            </div>
          </Section>

          {/* Financials */}
          <Section title="Financials">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Field label="Estimated Cost">
                <span className="font-mono font-bold text-slate-900">
                  ₦{Number(intervention.estimated_cost_ngn || 0).toLocaleString()}
                </span>
              </Field>
              <Field label="Proposed Funding">
                {intervention.proposed_funding || '—'}
              </Field>
              {intervention.executive_approval?.approved_amount_ngn && (
                <Field label="Executive Approved Amount">
                  <span className="font-mono font-bold text-emerald-700">
                    ₦{Number(intervention.executive_approval.approved_amount_ngn).toLocaleString()}
                  </span>
                </Field>
              )}
            </div>
          </Section>

          {/* Responsibility */}
          <Section title="Responsibility">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Field label="Department">{intervention.responsible_department || '—'}</Field>
              <Field label="Officer">{intervention.responsible_officer || '—'}</Field>
            </div>
          </Section>

          {/* Timeline */}
          <Section title="Timeline">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Field label="Target Start">{intervention.proposed_start_date || '—'}</Field>
              <Field label="Target Completion">{intervention.proposed_completion_date || '—'}</Field>
            </div>
          </Section>

          {/* Expected Outcome */}
          {intervention.expected_outcome && (
            <Section title="Expected Outcome">
              {intervention.expected_outcome}
            </Section>
          )}

          {/* Approval History */}
          <Section title="Approval History">
            <div className="space-y-2">
              <ApprovalStep
                done={true}
                label="Proposed"
                date={intervention.created_at}
                by={intervention.responsible_officer}
              />
              <ApprovalStep
                done={!!intervention.director_approval}
                label="Director Approval"
                date={intervention.director_approval?.approved_at}
                by={intervention.director_approval?.approved_by}
                notes={intervention.director_approval?.notes}
              />
              <ApprovalStep
                done={!!intervention.executive_approval}
                label="Executive Approval"
                date={intervention.executive_approval?.approved_at}
                by={intervention.executive_approval?.approved_by}
                notes={intervention.executive_approval?.notes}
              />
              {intervention.rejection_reason && (
                <div className="rounded-lg bg-rose-50 border border-rose-200 px-3 py-2 mt-2">
                  <div className="text-[10px] uppercase tracking-wider text-rose-700 font-bold mb-0.5">
                    ✕ Rejected
                  </div>
                  <div className="text-rose-900">{intervention.rejection_reason}</div>
                  <div className="text-[10px] text-rose-600 mt-1">
                    by {intervention.rejected_by} · {intervention.rejected_at}
                  </div>
                </div>
              )}
            </div>
          </Section>

          {/* Evidence */}
          <Section title={`Evidence Attachments (${allEvidence.length})`}>
            {loading ? (
              <div className="text-slate-400 text-[11px]">Loading evidence…</div>
            ) : allEvidence.length === 0 ? (
              <div className="text-slate-400 text-[11px] italic">No evidence attached to the linked hazard or project.</div>
            ) : (
              <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                {allEvidence.map((e: any) => (
                  <div
                    key={e.id}
                    onClick={() => setActiveMedia(e)}
                    className="relative rounded-lg overflow-hidden border border-slate-200 bg-slate-100 cursor-pointer group"
                    title={e.description || e.file_name}
                  >
                    <img src={e.file_url} alt={e.file_name} className="w-full h-20 object-cover group-hover:scale-105 transition-transform" />
                    {e.stage_tag && (
                      <span className={`absolute top-1 left-1 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider border ${
                        e.stage_tag === 'before' ? 'bg-rose-900/80 text-white border-rose-700' :
                        e.stage_tag === 'during' ? 'bg-amber-900/80 text-white border-amber-700' :
                        e.stage_tag === 'after' ? 'bg-emerald-900/80 text-white border-emerald-700' :
                        'bg-slate-800/80 text-white border-slate-600'
                      }`}>
                        {e.stage_tag}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </Section>

          {/* Linked Project */}
          {project && (
            <Section title="Linked Project">
              <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-3 space-y-2">
                <div className="font-semibold text-emerald-900">
                  {project.id} — {project.title}
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div>
                    <span className="text-emerald-600">Status:</span>{' '}
                    <span className="text-emerald-900 font-semibold">{project.status}</span>
                  </div>
                  <div>
                    <span className="text-emerald-600">Contractor:</span>{' '}
                    <span className="text-emerald-900">{project.contractor || '—'}</span>
                  </div>
                  <div>
                    <span className="text-emerald-600">Approved:</span>{' '}
                    <span className="font-mono text-emerald-900">
                      ₦{Number(project.approved_amount_ngn || 0).toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-emerald-600">Progress:</span>{' '}
                    <span className="text-emerald-900 font-semibold">{project.actual_percentage || 0}%</span>
                  </div>
                </div>
              </div>
            </Section>
          )}
        </div>

        {/* Footer actions */}
        <div className="px-6 py-4 border-t border-slate-200 bg-slate-50 flex flex-wrap items-center justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-200 hover:bg-slate-300 text-slate-800"
          >
            Close
          </button>
          {canDirectorApprove && isDirectorPending && (
            <>
              <button
                onClick={() => wrap(onReject)}
                disabled={busy}
                className="px-3 py-2 rounded-lg text-xs font-bold bg-rose-700 hover:bg-rose-800 text-white disabled:opacity-50"
              >
                Reject
              </button>
              <button
                onClick={() => wrap(onDirectorApprove)}
                disabled={busy}
                className="px-3 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white disabled:opacity-50"
              >
                Director Approve
              </button>
            </>
          )}
          {canExecutiveApprove && isExecutivePending && (
            <>
              <button
                onClick={() => wrap(onReject)}
                disabled={busy}
                className="px-3 py-2 rounded-lg text-xs font-bold bg-rose-700 hover:bg-rose-800 text-white disabled:opacity-50"
              >
                Reject
              </button>
              <button
                onClick={() => wrap(onExecutiveApprove)}
                disabled={busy}
                className="px-3 py-2 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white disabled:opacity-50"
              >
                Executive Approve
              </button>
            </>
          )}
          {isFullyApproved && !project && (
            <button
              onClick={() => onCreateProject(intervention)}
              className="px-3 py-2 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center gap-1.5"
            >
              Create Project
            </button>
          )}
        </div>
      </div>

      {/* Lightbox */}
      {activeMedia && (
        <div
          onClick={(e) => { e.stopPropagation(); setActiveMedia(null); }}
          className="fixed inset-0 z-[60] bg-black/90 flex items-center justify-center p-4"
        >
          <img src={activeMedia.file_url} alt={activeMedia.file_name} className="max-w-full max-h-[85vh] rounded-lg object-contain" />
        </div>
      )}
    </div>
  );
};

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div>
    <h4 className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-2 pb-1 border-b border-slate-100">
      {title}
    </h4>
    <div className="text-slate-700 text-xs">{children}</div>
  </div>
);

const Field: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div>
    <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">{label}</div>
    <div className="text-slate-800">{children}</div>
  </div>
);

const ApprovalStep: React.FC<{
  done: boolean;
  label: string;
  date?: string;
  by?: string;
  notes?: string;
}> = ({ done, label, date, by, notes }) => (
  <div className="flex items-start gap-3">
    <div
      className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5 ${
        done ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-500'
      }`}
    >
      {done ? '✓' : '·'}
    </div>
    <div className="flex-1">
      <div className={`text-xs ${done ? 'font-semibold text-slate-900' : 'text-slate-500'}`}>{label}</div>
      {done && (date || by) && (
        <div className="text-[10px] text-slate-500 mt-0.5">
          {by && <>by {by}</>}
          {by && date && ' · '}
          {date && <span className="font-mono">{date}</span>}
        </div>
      )}
      {done && notes && (
        <div className="text-[11px] text-slate-600 mt-1 italic">"{notes}"</div>
      )}
    </div>
  </div>
);
'''

if "InterventionDetailModal" not in src:
    src = src.rstrip() + component_code
    changes.append("appended InterventionDetailModal component")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)

# Brace balance sanity check
opens = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")