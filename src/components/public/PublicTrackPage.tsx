import React, { useState, useEffect } from 'react';
import { ArrowLeft, Search, MapPin, Calendar, FileText, CheckCircle2, Clock, Camera, Video, DollarSign, Building, Users } from 'lucide-react';
import { api } from '../../services/api';
import { PublicUserBanner } from './PublicUserBanner.tsx';

interface Props {
  initialCode?: string;
  onBack?: () => void;
  currentUser?: any;
  onSignOut?: () => void;
}

const STATUS_STYLES: Record<string, string> = {
  'Submitted': 'bg-amber-950 border-amber-800 text-amber-200',
  'Under Review': 'bg-blue-950 border-blue-800 text-blue-200',
  'Verified': 'bg-emerald-950 border-emerald-800 text-emerald-200',
  'Assessed': 'bg-cyan-950 border-cyan-800 text-cyan-200',
  'Intervention Recommended': 'bg-purple-950 border-purple-800 text-purple-200',
  'Intervention Approved': 'bg-indigo-950 border-indigo-800 text-indigo-200',
  'Resolved': 'bg-emerald-950 border-emerald-800 text-emerald-200',
  'Closed': 'bg-slate-800 border-slate-700 text-slate-200',
  'Rejected/Invalid': 'bg-rose-950 border-rose-800 text-rose-200',
};

const STAGE_COLORS: Record<string, string> = {
  before: 'bg-rose-900/40 text-rose-200 border-rose-800/60',
  during: 'bg-amber-900/40 text-amber-200 border-amber-800/60',
  after: 'bg-emerald-900/40 text-emerald-200 border-emerald-800/60',
  evidence: 'bg-slate-700/40 text-slate-200 border-slate-600/60',
};

