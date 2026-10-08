import React, { useState } from 'react';
import { Intervention, Hazard, Project } from '../../types/index.ts';
import { api } from '../../services/api.ts';
import { InterventionModal } from './InterventionModal.tsx';
import { ProjectModal } from '../projects/ProjectModal.tsx';
import {
  Compass,
  DollarSign,
  Calendar,
  CheckCircle,
  Clock,
  Building,
  TrendingUp,
  Filter,
  Plus,
  Search,
  X,
  AlertCircle,
  FolderGit2,
  Pencil,
  Trash2
} from 'lucide-react';

interface InterventionPlanningProps {
  interventions: Intervention[];
  hazards: Hazard[];
  projects: Project[];
  onUpdateIntervention: (id: string, data: Partial<Intervention>) => Promise<void>;
  currentUser?: { role?: string; name?: string } | null;
  onRefresh?: () => Promise<void> | void;
  referenceData?: any;
  hideHeader?: boolean;
  onEditIntervention?: (iv: Intervention) => void;
  onDeleteIntervention?: (iv: Intervention) => Promise<void> | void;
}

export const InterventionPlanning: React.FC<InterventionPlanningProps> = ({
  interventions = [],
  hazards = [],
  projects = [],
  onUpdateIntervention,
  currentUser,
  onRefresh,
  referenceData,
  hideHeader = false,
  onEditIntervention,
  onDeleteIntervention
}) => {
  // --- Two-stage approval ---
  const [activeTab, setActiveTab] = useState<'all' | 'director' | 'executive' | 'approved'>('all');
  const [approvalBusy, setApprovalBusy] = useState<string | null>(null);
  const [isNewModalOpen, setIsNewModalOpen] = useState(false);
  const [isHazardPickerOpen, setIsHazardPickerOpen] = useState(false);
  const [pickerSelectedHazard, setPickerSelectedHazard] = useState<Hazard | null>(null);
  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [projectSourceIntervention, setProjectSourceIntervention] = useState<any | null>(null);
  const [selectedIntervention, setSelectedIntervention] = useState<any | null>(null);

  const role = currentUser?.role || '';
  const tier = (() => {
    if (role === 'SUPER_ADMIN') return 'TIER_1_ADMIN';
    if (role === 'EXECUTIVE' || role === 'AUDITOR') return 'TIER_2_EXEC';
    if (role === 'COORDINATOR' || role === 'INSPECTOR') return 'TIER_3_DIRECTOR';
    if (role === 'TECHNICAL_OFFICER' || role === 'PLANNING_OFFICER') return 'TIER_4_STAFF';
    return '';
  })();
  const canDirectorApprove = tier === 'TIER_1_ADMIN' || tier === 'TIER_3_DIRECTOR';
  const canExecutiveApprove = tier === 'TIER_1_ADMIN' || tier === 'TIER_2_EXEC';

  // --- Edit / Delete (Super Admin + Executive) ---
  const canEditDelete = role === 'SUPER_ADMIN' || role === 'EXECUTIVE';

  const handleDirectorApprove = async (id: string) => {
    const notes = window.prompt('Director approval notes (optional):', 'Technical merit confirmed.');
    if (notes === null) return;
    setApprovalBusy(id);
    try {
      await api.directorApproveIntervention(id, notes);
      await onRefresh?.();
    } catch (err: any) {
      alert(`Director approval failed: ${err.message}`);
    } finally {
      setApprovalBusy(null);
    }
  };

  const handleExecutiveApprove = async (id: string) => {
    const notes = window.prompt('Executive approval notes (optional):', 'Budget approved.');
    if (notes === null) return;
    setApprovalBusy(id);
    try {
      await api.executiveApproveIntervention(id, notes);
      await onRefresh?.();
    } catch (err: any) {
      alert(`Executive approval failed: ${err.message}`);
    } finally {
      setApprovalBusy(null);
    }
  };

  const handleReject = async (id: string) => {
    const reason = window.prompt('Rejection reason (required):', '');
    if (!reason) return;
    setApprovalBusy(id);
    try {
      await api.rejectIntervention(id, reason);
      await onRefresh?.();
    } catch (err: any) {
      alert(`Rejection failed: ${err.message}`);
    } finally {
      setApprovalBusy(null);
    }
  };

  const handleEditClick = (item: Intervention, e: React.MouseEvent) => {
    e.stopPropagation();
    if (onEditIntervention) {
      onEditIntervention(item);
    } else {
      alert('Edit handler not wired. Please ask the developer to pass onEditIntervention.');
    }
  };

  const handleDeleteClick = async (item: Intervention, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!onDeleteIntervention) {
      alert('Delete handler not wired. Please ask the developer to pass onDeleteIntervention.');
      return;
    }
    const linkedHazard = hazards.find(h => h.id === (item as any).hazard_id);
    const hasProject = Boolean((item as any).project_id);
    const warning = hasProject
      ? `\n\nWARNING: This intervention is linked to project ${(item as any).project_id}. Deleting it will orphan the project.`
      : '';
    const confirmed = window.confirm(
      `Delete intervention ${item.id}?\n\n"${item.title}"${
        linkedHazard ? `\n\nLinked hazard: ${linkedHazard.id} — ${linkedHazard.title}` : ''
      }${warning}\n\nThis cannot be undone and will be recorded in the audit log.`
    );
    if (!confirmed) return;
    await onDeleteIntervention(item);
  };

  const handleCreateProjectFromIntervention = async (data: any) => {
    await api.createProject(data);
    await onRefresh?.();
    setIsProjectModalOpen(false);
    setProjectSourceIntervention(null);
    alert('Project created — pending Executive approval.\n\nOpen the Projects Register to review or approve.');
  };

  const queueOf = (i: any): 'director' | 'executive' | 'approved' | 'other' => {
    const s = i.approval_status;
    if (s === 'Proposed' || s === 'Rejected' || s === undefined || s === null) return 'director';
    if (s === 'Director Approved') return 'executive';
    if (s === 'Executive Approved') return 'approved';
    return 'other';
  };

  const filteredInterventions = (interventions || []).filter((i: any) => {
    if (activeTab === 'all') return true;
    return queueOf(i) === activeTab;
  });

  const counts = {
    all: (interventions || []).length,
    director: (interventions || []).filter((i: any) => queueOf(i) === 'director').length,
    executive: (interventions || []).filter((i: any) => queueOf(i) === 'executive').length,
    approved: (interventions || []).filter((i: any) => queueOf(i) === 'approved').length,
  };

  const totalCost = (interventions || []).reduce((acc, i) => acc + (i.estimated_cost_ngn || 0), 0);

  return (
    <div id="intervention-planning-module" className="space-y-4">
      {/* Header */}
      {!hideHeader && (
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">Edo State Intervention Planning & Pipeline</h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              {interventions.length} Interventions
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Module 9: Two-stage approval workflow (Director → Executive), budget pipeline, and statutory fund allocation.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="text-right">
            <span className="text-[10px] text-slate-400 uppercase block font-semibold">Total Pipeline Budget</span>
            <span className="font-mono text-base font-black text-emerald-800">
              ₦{(totalCost / 1e9).toFixed(2)} Billion
            </span>
          </div>
          <button
            onClick={() => setIsHazardPickerOpen(true)}
            className="px-3 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white inline-flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            Plan New Intervention
          </button>
        </div>
      </div>
      )}

      {/* Approval Queue Tabs */}
      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center gap-2 text-xs">
        <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mr-2">Approval Queue:</span>
        {[
          { key: 'all',       label: `All (${counts.all})` },
          { key: 'director',  label: `Awaiting Director (${counts.director})` },
          { key: 'executive', label: `Awaiting Executive (${counts.executive})` },
          { key: 'approved',  label: `Approved (${counts.approved})` },
        ].map(t => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key as any)}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
              activeTab === t.key
                ? 'bg-emerald-800 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Interventions Register Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredInterventions.length === 0 && (
          <div className="bg-white p-8 rounded-xl border border-dashed border-slate-300 text-center">
            <Compass className="w-8 h-8 mx-auto text-slate-300 mb-2" />
            <p className="text-sm text-slate-500">No interventions in this queue.</p>
          </div>
        )}
        {filteredInterventions.map(item => {
          const linkedHazard = hazards.find(h => h.id === item.hazard_id);
          const status = (item as any).approval_status;
          const isDirectorPending = status === 'Proposed' || status === 'Rejected' || !status;
          const isExecutivePending = status === 'Director Approved';
          const isFullyApproved = status === 'Executive Approved';

          return (
            <div
              key={item.id}
              id={`intervention-row-${item.id}`}
              onClick={() => setSelectedIntervention(item)}
              className="aspect-square bg-white rounded-xl border border-slate-200 p-4 shadow-xs hover:border-emerald-500 hover:shadow-lg transition-all flex flex-col text-xs cursor-pointer relative"
              title="Click to view full details"
            >
              {/* Edit / Delete icons — Super Admin + Executive only */}
              {canEditDelete && (
                <div
                  className="absolute top-2 right-2 flex items-center gap-1 z-10"
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    onClick={(e) => handleEditClick(item, e)}
                    title="Edit intervention"
                    className="p-1 rounded bg-white/90 hover:bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200 shadow-xs"
                  >
                    <Pencil className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={(e) => handleDeleteClick(item, e)}
                    title="Delete intervention"
                    className="p-1 rounded bg-white/90 hover:bg-rose-100 text-rose-700 border border-slate-200 shadow-xs"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              {/* Top: ID + status badges */}
              <div className="flex flex-wrap items-center gap-1.5 mb-2 pr-14">
                <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                  {item.id}
                </span>
                <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                  item.priority === 'CRITICAL' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'
                }`}>
                  {item.priority}
                </span>
                {isDirectorPending && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-100 text-amber-800">
                    Awaiting Director
                  </span>
                )}
                {isExecutivePending && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-blue-100 text-blue-800">
                    Awaiting Executive
                  </span>
                )}
                {isFullyApproved && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-100 text-emerald-800">
                    ✓ Approved
                  </span>
                )}
                {status === 'Rejected' && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-100 text-rose-800">
                    Rejected
                  </span>
                )}
              </div>

              {/* Middle: title + linked hazard */}
              <div className="flex-1 min-h-0 overflow-hidden">
                <h3 className="font-bold text-slate-900 text-sm leading-tight line-clamp-3 mb-1.5">
                  {item.title}
                </h3>
                {linkedHazard && (
                  <p className="text-[10px] text-slate-500 line-clamp-2">
                    <span className="text-slate-400">Hazard:</span>{' '}
                    {linkedHazard.title}
                    {linkedHazard.community && <span className="text-slate-400"> · {linkedHazard.community}</span>}
                  </p>
                )}
              </div>

              {/* Bottom: cost + action */}
              <div className="pt-2 border-t border-slate-100">
                <div className="flex items-end justify-between mb-2">
                  <div>
                    <div className="text-[9px] text-slate-400 uppercase tracking-wider">Est. Cost</div>
                    <div className="font-mono text-sm font-black text-slate-900 leading-tight">
                      ₦{(item.estimated_cost_ngn / 1e6).toFixed(1)}M
                    </div>
                  </div>
                  {isFullyApproved && item.project_id && (
                    <span className="text-[9px] text-emerald-700 font-semibold">
                      {item.project_id}
                    </span>
                  )}
                </div>

                {/* Action button (compact) */}
                <div onClick={(e) => e.stopPropagation()}>
                  {isFullyApproved && !item.project_id && (
                    <button
                      onClick={() => {
                        setProjectSourceIntervention(item);
                        setIsProjectModalOpen(true);
                      }}
                      className="w-full px-2 py-1.5 rounded-lg text-[10px] font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center justify-center gap-1"
                    >
                      <FolderGit2 className="w-3 h-3" />
                      Create Project
                    </button>
                  )}
                  {item.project_id && (
                    <button
                      onClick={() => {
                        window.dispatchEvent(new CustomEvent('navigate-view', { detail: 'projects' }));
                      }}
                      className="w-full px-2 py-1.5 rounded-lg text-[10px] font-bold bg-slate-700 hover:bg-slate-600 text-white inline-flex items-center justify-center gap-1"
                    >
                      <FolderGit2 className="w-3 h-3" />
                      View Project
                    </button>
                  )}
                  {(canDirectorApprove && isDirectorPending) && (
                    <div className="flex gap-1">
                      <button
                        onClick={() => handleDirectorApprove(item.id)}
                        disabled={approvalBusy === item.id}
                        className="flex-1 px-2 py-1.5 rounded-lg text-[10px] font-bold bg-emerald-700 hover:bg-emerald-800 text-white disabled:opacity-50"
                      >
                        {approvalBusy === item.id ? '…' : 'Approve'}
                      </button>
                      <button
                        onClick={() => handleReject(item.id)}
                        disabled={approvalBusy === item.id}
                        className="px-2 py-1.5 rounded-lg text-[10px] font-bold bg-rose-700 hover:bg-rose-800 text-white disabled:opacity-50"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                  {(canExecutiveApprove && isExecutivePending) && (
                    <div className="flex gap-1">
                      <button
                        onClick={() => handleExecutiveApprove(item.id)}
                        disabled={approvalBusy === item.id}
                        className="flex-1 px-2 py-1.5 rounded-lg text-[10px] font-bold bg-blue-700 hover:bg-blue-800 text-white disabled:opacity-50"
                      >
                        {approvalBusy === item.id ? '…' : 'Executive Approve'}
                      </button>
                      <button
                        onClick={() => handleReject(item.id)}
                        disabled={approvalBusy === item.id}
                        className="px-2 py-1.5 rounded-lg text-[10px] font-bold bg-rose-700 hover:bg-rose-800 text-white disabled:opacity-50"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Step 1: pick a hazard */}
      {isHazardPickerOpen && (
        <HazardPickerModal
          hazards={hazards}
          interventions={interventions}
          onClose={() => setIsHazardPickerOpen(false)}
          onPick={(h) => {
            setPickerSelectedHazard(h);
            setIsHazardPickerOpen(false);
            setIsNewModalOpen(true);
          }}
        />
      )}

      {/* Create Project from an Executive-Approved intervention */}
      <ProjectModal
        isOpen={isProjectModalOpen}
        onClose={() => {
          setIsProjectModalOpen(false);
          setProjectSourceIntervention(null);
        }}
        onSubmit={handleCreateProjectFromIntervention}
        statesAndLgas={referenceData?.states_and_lgas || {}}
        categories={referenceData?.hazard_categories || []}
        prefillInterventionId={projectSourceIntervention?.id}
        referenceData={referenceData}
      />

      {/* Intervention detail modal */}
      {selectedIntervention && (
        <InterventionDetailModal
          intervention={selectedIntervention}
          hazard={hazards.find((h: any) => h.id === selectedIntervention.hazard_id) || null}
          project={projects.find((p: any) => p.id === selectedIntervention.project_id) || null}
          currentUser={currentUser}
          canDirectorApprove={canDirectorApprove}
          canExecutiveApprove={canExecutiveApprove}
          canEditDelete={canEditDelete}
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
          onEdit={(iv) => {
            setSelectedIntervention(null);
            if (onEditIntervention) onEditIntervention(iv);
          }}
          onDelete={async (iv) => {
            setSelectedIntervention(null);
            if (onDeleteIntervention) await onDeleteIntervention(iv);
          }}
        />
      )}

      {/* Step 2: intervention form, prefilled with the picked hazard */}
      <InterventionModal
        isOpen={isNewModalOpen}
        onClose={() => {
          setIsNewModalOpen(false);
          setPickerSelectedHazard(null);
        }}
        hazard={pickerSelectedHazard}
        currentUser={currentUser}
        onSuccess={async () => {
          setIsNewModalOpen(false);
          setPickerSelectedHazard(null);
          await onRefresh?.();
        }}
      />
    </div>
  );
};

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
  canEditDelete: boolean;
  onClose: () => void;
  onDirectorApprove: (id: string) => Promise<void>;
  onExecutiveApprove: (id: string) => Promise<void>;
  onReject: (id: string) => Promise<void>;
  onCreateProject: (iv: any) => void;
  onEdit: (iv: any) => void;
  onDelete: (iv: any) => Promise<void>;
}> = ({
  intervention,
  hazard,
  project,
  currentUser,
  canDirectorApprove,
  canExecutiveApprove,
  canEditDelete,
  onClose,
  onDirectorApprove,
  onExecutiveApprove,
  onReject,
  onCreateProject,
  onEdit,
  onDelete,
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
          <div className="flex items-center gap-1.5 ml-3">
            {canEditDelete && (
              <>
                <button
                  onClick={() => onEdit(intervention)}
                  title="Edit intervention"
                  className="p-1.5 rounded-lg bg-emerald-800/60 hover:bg-emerald-700 text-emerald-100"
                >
                  <Pencil className="w-4 h-4" />
                </button>
                <button
                  onClick={() => onDelete(intervention)}
                  title="Delete intervention"
                  className="p-1.5 rounded-lg bg-rose-900/60 hover:bg-rose-800 text-rose-100"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
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

          <Section title="Responsibility">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Field label="Department">{intervention.responsible_department || '—'}</Field>
              <Field label="Officer">{intervention.responsible_officer || '—'}</Field>
            </div>
          </Section>

          <Section title="Timeline">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Field label="Target Start">{intervention.proposed_start_date || '—'}</Field>
              <Field label="Target Completion">{intervention.proposed_completion_date || '—'}</Field>
            </div>
          </Section>

          {intervention.expected_outcome && (
            <Section title="Expected Outcome">
              {intervention.expected_outcome}
            </Section>
          )}

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

          <Section title={`Evidence Attachments (${allEvidence.length})`}>
            {loading ? (
              <div className="text-slate-400 text-[11px]">Loading evidence…</div>
            ) : allEvidence.length === 0 ? (
              <div className="text-slate-400 text-[11px] italic">No evidence attached to the linked hazard or project.</div>
            ) : (
              <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                {allEvidence.map((e: any, __idx: number) => (
                  <div
                    key={e.id}
                    onClick={() => setActiveMedia({ images: allEvidence, index: __idx })}
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
          {isFullyApproved && !project && !intervention.project_id && (
            <button
              onClick={() => onCreateProject(intervention)}
              className="px-3 py-2 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center gap-1.5"
            >
              Create Project
            </button>
          )}
          {(intervention.project_id || project) && (
            <button
              onClick={() => {
                window.dispatchEvent(new CustomEvent('navigate-view', { detail: 'projects' }));
                onClose();
              }}
              className="px-3 py-2 rounded-lg text-xs font-bold bg-slate-700 hover:bg-slate-600 text-white inline-flex items-center gap-1.5"
            >
              <FolderGit2 className="w-3.5 h-3.5" />
              View Project ({intervention.project_id || project?.id})
            </button>
          )}
        </div>
      </div>

      {activeMedia && (() => {
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