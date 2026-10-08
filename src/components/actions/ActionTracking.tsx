import React, { useState } from 'react';
import { ActionItem, HazardSeverity } from '../../types/index.ts';
import {
  CheckCircle,
  Plus,
  Clock,
  AlertTriangle,
  Search,
  CheckSquare,
  UserCheck,
  RotateCcw,
  Filter,
  X,
  Layers,
  Calendar,
  Pencil,
  Trash2,
  Save,
  Upload,
  FileText,
  Image,
  Paperclip,
  ExternalLink
} from 'lucide-react';

interface ActionTrackingProps {
  currentUser?: { role?: string; name?: string; id?: string } | null;
  actions: ActionItem[];
  onCreateAction: (data: Partial<ActionItem>) => Promise<void>;
  onUpdateAction: (id: string, data: Partial<ActionItem>) => Promise<void>;
}

export const ActionTracking: React.FC<ActionTrackingProps> = ({
  currentUser,
  actions = [],
  onCreateAction,
  onUpdateAction
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Edit modal state
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingAction, setEditingAction] = useState<ActionItem | null>(null);
  const [editForm, setEditForm] = useState<Partial<ActionItem>>({});
  const [editBusy, setEditBusy] = useState(false);

  // Evidence upload + preview
  const [evidenceForAction, setEvidenceForAction] = useState<ActionItem | null>(null);
  const [evidenceFile, setEvidenceFile] = useState<string>('');
  const [evidenceFileName, setEvidenceFileName] = useState<string>('');
  const [evidenceFileType, setEvidenceFileType] = useState<string>('');
  const [evidenceDescription, setEvidenceDescription] = useState<string>('');
  const [evidenceBusy, setEvidenceBusy] = useState(false);
  const [evidenceError, setEvidenceError] = useState('');
  const [previewItem, setPreviewItem] = useState<{ evidence: any; action: any } | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedActionForDetail, setSelectedActionForDetail] = useState<ActionItem | null>(null);

  // Role — set from props or a global context
  const currentRole = currentUser?.role || '';
  const [editError, setEditError] = useState('');

  // Extended filter state
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [assigneeFilter, setAssigneeFilter] = useState<string>('ALL');
  const [orgFilter, setOrgFilter] = useState<string>('ALL');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [overdueOnly, setOverdueOnly] = useState<boolean>(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    responsible_person: 'Engr. Osasere Imasuen',
    responsible_organization: 'Edo State Ministry of Environment & Sustainability / EDEFA',
    priority: 'HIGH' as HazardSeverity,
    due_date: new Date(Date.now() + 14 * 86400000).toISOString().split('T')[0],
    status: 'Assigned' as const,
    progress_percentage: 20
  });

  // Derive filter options from actual data
  const statusOptions = Array.from(
    new Set((actions || []).map(a => a.status).filter(Boolean) as string[])
  ).sort();

  const priorityOptions = Array.from(
    new Set((actions || []).map(a => a.priority).filter(Boolean) as string[])
  ).sort();

  const assigneeOptions = Array.from(
    new Set((actions || []).map(a => a.responsible_person).filter(Boolean) as string[])
  ).sort();

  const orgOptions = Array.from(
    new Set((actions || []).map(a => a.responsible_organization).filter(Boolean) as string[])
  ).sort();

  // Classify which entity an action belongs to
  const linkedEntity = (a: any): { type: 'HAZARD' | 'PROJECT' | 'INTERVENTION' | 'NONE'; id: string } => {
    if (a.hazard_id) return { type: 'HAZARD', id: a.hazard_id };
    if (a.project_id) return { type: 'PROJECT', id: a.project_id };
    if (a.intervention_id) return { type: 'INTERVENTION', id: a.intervention_id };
    return { type: 'NONE', id: '' };
  };

  // Compute days until due (negative if overdue)
  const daysUntilDue = (dueDate: string | undefined, status: string): number | null => {
    if (!dueDate) return null;
    if (status === 'Completed' || status === 'Verified' || status === 'Closed') return null;
    const due = new Date(dueDate).getTime();
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const diffMs = due - today.getTime();
    return Math.round(diffMs / 86400000);
  };

  // Wildcard search across all fields
  const matchesSearch = (a: any, q: string): boolean => {
    if (!q) return true;
    const lower = q.toLowerCase();
    const haystack = [
      a.id,
      a.title,
      a.description,
      a.responsible_person,
      a.responsible_organization,
      a.hazard_id,
      a.project_id,
      a.intervention_id,
      a.status,
      a.priority,
      a.due_date,
      a.completion_date,
      a.verified_by,
      a.evidence_summary,
      a.verification_comments,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return haystack.includes(lower);
  };

  const filteredActions = (actions || []).filter(a => {
    if (statusFilter !== 'ALL' && a.status !== statusFilter) return false;
    if (priorityFilter !== 'ALL' && a.priority !== priorityFilter) return false;
    if (assigneeFilter !== 'ALL' && a.responsible_person !== assigneeFilter) return false;
    if (orgFilter !== 'ALL' && a.responsible_organization !== orgFilter) return false;
    if (dateFrom && a.due_date && a.due_date < dateFrom) return false;
    if (dateTo && a.due_date && a.due_date > dateTo) return false;
    if (overdueOnly && !a.is_overdue) return false;
    if (!matchesSearch(a, searchTerm)) return false;
    return true;
  });

  // Header stat counts
  const totalActions = (actions || []).length;
  const overdueCount = (actions || []).filter(a => a.is_overdue).length;
  const completedCount = (actions || []).filter(a => a.status === 'Completed').length;
  const verifiedCount = (actions || []).filter(a => a.status === 'Verified').length;

  const resetActionFilters = () => {
    setSearchTerm('');
    setStatusFilter('ALL');
    setPriorityFilter('ALL');
    setAssigneeFilter('ALL');
    setOrgFilter('ALL');
    setDateFrom('');
    setDateTo('');
    setOverdueOnly(false);
  };

  const actionHasActiveFilters =
    searchTerm !== '' ||
    statusFilter !== 'ALL' ||
    priorityFilter !== 'ALL' ||
    assigneeFilter !== 'ALL' ||
    orgFilter !== 'ALL' ||
    dateFrom !== '' ||
    dateTo !== '' ||
    overdueOnly;


  const handleMarkCompleted = async (action: ActionItem) => {
    const evidence = (action as any).evidence_files || [];
    if (evidence.length === 0) {
      // No evidence yet — open the upload modal instead
      const proceed = window.confirm(
        'Evidence is required to mark this action complete.\n\nDo you want to upload evidence now?'
      );
      if (proceed) openEvidenceModal(action);
      return;
    }
    try {
      await onUpdateAction(action.id, { status: 'Completed', progress_percentage: 100 });
    } catch (err: any) {
      alert(`Failed to mark complete: ${err?.message || 'Unknown error'}`);
    }
  };

  const handleVerifyClose = async (action: ActionItem) => {
    try {
      await onUpdateAction(action.id, {
        status: 'Verified',
        verified_by: 'Engr. Director Audits',
      });
    } catch (err: any) {
      alert(`Failed to verify: ${err?.message || 'Unknown error'}`);
    }
  };

  const openEvidenceModal = (action: ActionItem) => {
    setEvidenceForAction(action);
    setEvidenceFile('');
    setEvidenceFileName('');
    setEvidenceFileType('');
    setEvidenceDescription('');
    setEvidenceError('');
  };

  const handleEvidenceFilePick = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      setEvidenceFile(String(reader.result || ''));
      setEvidenceFileName(file.name);
      setEvidenceFileType(file.type);
    };
    reader.readAsDataURL(file);
  };

  const submitEvidence = async () => {
    if (!evidenceForAction || !evidenceFile) {
      setEvidenceError('Please select a file.');
      return;
    }
    setEvidenceBusy(true);
    setEvidenceError('');
    try {
      const { api } = await import('../../services/api.ts');
      const mediaType = evidenceFileType.startsWith('image') ? 'photo' : 'document';
      await api.uploadActionEvidence(evidenceForAction.id, {
        file_name: evidenceFileName,
        file_type: evidenceFileType,
        base64_data: evidenceFile,
        media_type: mediaType,
        description: evidenceDescription || 'Action completion evidence',
        stage_tag: 'after',
      });
      setEvidenceForAction(null);
      window.location.reload();
    } catch (err: any) {
      setEvidenceError(err?.message || 'Upload failed');
    } finally {
      setEvidenceBusy(false);
    }
  };

  const canEditActionMetadata = currentRole === 'SUPER_ADMIN' || currentRole === 'EXECUTIVE';
  const canMarkComplete = (action: ActionItem) => {
    if (currentRole === 'SUPER_ADMIN' || currentRole === 'EXECUTIVE') return true;
    return false; // Staff/Director handled by backend ownership check
  };

  const openEditModal = (action: ActionItem) => {
    setEditingAction(action);
    setEditForm({ ...action });
    setEditError('');
    setIsEditModalOpen(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingAction) return;
    setEditError('');
    setEditBusy(true);
    try {
      await onUpdateAction(editingAction.id, editForm);
      setIsEditModalOpen(false);
      setEditingAction(null);
    } catch (err: any) {
      setEditError(err?.message || 'Failed to save changes');
    } finally {
      setEditBusy(false);
    }
  };

  const handleDeleteAction = async (action: ActionItem) => {
    const confirmed = window.confirm(
      `Delete action ${action.id}?\n\n"${action.title}"\n\nThis cannot be undone and will be recorded in the audit log.`
    );
    if (!confirmed) return;
    try {
      // Call the API directly
      const { api } = await import('../../services/api.ts');
      await api.deleteAction(action.id);
      window.location.reload();
    } catch (err: any) {
      alert(`Delete failed: ${err?.message || 'Unknown error'}`);
    }
  };

  const canDeleteAction = (action: ActionItem) => {
    // Only T1/T2 can delete; the backend enforces it, this is a UI hint
    return true; // we let the backend return 403 if not permitted
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onCreateAction(formData);
    setIsModalOpen(false);
  };


  return (
    <div id="action-tracking-module" className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">Corrective Actions & Follow-up Tracker</h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              {actions.length} Action Directives
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Module 10: Task assignment, contractor compliance directives, timeline enforcement, and physical verification.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="px-3.5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white inline-flex items-center transition-colors shadow-xs"
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Issue Action Directive
        </button>
      </div>

      {/* Action filter bar */}
      <div
        id="action-filter-bar"
        className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3"
      >
        {/* Stat pills */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={resetActionFilters}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              !actionHasActiveFilters
                ? 'bg-emerald-800 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            All ({totalActions})
          </button>
          <button
            onClick={() => { resetActionFilters(); setOverdueOnly(true); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              overdueOnly
                ? 'bg-rose-700 text-white'
                : 'bg-rose-100 text-rose-800 hover:bg-rose-200'
            }`}
          >
            Overdue ({overdueCount})
          </button>
          <button
            onClick={() => { resetActionFilters(); setStatusFilter('Completed'); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              statusFilter === 'Completed'
                ? 'bg-blue-700 text-white'
                : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
            }`}
          >
            Completed ({completedCount})
          </button>
          <button
            onClick={() => { resetActionFilters(); setStatusFilter('Verified'); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              statusFilter === 'Verified'
                ? 'bg-teal-700 text-white'
                : 'bg-teal-100 text-teal-800 hover:bg-teal-200'
            }`}
          >
            Verified ({verifiedCount})
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            placeholder="Wildcard search — ID, title, description, assignee, organization, linked IDs..."
            className="w-full pl-9 pr-9 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 text-xs"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded hover:bg-slate-100 text-slate-400"
              title="Clear search"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Dropdown filters */}
        <div className="flex flex-wrap items-end gap-3 text-xs">
          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Status</span>
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[160px]"
            >
              <option value="ALL">All Statuses ({statusOptions.length})</option>
              {statusOptions.map(s => (<option key={s} value={s}>{s}</option>))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Priority</span>
            <select
              value={priorityFilter}
              onChange={e => setPriorityFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[140px]"
            >
              <option value="ALL">All Priorities</option>
              {priorityOptions.map(p => (<option key={p} value={p}>{p}</option>))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Assignee</span>
            <select
              value={assigneeFilter}
              onChange={e => setAssigneeFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[180px]"
            >
              <option value="ALL">All Assignees ({assigneeOptions.length})</option>
              {assigneeOptions.map(a => (<option key={a} value={a}>{a}</option>))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Organization</span>
            <select
              value={orgFilter}
              onChange={e => setOrgFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[220px]"
            >
              <option value="ALL">All Organizations ({orgOptions.length})</option>
              {orgOptions.map(o => (<option key={o} value={o}>{o}</option>))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Due From</span>
            <input
              type="date"
              value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600"
            />
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Due To</span>
            <input
              type="date"
              value={dateTo}
              onChange={e => setDateTo(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600"
            />
          </label>

          <label className="flex items-center gap-2 pb-2">
            <input
              type="checkbox"
              checked={overdueOnly}
              onChange={e => setOverdueOnly(e.target.checked)}
              className="w-4 h-4"
            />
            <span className="text-xs font-semibold text-slate-700">Overdue only</span>
          </label>

          {actionHasActiveFilters && (
            <button
              onClick={resetActionFilters}
              className="px-3 py-2 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 inline-flex items-center gap-1.5 h-[38px]"
              title="Reset all filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Filters
            </button>
          )}
        </div>

        {/* Result count */}
        <div className="text-[11px] text-slate-500 border-t border-slate-100 pt-2 flex items-center gap-2">
          <Filter className="w-3.5 h-3.5" />
          Showing <strong className="text-slate-700">{filteredActions.length}</strong> of{' '}
          <strong className="text-slate-700">{totalActions}</strong> action directives
          {actionHasActiveFilters && (
            <span className="text-emerald-700 font-semibold">— filters active</span>
          )}
        </div>
      </div>

      {/* Action cards grid/list */}
      <div>
        {/* View mode toggle */}
        <div className="flex items-center justify-between mb-3">
          <div className="text-[11px] text-slate-500">
            Showing <strong className="text-slate-700">{filteredActions.length}</strong> of{' '}
            <strong className="text-slate-700">{totalActions}</strong> directives
          </div>
          <div className="flex items-center gap-1 bg-white border border-slate-200 rounded-lg p-0.5">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                viewMode === 'grid' ? 'bg-emerald-700 text-white' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                viewMode === 'list' ? 'bg-emerald-700 text-white' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              List
            </button>
          </div>
        </div>

        {/* Grid view — square cards */}
        {viewMode === 'grid' && (
          <div
            id="action-card-grid"
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
          >
            {filteredActions.map(item => {
              const evidenceCount = ((item as any).evidence_files || []).length;
              const priorityColor =
                item.priority === 'CRITICAL' ? 'bg-rose-100 text-rose-800' :
                item.priority === 'HIGH' ? 'bg-amber-100 text-amber-800' :
                item.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                'bg-emerald-100 text-emerald-800';
              const statusColor =
                item.status === 'Verified' ? 'bg-teal-100 text-teal-800' :
                item.status === 'Completed' ? 'bg-blue-100 text-blue-800' :
                item.status === 'Overdue' ? 'bg-rose-100 text-rose-800' :
                item.status === 'In Progress' ? 'bg-indigo-100 text-indigo-800' :
                'bg-slate-100 text-slate-700';
              return (
                <button
                  key={item.id}
                  id={`action-card-${item.id}`}
                  onClick={() => setSelectedActionForDetail(item)}
                  className={`group text-left aspect-square rounded-xl border-2 transition-all p-4 flex flex-col justify-between ${
                    item.is_overdue
                      ? 'bg-rose-50/40 border-rose-300 hover:border-rose-500 hover:shadow-lg'
                      : 'bg-white border-slate-200 hover:border-emerald-500 hover:shadow-lg'
                  }`}
                >
                  {/* Header: ID + priority */}
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                        {item.id}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${priorityColor}`}>
                        {item.priority}
                      </span>
                    </div>

                    {/* Status */}
                    <div className="flex flex-wrap items-center gap-1">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${statusColor}`}>
                        {item.status}
                      </span>
                      {item.is_overdue && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-600 text-white animate-pulse">
                          OVERDUE
                        </span>
                      )}
                    </div>

                    {/* Title */}
                    <h3 className="font-bold text-slate-900 text-sm leading-snug line-clamp-3">
                      {item.title}
                    </h3>
                  </div>

                  {/* Progress bar */}
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-[10px] text-slate-500">
                      <span>Progress</span>
                      <span className="font-mono font-bold text-slate-800">
                        {item.progress_percentage}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          item.progress_percentage === 100 ? 'bg-emerald-600' : 'bg-emerald-500'
                        }`}
                        style={{ width: `${item.progress_percentage}%` }}
                      />
                    </div>
                  </div>

                  {/* Footer: assignee + evidence + due */}
                  <div className="space-y-1.5 text-[10px] text-slate-600 border-t border-slate-100 pt-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="truncate" title={item.responsible_person}>
                        👤 {item.responsible_person || '—'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between gap-2">
                      <span className={item.is_overdue ? 'text-rose-700 font-bold' : ''}>
                        📅 {item.due_date}
                      </span>
                      {evidenceCount > 0 && (
                        <span className="text-emerald-700 font-semibold">
                          📎 {evidenceCount}
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* List view — original card layout (same as before, kept for power users) */}
        {viewMode === 'list' && (
          <div className="space-y-3">
            {filteredActions.map(item => (
              <button
                key={item.id}
                id={`action-row-${item.id}`}
                onClick={() => setSelectedActionForDetail(item)}
                className="w-full text-left bg-white rounded-xl border border-slate-200 p-4 shadow-xs hover:border-emerald-500 transition-colors text-xs space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-2">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                        {item.id}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        item.priority === 'CRITICAL' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {item.priority}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700">
                        {item.status}
                      </span>
                      {item.is_overdue && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-600 text-white animate-pulse">
                          OVERDUE
                        </span>
                      )}
                    </div>
                    <h3 className="font-bold text-slate-900 text-sm mt-1">{item.title}</h3>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 block font-semibold">Due Date</span>
                    <span className={`font-mono text-xs font-bold ${item.is_overdue ? 'text-rose-600' : 'text-slate-800'}`}>
                      {item.due_date}
                    </span>
                  </div>
                </div>
                <p className="text-slate-700 leading-relaxed">{item.description}</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-600 bg-slate-50 p-2.5 rounded-lg">
                  <div><strong>Assigned To:</strong> {item.responsible_person}</div>
                  <div><strong>Organization:</strong> {item.responsible_organization}</div>
                </div>
                <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-500">Progress:</span>
                    <span className="font-bold text-emerald-800">{item.progress_percentage}%</span>
                  </div>
                  <span className="text-[11px] text-emerald-700 font-semibold group-hover:underline">
                    Click to view details →
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 text-xs">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-5 border border-slate-200">
            <h3 className="text-sm font-bold text-slate-900 mb-3">Issue Corrective Action Directive</h3>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="block font-semibold mb-1">Action Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Immediate reinforcement of gully toe protection"
                  value={formData.title}
                  onChange={e => setFormData({ ...formData, title: e.target.value })}
                  className="w-full p-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">Description / Directive *</label>
                <textarea
                  rows={3}
                  required
                  value={formData.description}
                  onChange={e => setFormData({ ...formData, description: e.target.value })}
                  className="w-full p-2 border rounded-lg"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold mb-1">Assigned Person</label>
                  <input
                    type="text"
                    value={formData.responsible_person}
                    onChange={e => setFormData({ ...formData, responsible_person: e.target.value })}
                    className="w-full p-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1">Organization</label>
                  <input
                    type="text"
                    value={formData.responsible_organization}
                    onChange={e => setFormData({ ...formData, responsible_organization: e.target.value })}
                    className="w-full p-2 border rounded-lg"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold mb-1">Priority</label>
                  <select
                    value={formData.priority}
                    onChange={e => setFormData({ ...formData, priority: e.target.value as any })}
                    className="w-full p-2 border rounded-lg bg-white"
                  >
                    <option value="CRITICAL">CRITICAL</option>
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold mb-1">Due Date</label>
                  <input
                    type="date"
                    value={formData.due_date}
                    onChange={e => setFormData({ ...formData, due_date: e.target.value })}
                    className="w-full p-2 border rounded-lg"
                  />
                </div>
              </div>

              <div className="pt-3 border-t flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-emerald-700 text-white font-bold"
                >
                  Issue Directive
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {/* Edit Action Modal */}
      {isEditModalOpen && editingAction && (
        <div
          id="edit-action-modal"
          className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4"
        >
          <div className="bg-white rounded-xl shadow-2xl max-w-xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200 text-xs">
            <div className="px-5 py-4 bg-emerald-950 text-white flex items-center justify-between border-b border-emerald-900">
              <div>
                <h2 className="text-sm font-bold">Edit Action Directive</h2>
                <p className="text-[11px] text-emerald-300">{editingAction.id}</p>
              </div>
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="p-1 rounded bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="flex-1 overflow-y-auto p-5 space-y-3">
              {editError && (
                <div className="rounded-lg bg-rose-50 border border-rose-200 text-rose-800 p-2.5">
                  {editError}
                </div>
              )}

              <label className="block">
                <span className="font-semibold text-slate-700">Title</span>
                <input
                  value={editForm.title || ''}
                  onChange={e => setEditForm({ ...editForm, title: e.target.value })}
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                />
              </label>

              <label className="block">
                <span className="font-semibold text-slate-700">Description</span>
                <textarea
                  value={editForm.description || ''}
                  onChange={e => setEditForm({ ...editForm, description: e.target.value })}
                  rows={3}
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 resize-y"
                />
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <label className="block">
                  <span className="font-semibold text-slate-700">Responsible Person</span>
                  <input
                    value={editForm.responsible_person || ''}
                    onChange={e => setEditForm({ ...editForm, responsible_person: e.target.value })}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  />
                </label>

                <label className="block">
                  <span className="font-semibold text-slate-700">Organization</span>
                  <input
                    value={editForm.responsible_organization || ''}
                    onChange={e => setEditForm({ ...editForm, responsible_organization: e.target.value })}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  />
                </label>

                <label className="block">
                  <span className="font-semibold text-slate-700">Priority</span>
                  <select
                    value={editForm.priority || 'HIGH'}
                    onChange={e => setEditForm({ ...editForm, priority: e.target.value as any })}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  >
                    <option value="CRITICAL">CRITICAL</option>
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="LOW">LOW</option>
                  </select>
                </label>

                <label className="block">
                  <span className="font-semibold text-slate-700">Status</span>
                  <select
                    value={editForm.status || 'Assigned'}
                    onChange={e => setEditForm({ ...editForm, status: e.target.value as any })}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  >
                    <option value="Open">Open</option>
                    <option value="Assigned">Assigned</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                    <option value="Verified">Verified</option>
                    <option value="Closed">Closed</option>
                  </select>
                </label>

                <label className="block">
                  <span className="font-semibold text-slate-700">Due Date</span>
                  <input
                    type="date"
                    value={(editForm.due_date as string) || ''}
                    onChange={e => setEditForm({ ...editForm, due_date: e.target.value })}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  />
                </label>

                <label className="block">
                  <span className="font-semibold text-slate-700">Progress %</span>
                  <input
                    type="number"
                    min={0}
                    max={100}
                    value={editForm.progress_percentage ?? 0}
                    onChange={e => setEditForm({ ...editForm, progress_percentage: Number(e.target.value) })}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                  />
                </label>
              </div>
            </form>

            <div className="px-5 py-3 border-t border-slate-200 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsEditModalOpen(false)}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={(e) => handleEditSubmit(e as any)}
                disabled={editBusy}
                className="px-5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white disabled:opacity-50 inline-flex items-center gap-1.5"
              >
                <Save className="w-4 h-4" />
                {editBusy ? 'Saving…' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}


      {/* Evidence Upload Modal */}
      {evidenceForAction && (
        <div className="fixed inset-0 z-[60] overflow-y-auto bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200 text-xs">
            <div className="px-5 py-4 bg-emerald-950 text-white flex items-center justify-between border-b border-emerald-900">
              <div>
                <h2 className="text-sm font-bold">Upload Completion Evidence</h2>
                <p className="text-[11px] text-emerald-300">
                  For action {evidenceForAction.id} — {evidenceForAction.title}
                </p>
              </div>
              <button
                onClick={() => setEvidenceForAction(null)}
                className="p-1 rounded bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-5 space-y-3">
              {evidenceError && (
                <div className="rounded-lg bg-rose-50 border border-rose-200 text-rose-800 p-2.5">
                  {evidenceError}
                </div>
              )}
              <label className="block">
                <span className="font-semibold text-slate-700">Choose file (image or PDF)</span>
                <input
                  type="file"
                  accept="image/*,application/pdf"
                  onChange={handleEvidenceFilePick}
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
                />
              </label>
              {evidenceFile && (
                <div className="rounded-lg border border-slate-200 p-3 bg-slate-50">
                  <div className="text-[11px] text-slate-600 mb-2">
                    <strong>{evidenceFileName}</strong> — {evidenceFileType}
                  </div>
                  {evidenceFileType.startsWith('image') && (
                    <img
                      src={evidenceFile}
                      alt="preview"
                      className="max-h-48 rounded object-contain mx-auto"
                    />
                  )}
                </div>
              )}
              <label className="block">
                <span className="font-semibold text-slate-700">Description</span>
                <textarea
                  value={evidenceDescription}
                  onChange={e => setEvidenceDescription(e.target.value)}
                  rows={2}
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 resize-y"
                  placeholder="What does this evidence show?"
                />
              </label>
            </div>
            <div className="px-5 py-3 border-t border-slate-200 flex items-center justify-end gap-2">
              <button
                onClick={() => setEvidenceForAction(null)}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={submitEvidence}
                disabled={evidenceBusy || !evidenceFile}
                className="px-5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white disabled:opacity-50 inline-flex items-center gap-1.5"
              >
                <Upload className="w-4 h-4" />
                {evidenceBusy ? 'Uploading…' : 'Upload Evidence'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Evidence Preview Lightbox */}
      {previewItem && (
        <div
          onClick={() => setPreviewItem(null)}
          className="fixed inset-0 z-[70] bg-black/80 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto"
        >
          <div
            onClick={e => e.stopPropagation()}
            className="bg-white rounded-xl max-w-3xl w-full p-5 space-y-4 my-8"
          >
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">{previewItem.evidence.file_name}</h3>
                <p className="text-[11px] text-slate-500">
                  {previewItem.action.id} — {previewItem.action.title}
                </p>
              </div>
              <button
                onClick={() => setPreviewItem(null)}
                className="p-1 rounded hover:bg-slate-100 text-slate-500"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* File preview */}
            <div className="rounded-lg bg-slate-900 flex items-center justify-center min-h-[280px] max-h-[60vh] overflow-hidden">
              {previewItem.evidence.media_type === 'photo'
                || previewItem.evidence.file_type?.startsWith('image') ? (
                <img
                  src={previewItem.evidence.file_url}
                  alt={previewItem.evidence.file_name}
                  className="max-h-[60vh] w-auto object-contain"
                />
              ) : previewItem.evidence.file_type === 'application/pdf' ? (
                <iframe
                  src={previewItem.evidence.file_url}
                  className="w-full h-[60vh]"
                  title={previewItem.evidence.file_name}
                />
              ) : (
                <div className="text-white text-center p-6">
                  <FileText className="w-12 h-12 mx-auto text-slate-500 mb-2" />
                  <p className="text-sm">Preview not available</p>
                  <a
                    href={previewItem.evidence.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 inline-block text-amber-400 hover:text-amber-300 underline text-xs"
                  >
                    Download file
                  </a>
                </div>
              )}
            </div>

            {/* Action & evidence details */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px]">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <div className="font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Action
                </div>
                <div><strong>ID:</strong> {previewItem.action.id}</div>
                <div><strong>Priority:</strong> {previewItem.action.priority}</div>
                <div><strong>Status:</strong> {previewItem.action.status}</div>
                <div><strong>Due:</strong> {previewItem.action.due_date}</div>
                {previewItem.action.completion_date && (
                  <div><strong>Completed:</strong> {previewItem.action.completion_date}</div>
                )}
                <div><strong>Assignee:</strong> {previewItem.action.responsible_person}</div>
                <div><strong>Organization:</strong> {previewItem.action.responsible_organization}</div>
                <div><strong>Progress:</strong> {previewItem.action.progress_percentage}%</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <div className="font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Evidence
                </div>
                <div><strong>Uploaded:</strong> {previewItem.evidence.upload_date}</div>
                <div><strong>By:</strong> {previewItem.evidence.uploader_name}</div>
                <div><strong>Type:</strong> {previewItem.evidence.media_type}</div>
                {previewItem.evidence.gps_latitude && (
                  <div>
                    <strong>GPS:</strong>{' '}
                    <span className="font-mono">
                      {previewItem.evidence.gps_latitude?.toFixed(5)},{' '}
                      {previewItem.evidence.gps_longitude?.toFixed(5)}
                    </span>
                  </div>
                )}
                {previewItem.evidence.description && (
                  <div className="mt-1 italic text-slate-600">
                    "{previewItem.evidence.description}"
                  </div>
                )}
              </div>
            </div>

            <div className="text-right">
              <a
                href={previewItem.evidence.file_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-xs text-emerald-700 hover:text-emerald-900 font-semibold"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                Open in new tab
              </a>
            </div>
          </div>
        </div>
      )}


      {/* Action Detail Modal */}
      {selectedActionForDetail && (() => {
        const item = selectedActionForDetail;
        const evidenceFiles = (item as any).evidence_files || [];
        const priorityColor =
          item.priority === 'CRITICAL' ? 'bg-rose-100 text-rose-800' :
          item.priority === 'HIGH' ? 'bg-amber-100 text-amber-800' :
          item.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
          'bg-emerald-100 text-emerald-800';
        const statusColor =
          item.status === 'Verified' ? 'bg-teal-100 text-teal-800' :
          item.status === 'Completed' ? 'bg-blue-100 text-blue-800' :
          item.status === 'Overdue' ? 'bg-rose-100 text-rose-800' :
          item.status === 'In Progress' ? 'bg-indigo-100 text-indigo-800' :
          'bg-slate-100 text-slate-700';
        return (
          <div
            id="action-detail-modal"
            onClick={() => setSelectedActionForDetail(null)}
            className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4"
          >
            <div
              onClick={e => e.stopPropagation()}
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200 text-xs"
            >
              {/* Header */}
              <div className="px-5 py-4 bg-emerald-950 text-white flex items-start justify-between border-b border-emerald-900">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-[10px] text-emerald-300 bg-emerald-900 px-2 py-0.5 rounded">
                      {item.id}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${priorityColor}`}>
                      {item.priority}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${statusColor}`}>
                      {item.status}
                    </span>
                    {item.is_overdue && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-600 text-white animate-pulse">
                        OVERDUE
                      </span>
                    )}
                  </div>
                  <h2 className="text-base font-bold mt-2 max-w-xl">{item.title}</h2>
                </div>
                <button
                  onClick={() => setSelectedActionForDetail(null)}
                  className="p-1.5 rounded bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 shrink-0"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Body */}
              <div className="flex-1 overflow-y-auto p-5 space-y-4">
                {/* Description */}
                {item.description && (
                  <div>
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                      Description
                    </div>
                    <p className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                )}

                {/* Grid of details */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                      Assignment
                    </div>
                    <div className="space-y-1">
                      <div><strong>Person:</strong> {item.responsible_person || '—'}</div>
                      <div><strong>Organization:</strong> {item.responsible_organization || '—'}</div>
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                      Timeline
                    </div>
                    <div className="space-y-1">
                      <div><strong>Due:</strong> {item.due_date || '—'}</div>
                      {item.completion_date && (
                        <div><strong>Completed:</strong> {item.completion_date}</div>
                      )}
                      <div><strong>Created:</strong> {item.created_at?.slice(0, 10) || '—'}</div>
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 sm:col-span-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                        Progress
                      </span>
                      <span className="font-mono font-bold text-slate-800">
                        {item.progress_percentage}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 h-3 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          item.progress_percentage === 100 ? 'bg-emerald-600' : 'bg-emerald-500'
                        }`}
                        style={{ width: `${item.progress_percentage}%` }}
                      />
                    </div>
                  </div>

                  {/* Verification note */}
                  {item.verification_comments && (
                    <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 sm:col-span-2">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 mb-1">
                        Verification
                      </div>
                      <p className="text-emerald-900">{item.verification_comments}</p>
                      {item.verified_by && (
                        <div className="text-[11px] text-emerald-700 mt-1">
                          by {item.verified_by}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Evidence gallery */}
                <div>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                    <Paperclip className="w-3.5 h-3.5" />
                    Evidence ({evidenceFiles.length})
                  </div>
                  {evidenceFiles.length === 0 ? (
                    <div className="p-4 rounded-lg border border-dashed border-slate-300 text-center text-slate-400">
                      No evidence uploaded yet.
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {evidenceFiles.map((ev: any) => (
                        <button
                          key={ev.id}
                          onClick={() => setPreviewItem({ evidence: ev, action: item })}
                          className="group text-left rounded-lg border border-slate-200 bg-slate-50 hover:border-emerald-500 overflow-hidden"
                        >
                          {ev.media_type === 'photo' || ev.file_type?.startsWith('image') ? (
                            <img
                              src={ev.file_url}
                              alt={ev.file_name}
                              className="w-full h-24 object-cover"
                              onError={(e) => {
                                (e.target as HTMLImageElement).style.display = 'none';
                              }}
                            />
                          ) : (
                            <div className="w-full h-24 flex items-center justify-center bg-white">
                              <FileText className="w-8 h-8 text-slate-400" />
                            </div>
                          )}
                          <div className="p-2 text-[10px] text-slate-700 truncate">
                            {ev.file_name}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Footer — actions */}
              <div className="px-5 py-3 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-end gap-2">
                {item.status !== 'Completed' && item.status !== 'Verified' && (
                  <button
                    onClick={() => { setSelectedActionForDetail(null); openEvidenceModal(item); }}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-100 hover:bg-amber-200 text-amber-800 inline-flex items-center gap-1.5"
                  >
                    <Upload className="w-3.5 h-3.5" />
                    Upload Evidence
                  </button>
                )}
                {item.status !== 'Completed' && item.status !== 'Verified' && (
                  <button
                    onClick={() => { setSelectedActionForDetail(null); handleMarkCompleted(item); }}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-700 hover:bg-emerald-800 text-white"
                  >
                    Mark Completed
                  </button>
                )}
                {item.status === 'Completed' && (
                  <button
                    onClick={() => { setSelectedActionForDetail(null); handleVerifyClose(item); }}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-700 hover:bg-blue-800 text-white"
                  >
                    Verify & Close
                  </button>
                )}
                {canEditActionMetadata && (
                  <button
                    onClick={() => { setSelectedActionForDetail(null); openEditModal(item); }}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 inline-flex items-center gap-1.5"
                  >
                    <Pencil className="w-3.5 h-3.5" />
                    Edit
                  </button>
                )}
                {currentRole === 'SUPER_ADMIN' && (
                  <button
                    onClick={() => { setSelectedActionForDetail(null); handleDeleteAction(item); }}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-100 hover:bg-rose-200 text-rose-800 inline-flex items-center gap-1.5"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Delete
                  </button>
                )}
                <button
                  onClick={() => setSelectedActionForDetail(null)}
                  className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-100"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        );
      })()}

    </div>
  );
};
