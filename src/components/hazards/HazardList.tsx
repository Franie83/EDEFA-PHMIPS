import React, { useState } from 'react';
import { Hazard, HazardSeverity, HazardStatus } from '../../types/index.ts';
import {
  Search,
  Filter,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Eye,
  CheckSquare,
  Compass,
  MapPin,
  ChevronDown,
  Layers,
  ArrowUpDown,
  FileDown
} from 'lucide-react';

interface HazardListProps {
  hazards?: Hazard[];
  onSelectHazard: (hazard: Hazard) => void;
  onOpenReportModal?: () => void;
  onOpenVerifyModal?: (hazard: Hazard) => void;
  onOpenAssessModal?: (hazard: Hazard) => void;
  onBulkVerify?: (ids: string[], action: 'VERIFY' | 'INVALIDATE') => void;
  states?: string[];
  statesAndLgas?: Record<string, string[]>;
  categories?: string[];
  onNewReportClick?: () => void;
  onVerifyHazard?: (hazard: Hazard) => void;
}

export const HazardList: React.FC<HazardListProps> = ({
  hazards = [],
  onSelectHazard,
  onOpenReportModal,
  onOpenVerifyModal,
  onOpenAssessModal,
  onBulkVerify,
  states,
  statesAndLgas,
  categories = [],
  onNewReportClick,
  onVerifyHazard
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedState, setSelectedState] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [recurringOnly, setRecurringOnly] = useState(false);

  const stateList = states || Object.keys(statesAndLgas || {});
  const categoryList = categories || [];
  const handleReportClick = onOpenReportModal || onNewReportClick || (() => {});
  const handleVerifyClick = onOpenVerifyModal || onVerifyHazard || onSelectHazard;

  // Filter hazards
  const filtered = (hazards || []).filter(h => {
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      const match =
        h.title.toLowerCase().includes(q) ||
        h.id.toLowerCase().includes(q) ||
        h.community.toLowerCase().includes(q) ||
        h.lga.toLowerCase().includes(q) ||
        h.state.toLowerCase().includes(q) ||
        h.reporter_name.toLowerCase().includes(q);
      if (!match) return false;
    }
    if (selectedState && h.state !== selectedState) return false;
    if (selectedCategory && h.category !== selectedCategory) return false;
    if (selectedSeverity && h.severity !== selectedSeverity) return false;
    if (selectedStatus && h.status !== selectedStatus) return false;
    if (recurringOnly && !h.is_recurring) return false;
    return true;
  });

  const toggleSelectAll = () => {
    if (selectedIds.length === filtered.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filtered.map(h => h.id));
    }
  };

  const toggleSelectOne = (id: string) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(i => i !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const getSeverityBadge = (severity: HazardSeverity) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-rose-100 text-rose-800 border-rose-300 font-bold';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800 border-orange-300 font-semibold';
      case 'MEDIUM':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'LOW':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  const getStatusBadge = (status: HazardStatus) => {
    if (status.includes('Verified')) return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    if (status.includes('Critical') || status.includes('Prioritised')) return 'bg-rose-100 text-rose-800 border-rose-200';
    if (status.includes('Intervention')) return 'bg-blue-100 text-blue-800 border-blue-200';
    if (status.includes('Resolved') || status.includes('Closed')) return 'bg-teal-100 text-teal-800 border-teal-200';
    if (status.includes('Under Review') || status.includes('Assessment')) return 'bg-amber-100 text-amber-800 border-amber-200';
    return 'bg-slate-100 text-slate-700 border-slate-200';
  };

  return (
    <div id="hazards-list-module" className="space-y-4">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">Edo State Ecological Hazard Register</h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              {hazards.length} Records
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Gully erosion, ravine expansion, flash flooding, soil instability, and watershed degradation across Edo State.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {selectedIds.length > 0 && onBulkVerify && (
            <div className="flex items-center space-x-2 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200">
              <span className="text-xs font-semibold text-emerald-900">{selectedIds.length} Selected:</span>
              <button
                onClick={() => onBulkVerify(selectedIds, 'VERIFY')}
                className="px-2.5 py-1 rounded text-xs font-semibold bg-emerald-700 text-white hover:bg-emerald-800"
              >
                Verify Selected
              </button>
              <button
                onClick={() => onBulkVerify(selectedIds, 'INVALIDATE')}
                className="px-2.5 py-1 rounded text-xs font-semibold bg-rose-700 text-white hover:bg-rose-800"
              >
                Mark Invalid
              </button>
            </div>
          )}

          <button
            id="hazards-btn-create-report"
            onClick={handleReportClick}
            className="px-3.5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white transition-colors shadow-xs inline-flex items-center cursor-pointer"
          >
            <AlertTriangle className="w-4 h-4 mr-1.5 text-amber-300" />
            Report New Hazard
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2.5 text-xs">
          {/* Search bar */}
          <div className="relative sm:col-span-2">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search title, ID, LGA, community, reporter..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white focus:outline-hidden focus:ring-1 focus:ring-emerald-600 text-xs"
            />
          </div>

          {/* State filter */}
          <select
            value={selectedState}
            onChange={e => setSelectedState(e.target.value)}
            className="py-2 px-2.5 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white text-xs"
          >
            <option value="">All States ({stateList.length})</option>
            {stateList.map(st => (
              <option key={st} value={st}>{st}</option>
            ))}
          </select>

          {/* Category filter */}
          <select
            value={selectedCategory}
            onChange={e => setSelectedCategory(e.target.value)}
            className="py-2 px-2.5 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white text-xs"
          >
            <option value="">All Categories</option>
            {categoryList.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>

          {/* Severity filter */}
          <select
            value={selectedSeverity}
            onChange={e => setSelectedSeverity(e.target.value)}
            className="py-2 px-2.5 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white text-xs"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>

          {/* Status filter */}
          <select
            value={selectedStatus}
            onChange={e => setSelectedStatus(e.target.value)}
            className="py-2 px-2.5 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white text-xs"
          >
            <option value="">All Statuses</option>
            <option value="Submitted">Submitted (Unverified)</option>
            <option value="Under Review">Under Review</option>
            <option value="Verified">Verified</option>
            <option value="Prioritised">Prioritised</option>
            <option value="Intervention Planned">Intervention Planned</option>
            <option value="Intervention Ongoing">Intervention Ongoing</option>
            <option value="Resolved">Resolved</option>
          </select>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs text-slate-500">
          <label className="inline-flex items-center space-x-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={recurringOnly}
              onChange={e => setRecurringOnly(e.target.checked)}
              className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
            />
            <span>Show only recurring hazard hotspots (history &gt; 1 occurrence)</span>
          </label>

          <span>Showing {filtered.length} of {hazards.length} hazards</span>
        </div>
      </div>

      {/* Hazards Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-bold text-[11px]">
              <tr>
                <th className="p-3 w-8">
                  <input
                    type="checkbox"
                    checked={filtered.length > 0 && selectedIds.length === filtered.length}
                    onChange={toggleSelectAll}
                    className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                  />
                </th>
                <th className="p-3">ID / Title</th>
                <th className="p-3">Category</th>
                <th className="p-3">Location (State/LGA/Community)</th>
                <th className="p-3">Severity & Urgency</th>
                <th className="p-3">Status</th>
                <th className="p-3">Reported</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-slate-400">
                    No ecological hazard reports match the selected criteria.
                  </td>
                </tr>
              ) : (
                filtered.map(h => (
                  <tr
                    key={h.id}
                    id={`hazard-row-${h.id}`}
                    className="hover:bg-slate-50/80 transition-colors"
                  >
                    <td className="p-3">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(h.id)}
                        onChange={() => toggleSelectOne(h.id)}
                        className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                      />
                    </td>
                    <td className="p-3 font-medium">
                      <div className="flex items-center space-x-1.5">
                        <span className="font-mono text-[11px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                          {h.id}
                        </span>
                        {h.is_recurring && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                            Recurring ({h.recurring_count}x)
                          </span>
                        )}
                      </div>
                      <div
                        onClick={() => onSelectHazard(h)}
                        className="font-bold text-slate-900 mt-1 cursor-pointer hover:text-emerald-700 hover:underline max-w-sm truncate"
                        title={h.title}
                      >
                        {h.title}
                      </div>
                      <div className="text-[11px] text-slate-500 truncate max-w-xs">{h.hazard_type}</div>
                    </td>
                    <td className="p-3">
                      <span className="inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-medium">
                        {h.category}
                      </span>
                    </td>
                    <td className="p-3">
                      <div className="font-semibold text-slate-900">{h.community}, {h.lga}</div>
                      <div className="text-[11px] text-emerald-800 font-medium">{h.state} State</div>
                      <div className="text-[10px] text-slate-400 font-mono">
                        {h.latitude.toFixed(4)}, {h.longitude.toFixed(4)}
                      </div>
                    </td>
                    <td className="p-3">
                      <div className="flex flex-col space-y-1">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] border w-max ${getSeverityBadge(h.severity)}`}>
                          {h.severity}
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono">
                          Urgency: {h.urgency}
                        </span>
                      </div>
                    </td>
                    <td className="p-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium border ${getStatusBadge(h.status)}`}>
                        {h.status}
                      </span>
                      {h.assessment && (
                        <div className="text-[10px] text-slate-500 mt-0.5">
                          Score: {h.assessment.calculated_priority_score}/100
                        </div>
                      )}
                    </td>
                    <td className="p-3">
                      <div className="text-slate-700">{h.date_reported}</div>
                      <div className="text-[11px] text-slate-400 truncate max-w-[120px]">{h.reporter_name}</div>
                    </td>
                    <td className="p-3 text-right">
                      <div className="flex items-center justify-end space-x-1">
                        <button
                          onClick={() => onSelectHazard(h)}
                          className="p-1.5 rounded hover:bg-slate-200 text-slate-600 hover:text-slate-900"
                          title="View Full Dossier"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {h.status === 'Submitted' && (
                          <button
                            onClick={() => handleVerifyClick(h)}
                            className="p-1.5 rounded hover:bg-emerald-100 text-emerald-700 font-medium"
                            title="Perform Verification"
                          >
                            <CheckSquare className="w-4 h-4" />
                          </button>
                        )}
                        {(h.status === 'Verified' || h.status === 'Assessment Required') && (
                          <button
                            onClick={() => (onOpenAssessModal || onSelectHazard)(h)}
                            className="p-1.5 rounded hover:bg-amber-100 text-amber-700 font-medium"
                            title="Technical Assessment & Scoring"
                          >
                            <Compass className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};