import React, { useState } from 'react';
import { Project, ProjectStatus } from '../../types/index.ts';
import { api } from '../../services/api.ts';
import {
  FolderGit2,
  Plus,
  Search,
  CheckCircle2,
  Clock,
  Activity,
  AlertTriangle,
  Eye,
  MapPin,
  TrendingUp,
  DollarSign,
  Pencil,
  Trash2
} from 'lucide-react';

interface ProjectListProps {
  projects?: Project[];
  onSelectProject: (project: Project) => void;
  onOpenCreateModal?: () => void;
  onNewProjectClick?: () => void;
  states?: string[];
  statesAndLgas?: Record<string, string[]>;
  categories?: string[];
  currentUser?: { role?: string; name?: string } | null;
  onRefresh?: () => Promise<void> | void;
  onEditProject?: (project: Project) => void;
  onDeleteProject?: (project: Project) => Promise<void> | void;
}

export const ProjectList: React.FC<ProjectListProps> = ({
  projects = [],
  onSelectProject,
  onOpenCreateModal,
  onNewProjectClick,
  states,
  statesAndLgas,
  categories = [],
  currentUser,
  onRefresh,
  onEditProject,
  onDeleteProject
}) => {

  // --- Project approval ---
  const [approvalBusyId, setApprovalBusyId] = useState<string | null>(null);
  const currentRole = currentUser?.role || '';
  const canApproveProject = currentRole === 'SUPER_ADMIN' || currentRole === 'EXECUTIVE';
  const canEditDelete = currentRole === 'SUPER_ADMIN' || currentRole === 'EXECUTIVE';

  const handleApproveProject = async (id: string) => {
    const notes = window.prompt('Approval notes (optional):', 'Contract awarded.');
    if (notes === null) return;
    const amountStr = window.prompt('Approved amount (NGN, optional):', '');
    const amount = amountStr ? parseFloat(amountStr) : undefined;
    setApprovalBusyId(id);
    try {
      await api.executiveApproveProject(id, notes, amount);
      await onRefresh?.();
    } catch (err: any) {
      alert(`Project approval failed: ${err.message}`);
    } finally {
      setApprovalBusyId(null);
    }
  };

  const handleEditClick = (proj: Project, e: React.MouseEvent) => {
    e.stopPropagation();
    if (onEditProject) onEditProject(proj);
  };

  const handleDeleteClick = async (proj: Project, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!onDeleteProject) return;
    const confirmed = window.confirm(
      `Delete project ${proj.id}?\n\n"${proj.title}"\n\nThis cannot be undone and will be recorded in the audit log.`
    );
    if (!confirmed) return;
    await onDeleteProject(proj);
  };

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedState, setSelectedState] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');

  // Derive filter options from actual project data so nothing is ever missing
  const availableStatuses = Array.from(
    new Set(projects.map(p => p.status).filter(Boolean) as string[])
  ).sort((a, b) => {
    // Custom order: Active first, then Pending Approval, then others alphabetically
    const order = ['Active', 'Pending Approval', 'Procurement', 'Delayed', 'Suspended', 'Completed', 'Rejected', 'Cancelled', 'Proposed'];
    const ai = order.indexOf(a);
    const bi = order.indexOf(b);
    if (ai !== -1 && bi !== -1) return ai - bi;
    if (ai !== -1) return -1;
    if (bi !== -1) return 1;
    return a.localeCompare(b);
  });

  const availableStates = Array.from(
    new Set(projects.map(p => p.state).filter(Boolean) as string[])
  ).sort();

  const availableCategories = Array.from(
    new Set(projects.map(p => p.category).filter(Boolean) as string[])
  ).sort();

  const [selectedCategory, setSelectedCategory] = useState('');

  const stateList = states || Object.keys(statesAndLgas || {});
  const categoryList = categories || [];
  const handleOpenCreate = onOpenCreateModal || onNewProjectClick || (() => {});

  const filtered = (projects || []).filter(p => {
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      const match =
        p.title.toLowerCase().includes(q) ||
        p.id.toLowerCase().includes(q) ||
        p.contractor.toLowerCase().includes(q) ||
        p.community.toLowerCase().includes(q) ||
        p.state.toLowerCase().includes(q);
      if (!match) return false;
    }
    if (selectedState && p.state !== selectedState) return false;
    if (selectedStatus && p.status !== selectedStatus) return false;
    if (selectedCategory && p.category !== selectedCategory) return false;
    return true;
  });

  const getStatusBadge = (status: ProjectStatus) => {
    switch (status) {
      case 'Active':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'Completed':
        return 'bg-teal-100 text-teal-800 border-teal-300';
      case 'Delayed':
        return 'bg-rose-100 text-rose-800 border-rose-300';
      case 'Suspended':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'Procurement':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  return (
    <div id="projects-list-module" className="space-y-4">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">Edo State Ecological Projects Register</h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              {(projects || []).length} Projects
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Module 3: Edo State infrastructure contracts, civil engineering remediation works, and progress tracking.
          </p>
        </div>

        <button
          id="btn-create-project"
          onClick={handleOpenCreate}
          className="px-3.5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white transition-colors shadow-xs inline-flex items-center cursor-pointer"
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Create New Project
        </button>
      </div>

      {/* Filter toolbar */}
      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs flex flex-wrap gap-2 text-xs">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search project title, contractor, ID, state..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white text-xs"
          />
        </div>

        <select
          value={selectedState}
          onChange={e => setSelectedState(e.target.value)}
          className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white text-xs"
        >
          <option value="">All States ({stateList.length})</option>
          {stateList.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        <select
          value={selectedStatus}
          onChange={e => setSelectedStatus(e.target.value)}
          className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white text-xs"
        >
          <option value="">All Statuses</option>
          {availableStatuses.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
          <option value="Suspended">Suspended</option>
          <option value="Proposed">Proposed</option>
        </select>

        <select
          value={selectedCategory}
          onChange={e => setSelectedCategory(e.target.value)}
          className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white text-xs"
        >
          <option value="">All Categories</option>
          {categoryList.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Project Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(proj => (
          <div
            key={proj.id}
            id={`project-card-${proj.id}`}
            onClick={() => onSelectProject(proj)}
            className="relative bg-white rounded-xl border border-slate-200 shadow-xs hover:shadow-md hover:border-emerald-500 cursor-pointer transition-all p-4 flex flex-col justify-between"
          >
            {/* Edit / Delete icons — Super Admin + Executive only */}
            {canEditDelete && (
              <div
                className="absolute top-2 right-2 flex items-center gap-1 z-10"
                onClick={(e) => e.stopPropagation()}
              >
                <button
                  onClick={(e) => handleEditClick(proj, e)}
                  title="Edit project"
                  className="p-1 rounded bg-white/90 hover:bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200 shadow-xs"
                >
                  <Pencil className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={(e) => handleDeleteClick(proj, e)}
                  title="Delete project"
                  className="p-1 rounded bg-white/90 hover:bg-rose-100 text-rose-700 border border-slate-200 shadow-xs"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            <div>
              <div className="flex items-start justify-between pr-14">
                <div>
                  <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                    {proj.id}
                  </span>
                  <span className={`ml-2 inline-block px-2 py-0.5 rounded text-[10px] border font-semibold ${getStatusBadge(proj.status)}`}>
                    {proj.status}
                  </span>
                </div>
                <span className="text-[11px] text-slate-400 font-mono">
                  {proj.category}
                </span>
              </div>

              <h3 className="font-bold text-slate-900 text-sm mt-2 line-clamp-2" title={proj.title}>
                {proj.title}
              </h3>

              <div className="mt-2 space-y-1 text-xs text-slate-600">
                <div className="flex items-center text-[11px]">
                  <MapPin className="w-3.5 h-3.5 mr-1 text-emerald-600 shrink-0" />
                  <span className="truncate">{proj.community}, {proj.lga}, <strong>{proj.state}</strong></span>
                </div>
                <div className="text-[11px] text-slate-500 truncate">
                  Contractor: <span className="font-semibold text-slate-800">{proj.contractor}</span>
                </div>
              </div>
            </div>

            {/* Progress and budget footer */}
            <div className="mt-4 pt-3 border-t border-slate-100 space-y-2 text-xs">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Physical Progress:</span>
                <span className="font-bold text-emerald-800">
                  {proj.actual_percentage}% <span className="text-slate-400 font-normal">(Planned: {proj.planned_percentage}%)</span>
                </span>
              </div>

              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden relative">
                <div
                  className="h-full bg-emerald-600 rounded-full transition-all duration-300"
                  style={{ width: `${proj.actual_percentage}%` }}
                ></div>
              </div>

              <div className="flex items-center justify-between pt-1 text-[11px]">
                <span className="text-slate-500">Contract Value:</span>
                <span className="font-bold text-slate-900 font-mono">
                  ₦{(proj.contract_amount_ngn / 1e6).toFixed(1)}M
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};