export const PublicTrackPage: React.FC<Props> = ({ initialCode, onBack, currentUser, onSignOut }) => {
  const [code, setCode] = useState(initialCode || '');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<any | null>(null);
  const [activeMedia, setActiveMedia] = useState<any | null>(null);

  const lookup = async (c?: string) => {
    const q = (c || code).trim();
    if (!q) return;
    setBusy(true);
    setError('');
    setResult(null);
    try {
      const r = await api.trackPublicReport(q);
      setResult(r);
    } catch (e: any) {
      setError(e.message || 'Tracking code not found');
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    if (initialCode) lookup(initialCode);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialCode]);

  const goBack = () => {
    if (onBack) return onBack();
    window.history.pushState({}, '', '/');
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const style = result ? (STATUS_STYLES[result.status] || 'bg-slate-800 border-slate-700 text-slate-200') : '';

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <PublicUserBanner currentUser={currentUser} onSignOut={onSignOut} />
      <div className="max-w-3xl mx-auto p-4 sm:p-6">
        <button onClick={goBack} className="flex items-center gap-2 text-slate-400 hover:text-white text-sm mb-4">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <div className="rounded-2xl bg-slate-900 border border-slate-700 p-6 sm:p-8 shadow-2xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-xl bg-blue-900/40 border border-blue-800 flex items-center justify-center">
              <Search className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Track Your Report</h1>
              <p className="text-xs text-slate-400">Edo State Ecological Fund Agency</p>
            </div>
          </div>

          <form onSubmit={e => { e.preventDefault(); lookup(); }} className="flex gap-2 mb-6">
            <input
              value={code} onChange={e => setCode(e.target.value)}
              placeholder="Enter tracking code (e.g. EF-HAZ-20260924-ORED)"
              className="flex-1 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-blue-600 font-mono text-sm"
            />
            <button type="submit" disabled={busy || !code}
              className="rounded-lg bg-blue-500 hover:bg-blue-400 disabled:opacity-50 text-white font-bold px-5">
              {busy ? '…' : 'Track'}
            </button>
          </form>

          {error && (
            <div className="rounded-lg bg-rose-950 border border-rose-800 text-rose-200 text-xs p-3 mb-4">
              {error}
            </div>
          )}

          {result && (
            <div className="space-y-5">
              {/* Current status banner */}
              <div className={`rounded-lg border p-4 ${style}`}>
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle2 className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase tracking-wider">Current Status</span>
                </div>
                <div className="text-lg font-bold">{result.status}</div>
              </div>

              {/* Title / location / reported */}
              <div className="rounded-lg bg-slate-800 border border-slate-700 p-4 space-y-3">
                <div>
                  <div className="text-[10px] uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1.5">
                    <FileText className="w-3 h-3" /> Title
                  </div>
                  <div className="font-semibold">{result.title}</div>
                  {result.description && (
                    <div className="text-xs text-slate-400 mt-1">{result.description}</div>
                  )}
                </div>
                <div className="grid sm:grid-cols-2 gap-3">
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1.5">
                      <MapPin className="w-3 h-3" /> Location
                    </div>
                    <div className="text-sm">
                      {result.lga}, {result.state}
                      {result.community ? ` — ${result.community}` : ''}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1.5">
                      <Calendar className="w-3 h-3" /> Reported
                    </div>
                    <div className="text-sm">{new Date(result.date_reported).toLocaleString()}</div>
                  </div>
                </div>
                <div className="pt-3 border-t border-slate-700">
                  <div className="text-[10px] uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1.5">
                    <Clock className="w-3 h-3" /> Tracking Code
                  </div>
                  <div className="font-mono text-sm text-amber-300 break-all">{result.tracking_code}</div>
                </div>
              </div>

              {/* Progress timeline */}
              {result.timeline && result.timeline.length > 0 && (
                <div className="rounded-lg bg-slate-800 border border-slate-700 p-4">
                  <div className="text-[10px] uppercase tracking-wider text-slate-400 mb-3 font-bold">
                    Progress Timeline
                  </div>
                  <div className="space-y-2">
                    {result.timeline.map((t: any, i: number) => (
                      <div key={i} className="flex items-center gap-3">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs shrink-0 ${
                          t.done ? 'bg-emerald-600 text-white' : 'bg-slate-700 text-slate-400'
                        }`}>
                          {t.done ? '✓' : i + 1}
                        </div>
                        <div className="flex-1 flex items-center justify-between">
                          <span className={`text-sm ${t.done ? 'text-white font-semibold' : 'text-slate-500'}`}>
                            {t.stage}
                          </span>
                          {t.date && t.done && (
                            <span className="text-[10px] text-slate-500 font-mono">
                              {new Date(t.date).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Evidence gallery */}
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

              {/* Intervention */}
              {result.intervention && (
                <div className="rounded-lg bg-purple-950/40 border border-purple-900 p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-purple-300" />
                    <span className="text-[10px] uppercase tracking-wider text-purple-300 font-bold">Planned Intervention</span>
                  </div>
                  <div className="font-semibold text-white">{result.intervention.title}</div>
                  {result.intervention.scope && (
                    <div className="text-xs text-purple-200">{result.intervention.scope}</div>
                  )}
                  <div className="grid sm:grid-cols-2 gap-2 text-xs pt-2 border-t border-purple-900/60">
                    <div>
                      <span className="text-purple-400">Estimated cost:</span>{' '}
                      <span className="font-mono text-purple-100">
                        ₦{Number(result.intervention.estimated_cost_ngn || 0).toLocaleString()}
                      </span>
                    </div>
                    {result.intervention.proposed_funding && (
                      <div>
                        <span className="text-purple-400">Funding:</span>{' '}
                        <span className="text-purple-100">{result.intervention.proposed_funding}</span>
                      </div>
                    )}
                    {result.intervention.responsible_department && (
                      <div>
                        <span className="text-purple-400">Department:</span>{' '}
                        <span className="text-purple-100">{result.intervention.responsible_department}</span>
                      </div>
                    )}
                    <div>
                      <span className="text-purple-400">Approval:</span>{' '}
                      <span className="text-purple-100">{result.intervention.approval_status}</span>
                    </div>
                    {result.intervention.proposed_start_date && (
                      <div>
                        <span className="text-purple-400">Target start:</span>{' '}
                        <span className="text-purple-100 font-mono">{result.intervention.proposed_start_date}</span>
                      </div>
                    )}
                    {result.intervention.proposed_completion_date && (
                      <div>
                        <span className="text-purple-400">Target completion:</span>{' '}
                        <span className="text-purple-100 font-mono">{result.intervention.proposed_completion_date}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Project */}
              {result.project && (
                <div className="rounded-lg bg-emerald-950/40 border border-emerald-900 p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <Building className="w-4 h-4 text-emerald-300" />
                    <span className="text-[10px] uppercase tracking-wider text-emerald-300 font-bold">Registered Project</span>
                  </div>
                  <div className="font-semibold text-white">{result.project.title}</div>
                  {result.project.description && (
                    <div className="text-xs text-emerald-100">{result.project.description}</div>
                  )}
                  <div className="grid sm:grid-cols-2 gap-2 text-xs pt-2 border-t border-emerald-900/60">
                    <div>
                      <span className="text-emerald-400">Status:</span>{' '}
                      <span className="text-emerald-100 font-semibold">{result.project.status}</span>
                    </div>
                    {result.project.contractor && (
                      <div>
                        <span className="text-emerald-400">Contractor:</span>{' '}
                        <span className="text-emerald-100">{result.project.contractor}</span>
                      </div>
                    )}
                    {result.project.implementing_agency && (
                      <div>
                        <span className="text-emerald-400">Implementing agency:</span>{' '}
                        <span className="text-emerald-100">{result.project.implementing_agency}</span>
                      </div>
                    )}
                    <div>
                      <span className="text-emerald-400">Approved budget:</span>{' '}
                      <span className="font-mono text-emerald-100">
                        ₦{Number(result.project.approved_amount_ngn || 0).toLocaleString()}
                      </span>
                    </div>
                    <div>
                      <span className="text-emerald-400">Contract value:</span>{' '}
                      <span className="font-mono text-emerald-100">
                        ₦{Number(result.project.contract_amount_ngn || 0).toLocaleString()}
                      </span>
                    </div>
                    {result.project.funding_source && (
                      <div>
                        <span className="text-emerald-400">Funding source:</span>{' '}
                        <span className="text-emerald-100">{result.project.funding_source}</span>
                      </div>
                    )}
                    {result.project.start_date && (
                      <div>
                        <span className="text-emerald-400">Start:</span>{' '}
                        <span className="text-emerald-100 font-mono">{result.project.start_date}</span>
                      </div>
                    )}
                    {result.project.expected_completion_date && (
                      <div>
                        <span className="text-emerald-400">Expected completion:</span>{' '}
                        <span className="text-emerald-100 font-mono">{result.project.expected_completion_date}</span>
                      </div>
                    )}
                  </div>
                  {/* Progress bar — only shown once the project is approved (Active / Delayed / Completed) */}
                  {['Active', 'Delayed', 'Completed'].includes(result.project.status) ? (
                    <div className="pt-2">
                      <div className="flex items-center justify-between text-[11px] mb-1">
                        <span className="text-emerald-400">Physical progress</span>
                        <span className="font-mono text-emerald-100 font-bold">
                          {result.project.actual_percentage || 0}%
                        </span>
                      </div>
                      <div className="h-2 bg-slate-800 rounded-full overflow-hidden border border-emerald-900/40">
                        <div
                          className="h-full bg-emerald-500 transition-all"
                          style={{ width: `${Math.min(100, result.project.actual_percentage || 0)}%` }}
                        />
                      </div>
                      <div className="text-[10px] text-emerald-400/70 mt-1">
                        Planned: {result.project.planned_percentage || 0}%
                      </div>
                    </div>
                  ) : (
                    <div className="pt-2 rounded bg-amber-950/30 border border-amber-900/40 px-3 py-2">
                      <div className="text-[10px] text-amber-300">
                        ⏳ Physical progress will be tracked once the project is approved and work begins.
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Lightbox */}
      {activeMedia && (
        <div
          onClick={() => setActiveMedia(null)}
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
        >
          <div onClick={(e) => e.stopPropagation()} className="max-w-3xl w-full">
            {activeMedia.media_type === 'photo' ? (
              <img src={activeMedia.file_url} alt={activeMedia.file_name} className="w-full max-h-[80vh] object-contain rounded-lg" />
            ) : (
              <video controls autoPlay className="w-full max-h-[80vh] rounded-lg">
                <source src={activeMedia.file_url} type="video/mp4" />
              </video>
            )}
            <div className="mt-3 text-center text-xs text-slate-400">
              {activeMedia.description || activeMedia.file_name}
              {activeMedia.stage_tag && ` · ${activeMedia.stage_tag.toUpperCase()}`}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
