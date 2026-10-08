import React, { useState } from 'react';
import { AuditLog } from '../../types/index.ts';
import {
  ShieldAlert,
  Search,
  Filter,
  Calendar,
  User,
  Clock,
  FileCode,
  CheckCircle2
} from 'lucide-react';

interface AuditLogsModuleProps {
  logs: AuditLog[];
}

export const AuditLogsModule: React.FC<AuditLogsModuleProps> = ({ logs = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [actionFilter, setActionFilter] = useState<string>('ALL');

  const filtered = (logs || []).filter(log => {
    if (actionFilter !== 'ALL' && !log.action.includes(actionFilter)) return false;
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      return (
        log.action.toLowerCase().includes(q) ||
        log.performed_by.toLowerCase().includes(q) ||
        log.details.toLowerCase().includes(q) ||
        log.entity_id.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div id="audit-logs-module" className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">State Audit Trail & Governance Logs</h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              {logs.length} Immutable Entries
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Module 14: Tamper-evident compliance tracking for all user interactions, verifications, status changes, and budget approvals.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs flex flex-wrap gap-2 text-xs">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by action, user, entity ID, or details..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white text-xs"
          />
        </div>

        <select
          value={actionFilter}
          onChange={e => setActionFilter(e.target.value)}
          className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white text-xs"
        >
          <option value="ALL">All Actions</option>
          <option value="REPORT">Report Created</option>
          <option value="VERIFY">Verification Actions</option>
          <option value="PROJECT">Project Changes</option>
          <option value="INTERVENTION">Intervention Approvals</option>
        </select>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden text-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-100 uppercase font-bold text-[10px] text-slate-700 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Entity</th>
                <th className="py-3 px-4">Performed By & Role</th>
                <th className="py-3 px-4">Audit Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {filtered.map(log => (
                <tr key={log.id} className="hover:bg-slate-50/80">
                  <td className="py-2.5 px-4 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="py-2.5 px-4 font-semibold text-slate-900">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-800">
                      {log.action}
                    </span>
                  </td>
                  <td className="py-2.5 px-4">
                    <span className="font-mono text-emerald-800 font-bold">{log.entity_id}</span>
                    <span className="text-slate-400 text-[10px] block uppercase">{log.entity_type}</span>
                  </td>
                  <td className="py-2.5 px-4">
                    <strong className="text-slate-900">{log.performed_by}</strong>
                    <span className="text-slate-500 block text-[10px]">{log.user_role}</span>
                  </td>
                  <td className="py-2.5 px-4 max-w-md text-slate-600 leading-relaxed">
                    {log.details}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
