import React, { useState, useEffect } from 'react';
import { Hazard, Evidence, ActionItem, Intervention } from '../../types/index.ts';
import { canEdit as canEditFn, canDelete as canDeleteFn } from '../../types/tiers.ts';
import {
  X,
  MapPin,
  Calendar,
  User,
  ShieldAlert,
  Clock,
  Compass,
  CheckCircle2,
  FileText,
  Camera,
  Video,
  Play,
  Share2,
  Printer,
  ChevronRight,
  ExternalLink,
  Layers,
  Pencil,
  Trash2
} from 'lucide-react';
import { DirectionsLink } from '../common/DirectionsLink.tsx';
import { api } from '../../services/api.ts';

interface HazardDetailModalProps {
  hazard: Hazard | null;
  onClose: () => void;
  onVerifyClick: (hazard: Hazard) => void;
  onAssessClick: (hazard: Hazard) => void;
  onInterventionClick: (hazard: Hazard) => void;
  onNavigateToMap: (lat: number, lng: number) => void;
  onEdit?: (hazard: Hazard) => void;
  onPlanIntervention?: (hazard: Hazard) => void;
  onDelete?: (hazard: Hazard) => void;
  currentRole?: string;
}

export const HazardDetailModal: React.FC<HazardDetailModalProps> = ({
  hazard,
  onClose,
  onVerifyClick,
  onAssessClick,
  onInterventionClick,
  onNavigateToMap,
  onEdit,
  onDelete,
  onPlanIntervention,
  currentRole
}) => {
  const [activeMedia, setActiveMedia] = useState<{ images: Evidence[]; index: number } | null>(null);
  const [fullHazard, setFullHazard] = useState<Hazard | null>(null);

  // Fetch the full hazard (with evidence_files, actions, intervention) when modal opens
  useEffect(() => {
    if (!hazard?.id) {
      setFullHazard(null);
      return;
    }
    let cancelled = false;
    api.getHazardById(hazard.id)
      .then(full => { if (!cancelled) setFullHazard(full); })
      .catch(() => { if (!cancelled) setFullHazard(hazard); });
    return () => { cancelled = true; };
  }, [hazard?.id]);

  if (!hazard) return null;

  // Prefer the fully-hydrated hazard (with evidence), fall back to the list item
  const h = fullHazard && fullHazard.id === hazard.id ? fullHazard : hazard;

  const userCanEdit = canEditFn(currentRole);
  const userCanDelete = canDeleteFn(currentRole);

  const handleDeleteClick = () => {
    if (!onDelete) return;
    const confirmed = window.confirm(
      `Delete hazard ${h.id}?\n\n"${h.title}"\n\nThis cannot be undone. The deletion will be permanently recorded in the audit log.`
    );
    if (confirmed) onDelete(hazard);
  };

  return (
    <div id="hazard-detail-modal" className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200 text-xs">
        {/* Header */}
        <div className="px-6 py-4 bg-emerald-950 text-white flex items-center justify-between border-b border-emerald-900">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-0.5 rounded font-mono font-bold bg-emerald-800 text-amber-300 text-[11px]">
                {h.id}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500 text-emerald-950 uppercase">
                {h.category}
              </span>
              <span className="text-emerald-300 text-xs">Reported: {h.date_reported}</span>
            </div>
            <h2 className="text-base font-bold text-white mt-1 max-w-2xl">{h.title}</h2>
          </div>
          <div className="flex items-center space-x-1.5">
            {userCanEdit && onEdit && (
              <button
                onClick={() => onEdit(hazard)}
                title="Edit this hazard (Super Admin / Executive only)"
                className="p-1.5 rounded-lg bg-emerald-800/60 hover:bg-emerald-700 text-emerald-100 transition-colors inline-flex items-center space-x-1"
              >
                <Pencil className="w-4 h-4" />
                <span className="hidden sm:inline text-[11px] font-semibold">Edit</span>
              </button>
            )}
            {userCanDelete && onDelete && (
              <button
                onClick={handleDeleteClick}
                title="Delete this hazard (Super Admin / Executive only)"
                className="p-1.5 rounded-lg bg-rose-900/60 hover:bg-rose-800 text-rose-100 transition-colors inline-flex items-center space-x-1"
              >
                <Trash2 className="w-4 h-4" />
                <span className="hidden sm:inline text-[11px] font-semibold">Delete</span>
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1 rounded-md text-emerald-300 hover:text-white hover:bg-emerald-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-slate-700">
          {/* Status Progression Bar */}
          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2">
              Hazard Lifecycle Stage
            </div>
            <div className="flex items-center justify-between relative">
              {[
                'Reported',
                'Verified',
                'Assessed',
                'Prioritised',
                'Intervention Planned',
                'Ongoing',
                'Resolved'
              ].map((stage, idx) => {
                const isPassed =
                  (stage === 'Reported' && h.status !== 'Draft') ||
                  (stage === 'Verified' && h.verified_by) ||
                  (stage === 'Assessed' && h.assessment) ||
                  (stage === 'Prioritised' && h.status.includes('Prioritised')) ||
                  (stage === 'Intervention Planned' && h.recommended_intervention) ||
                  (stage === 'Ongoing' && h.status.includes('Ongoing')) ||
                  (stage === 'Resolved' && h.status === 'Resolved');

                const isCurrent = h.status.toLowerCase().includes(stage.toLowerCase());

                return (
                  <div key={stage} className="flex flex-col items-center flex-1 text-center">
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold z-10 transition-colors ${
                        isCurrent
                          ? 'bg-amber-500 text-emerald-950 ring-4 ring-amber-100'
                          : isPassed
                          ? 'bg-emerald-700 text-white'
                          : 'bg-slate-200 text-slate-500'
                      }`}
                    >
                      {idx + 1}
                    </div>
                    <span
                      className={`text-[10px] mt-1 font-medium leading-tight ${
                        isCurrent ? 'text-amber-800 font-bold' : isPassed ? 'text-emerald-900' : 'text-slate-400'
                      }`}
                    >
                      {stage}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quick Metrics & Geographic Location */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
              <div className="text-[11px] font-bold uppercase text-slate-500 flex items-center">
                <MapPin className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                Geographic Placement
              </div>
              <div className="space-y-1">
                <div><span className="text-slate-500">State:</span> <strong className="text-slate-900">{h.state}</strong></div>
                <div><span className="text-slate-500">LGA:</span> <strong className="text-slate-900">{h.lga}</strong></div>
                <div><span className="text-slate-500">Community:</span> <strong className="text-slate-900">{h.community}</strong></div>
                {h.ward && <div><span className="text-slate-500">Ward:</span> <span className="text-slate-700">{h.ward}</span></div>}
                <div className="pt-1 text-[11px] text-slate-500 font-mono">
                  Coordinates: {h.latitude.toFixed(6)}, {h.longitude.toFixed(6)}
                </div>
              </div>
              <button
                onClick={() => {
                  onClose();
                  onNavigateToMap(h.latitude, h.longitude);
                }}
                className="w-full mt-2 py-1.5 rounded text-xs font-semibold bg-emerald-100 hover:bg-emerald-200 text-emerald-800 inline-flex items-center justify-center transition-colors"
              >
                <ExternalLink className="w-3.5 h-3.5 mr-1" />
                Locate on GIS Map
              </button>
              <div className="mt-2 flex justify-center">
                <DirectionsLink
                  lat={h.latitude}
                  lng={h.longitude}
                  label="Get Directions"
                />
              </div>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
              <div className="text-[11px] font-bold uppercase text-slate-500 flex items-center">
                <ShieldAlert className="w-3.5 h-3.5 mr-1 text-rose-600" />
                Severity & Risk Metrics
              </div>
              <div className="space-y-1">
                <div>
                  <span className="text-slate-500">Severity:</span>{' '}
                  <span className="font-bold text-rose-700">{h.severity}</span>
                </div>
                <div>
                  <span className="text-slate-500">Urgency:</span>{' '}
                  <span className="font-medium text-slate-900">{h.urgency}</span>
                </div>
                <div>
                  <span className="text-slate-500">Affected Area:</span>{' '}
                  <span className="font-medium text-slate-900">{h.estimated_affected_area_sqm.toLocaleString()} m²</span>
                </div>
                <div>
                  <span className="text-slate-500">Exposed Population:</span>{' '}
                  <span className="font-medium text-slate-900">{h.estimated_affected_population.toLocaleString()} citizens</span>
                </div>
                {h.is_recurring && (
                  <div className="text-amber-800 font-semibold text-[11px] bg-amber-50 p-1 rounded border border-amber-200">
                    Recurring Hotspot ({h.recurring_count} occurrences)
                  </div>
                )}
              </div>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
              <div className="text-[11px] font-bold uppercase text-slate-500 flex items-center">
                <User className="w-3.5 h-3.5 mr-1 text-blue-600" />
                Reporting & Verification
              </div>
              <div className="space-y-1">
                <div><span className="text-slate-500">Reporter:</span> <strong className="text-slate-900">{h.reporter_name}</strong></div>
                <div><span className="text-slate-500">Category:</span> <span className="text-slate-700">{h.reporter_type}</span></div>
                <div><span className="text-slate-500">Contact:</span> <span className="font-mono text-slate-700">{h.reporter_contact}</span></div>
                <div className="pt-1 border-t border-slate-200">
                  <span className="text-slate-500">Verified By:</span>{' '}
                  {h.verified_by ? (
                    <span className="text-emerald-700 font-semibold">{h.verified_by} ({h.verified_at?.split('T')[0]})</span>
                  ) : (
                    <span className="text-amber-700 font-medium">Pending Verification</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Description & Impact */}
          <div className="space-y-3">
            <div>
              <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider mb-1">
                Ecological Hazard Description
              </h4>
              <p className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 leading-relaxed">
                {h.description}
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-bold text-slate-500 uppercase block mb-1">Exposed Assets & Infrastructure</span>
                <p className="text-slate-800">{h.estimated_affected_assets}</p>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-bold text-slate-500 uppercase block mb-1">Potential Escalation Consequences</span>
                <p className="text-slate-800">{h.potential_impact}</p>
              </div>
            </div>
          </div>

          {/* Technical Assessment Scoring Details (if assessed) */}
          {h.assessment && (
            <div className="p-4 rounded-lg bg-emerald-50/60 border border-emerald-200 space-y-3">
              <div className="flex items-center justify-between border-b border-emerald-200 pb-2">
                <div className="flex items-center space-x-2">
                  <Compass className="w-4 h-4 text-emerald-800" />
                  <h4 className="font-bold text-emerald-950 uppercase text-xs">
                    Engineering Assessment & Priority Matrix
                  </h4>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-emerald-900">
                    Calculated Score: {h.assessment.calculated_priority_score} / 100
                  </span>
                  <span className="ml-2 px-2 py-0.5 rounded bg-emerald-800 text-white font-bold text-[10px]">
                    {h.assessment.recommended_priority}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center">
                <div className="p-2 rounded bg-white border border-emerald-100">
                  <span className="text-[10px] text-slate-500 block">Severity (25%)</span>
                  <strong className="text-base text-slate-900">{h.assessment.severity_score}/10</strong>
                </div>
                <div className="p-2 rounded bg-white border border-emerald-100">
                  <span className="text-[10px] text-slate-500 block">Urgency (20%)</span>
                  <strong className="text-base text-slate-900">{h.assessment.urgency_score}/10</strong>
                </div>
                <div className="p-2 rounded bg-white border border-emerald-100">
                  <span className="text-[10px] text-slate-500 block">Exposure (20%)</span>
                  <strong className="text-base text-slate-900">{h.assessment.exposure_score}/10</strong>
                </div>
                <div className="p-2 rounded bg-white border border-emerald-100">
                  <span className="text-[10px] text-slate-500 block">Impact (20%)</span>
                  <strong className="text-base text-slate-900">{h.assessment.impact_score}/10</strong>
                </div>
                <div className="p-2 rounded bg-white border border-emerald-100">
                  <span className="text-[10px] text-slate-500 block">Escalation (15%)</span>
                  <strong className="text-base text-slate-900">{h.assessment.escalation_risk_score}/10</strong>
                </div>
              </div>

              <div className="text-slate-700 space-y-1 pt-1 text-[11px]">
                <p><strong>Technical Findings:</strong> {h.assessment.technical_findings}</p>
                <p><strong>Assessed by:</strong> {h.assessment.assessed_by} on {h.assessment.assessed_at}</p>
              </div>
            </div>
          )}

          {/* Recommended Intervention (if proposed) */}
          {h.recommended_intervention && (
            <div className="p-4 rounded-lg bg-blue-50/70 border border-blue-200 space-y-2">
              <div className="flex items-center justify-between border-b border-blue-200 pb-2">
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4 text-blue-800" />
                  <h4 className="font-bold text-blue-950 uppercase text-xs">
                    Recommended Engineering Intervention
                  </h4>
                </div>
                <div className="text-sm font-bold text-blue-950">
                  ₦{h.recommended_intervention.estimated_cost_ngn.toLocaleString()}
                </div>
              </div>
              <div>
                <strong className="text-slate-900 block">{h.recommended_intervention.title}</strong>
                <p className="text-slate-700 mt-1">{h.recommended_intervention.scope_description}</p>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2 text-[11px] text-slate-600">
                <div><strong>Proposed Funding:</strong> {h.recommended_intervention.proposed_funding}</div>
                <div><strong>Department:</strong> {h.recommended_intervention.responsible_department}</div>
                <div><strong>Expected Outcome:</strong> {h.recommended_intervention.expected_outcome}</div>
              </div>
            </div>
          )}

          {/* Evidence Attachments (Photos & Videos) */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
                Photographic & Video Evidence ({h.evidence_files?.length || 0})
              </h4>
            </div>

            {(!h.evidence_files || h.evidence_files.length === 0) ? (
              <div className="p-4 text-center rounded-lg bg-slate-50 border border-slate-200 text-slate-400">
                No multimedia evidence uploaded for this hazard report yet.
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {h.evidence_files.map((ev, __idx) => (
                  <div
                    key={ev.id}
                    onClick={() => setActiveMedia({ images: h.evidence_files || [], index: __idx })}
                    className="cursor-pointer group relative rounded-lg border border-slate-200 overflow-hidden bg-slate-100 shadow-xs hover:shadow-md transition-shadow"
                  >
                    {ev.media_type === 'photo' ? (
                      <img src={ev.file_url} alt={ev.file_name} className="h-28 w-full object-cover group-hover:scale-105 transition-transform" />
                    ) : (
                      <div className="h-28 w-full bg-slate-900 flex flex-col items-center justify-center text-white">
                        <Play className="w-8 h-8 text-amber-400 fill-amber-400" />
                        <span className="text-[10px] mt-1 text-slate-300">Video Evidence</span>
                      </div>
                    )}
                    <div className="p-2 text-[11px] bg-white">
                      <div className="font-semibold text-slate-900 truncate">{ev.file_name}</div>
                      <div className="text-slate-400 text-[10px]">{ev.upload_date}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          <button
            onClick={() => window.print()}
            className="px-3 py-1.5 rounded text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 inline-flex items-center"
          >
            <Printer className="w-3.5 h-3.5 mr-1.5" />
            Print Dossier
          </button>

          <div className="flex items-center space-x-2">
            {!h.verified_by && (
              <button
                onClick={() => {
                  onClose();
                  onVerifyClick(h);
                }}
                className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-emerald-700 text-white hover:bg-emerald-800"
              >
                Perform Technical Verification
              </button>
            )}

            {!h.assessment && h.verified_by && (
              <button
                onClick={() => {
                  onClose();
                  onAssessClick(h);
                }}
                className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-amber-600 text-white hover:bg-amber-700"
              >
                Conduct Technical Assessment
              </button>
            )}

            {h.assessment && !h.recommended_intervention && (
              <button
                onClick={() => { if (onPlanIntervention) { onClose(); onPlanIntervention(h); } else { onClose(); onInterventionClick(h); } }}
                className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-blue-700 text-white hover:bg-blue-800"
              >
                Plan Engineering Intervention
              </button>
            )}

            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-200 hover:bg-slate-300 text-slate-800"
            >
              Close
            </button>
          </div>
        </div>
      </div>

      {/* Multi-image evidence lightbox with prev/next */}
      {activeMedia && (() => {
        const images = activeMedia.images || [];
        const idx = activeMedia.index || 0;
        const current = images[idx];
        if (!current) return null;
        const goPrev = () => setActiveMedia({ images, index: (idx - 1 + images.length) % images.length });
        const goNext = () => setActiveMedia({ images, index: (idx + 1) % images.length });
        return (
          <div
            className="fixed inset-0 z-[60] bg-black/85 flex items-center justify-center p-4"
            onClick={() => setActiveMedia(null)}
            onKeyDown={(e) => {
              if (e.key === 'Escape') setActiveMedia(null);
              else if (e.key === 'ArrowLeft') goPrev();
              else if (e.key === 'ArrowRight') goNext();
            }}
            tabIndex={0}
            ref={(el) => el && el.focus()}
          >
            <div
              onClick={e => e.stopPropagation()}
              className="bg-slate-900 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden border border-slate-700"
            >
              <div className="flex items-center justify-between border-b border-slate-700 px-4 py-3">
                <div className="min-w-0 flex-1">
                  <h3 className="font-bold text-sm text-white truncate">{current.file_name}</h3>
                  {current.description && (
                    <p className="text-xs text-slate-400 truncate">{current.description}</p>
                  )}
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  {images.length > 1 && (
                    <span className="px-2.5 py-1 rounded-full bg-black/60 text-white text-[11px] font-semibold">
                      {idx + 1} of {images.length}
                    </span>
                  )}
                  <button
                    onClick={() => setActiveMedia(null)}
                    className="p-1 rounded bg-slate-800 text-slate-300 hover:text-white"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="relative flex-1 flex items-center justify-center bg-black/50 min-h-[300px]">
                {images.length > 1 && (
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); goPrev(); }}
                    className="absolute left-3 top-1/2 -translate-y-1/2 p-2.5 rounded-full bg-white/10 hover:bg-white/25 text-white z-10"
                    title="Previous (←)"
                  >
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M15 18l-6-6 6-6" /></svg>
                  </button>
                )}
                {current.media_type === 'photo' ? (
                  <img src={current.file_url} alt={current.file_name} className="max-h-[65vh] w-auto object-contain" />
                ) : (
                  <video key={current.id} controls autoPlay className="max-h-[65vh] w-full">
                    <source src={current.file_url} type="video/mp4" />
                    Your browser does not support HTML5 video.
                  </video>
                )}
                {images.length > 1 && (
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); goNext(); }}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-2.5 rounded-full bg-white/10 hover:bg-white/25 text-white z-10"
                    title="Next (→)"
                  >
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M9 18l6-6-6-6" /></svg>
                  </button>
                )}
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400 px-4 py-3 border-t border-slate-700">
                <span>Uploaded by {current.uploader_name} on {current.upload_date}</span>
                {current.gps_latitude != null && (
                  <span className="font-mono">
                    GPS: {current.gps_latitude.toFixed(5)}, {current.gps_longitude?.toFixed(5)}
                  </span>
                )}
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
};