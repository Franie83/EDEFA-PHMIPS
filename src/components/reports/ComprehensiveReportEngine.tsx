import React, { useState } from 'react';
import { ComprehensiveReportData, ReferenceData } from '../../types/index.ts';
import { api } from '../../services/api.ts';
import {
  FileSpreadsheet,
  Download,
  Printer,
  FileText,
  Filter,
  CheckCircle,
  AlertTriangle,
  Building,
  Calendar,
  Share2,
  RefreshCw
} from 'lucide-react';
import * as XLSX from 'xlsx';

interface ComprehensiveReportEngineProps {
  referenceData: ReferenceData | null;
}

export const ComprehensiveReportEngine: React.FC<ComprehensiveReportEngineProps> = ({
  referenceData
}) => {
  const [reportData, setReportData] = useState<ComprehensiveReportData | null>(null);
  const [loading, setLoading] = useState(false);

  // Filter criteria
  const [filters, setFilters] = useState({
    title: 'Edo State Comprehensive Ecological Hazard, Intervention & Planning Report',
    state: 'Edo',
    lga: '',
    category: '',
    severity: '',
    prepared_by: 'Engr. Director of Ecological Hazard Management & GIS',
    reviewed_by: 'Permanent Secretary, Edo State Ministry of Environment',
    approved_by: 'Executive Governor / Chairman, Edo State Ecological Fund Agency'
  });

  const generateReport = async () => {
    setLoading(true);
    try {
      const data = await api.generateComprehensiveReport(filters);
      setReportData(data);
    } catch (e: any) {
      alert(`Report generation failed: ${e.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  // Export to Excel (.xlsx) using xlsx library
  const exportToExcel = () => {
    if (!reportData) return;

    // Sheet 1: Detailed Hazard Register
    const hazardRegisterRows = reportData.detailed_hazard_register.map(h => ({
      'Hazard ID': h.hazard_id,
      'Title': h.title,
      'Category': h.category,
      'State': h.state,
      'LGA': h.lga,
      'Community': h.community,
      'Coordinates': h.coordinates,
      'Date Reported': h.date_reported,
      'Reporter': h.reporter,
      'Verification Status': h.verification_status,
      'Verified By': h.verified_by,
      'Severity': h.severity,
      'Priority Score': h.priority_score,
      'Potential Impact': h.potential_impact,
      'Recommended Intervention': h.recommended_intervention,
      'Estimated Cost (NGN)': h.estimated_cost_ngn,
      'Responsible Authority': h.responsible_authority
    }));

    // Sheet 2: Interventions Pipeline
    const interventionRows = reportData.intervention_recommendations.map(i => ({
      'Hazard ID': i.hazard_id,
      'Recommended Intervention': i.recommended_intervention,
      'Priority': i.priority,
      'Estimated Cost (NGN)': i.estimated_cost_ngn,
      'Responsible Organization': i.responsible_organization,
      'Timeline': i.expected_timeline
    }));

    // Sheet 3: Executive Summary Stats
    const summaryRows = [
      { Metric: 'Total Reports', Value: reportData.executive_summary_stats.totalReports },
      { Metric: 'Verified Reports', Value: reportData.executive_summary_stats.verifiedReports },
      { Metric: 'Critical Hazards', Value: reportData.executive_summary_stats.criticalHazards },
      { Metric: 'High Hazards', Value: reportData.executive_summary_stats.highHazards },
      { Metric: 'Requiring Intervention', Value: reportData.executive_summary_stats.requiringIntervention },
      { Metric: 'Total Pipeline Budget (NGN)', Value: reportData.planning_analysis.total_estimated_pipeline_budget_ngn }
    ];

    const wb = XLSX.utils.book_new();
    const wsRegister = XLSX.utils.json_to_sheet(hazardRegisterRows);
    const wsInterventions = XLSX.utils.json_to_sheet(interventionRows);
    const wsSummary = XLSX.utils.json_to_sheet(summaryRows);

    XLSX.utils.book_append_sheet(wb, wsSummary, 'Executive Summary');
    XLSX.utils.book_append_sheet(wb, wsRegister, 'Hazard Register');
    XLSX.utils.book_append_sheet(wb, wsInterventions, 'Intervention Pipeline');

    XLSX.writeFile(wb, `EF_PHMIPS_Report_${new Date().toISOString().split('T')[0]}.xlsx`);
  };

  // Export to CSV
  const exportToCSV = () => {
    if (!reportData) return;
    const rows = reportData.detailed_hazard_register.map(h => ({
      Hazard_ID: h.hazard_id,
      Title: h.title,
      Category: h.category,
      State: h.state,
      LGA: h.lga,
      Community: h.community,
      Severity: h.severity,
      Estimated_Cost_NGN: h.estimated_cost_ngn
    }));
    const ws = XLSX.utils.json_to_sheet(rows);
    const csv = XLSX.utils.sheet_to_csv(ws);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `EF_PHMIPS_Register_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div id="comprehensive-reports-module" className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">Edo State Ecological Hazard, Intervention & Planning Report</h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              Module 12 Engine
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Generates standardized statutory briefs for the Executive Governor of Edo State, State Executive Council (EXCO), and Edo State House of Assembly.
          </p>
        </div>

        {reportData && (
          <div className="flex items-center space-x-2">
            <button
              onClick={() => window.print()}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 inline-flex items-center shadow-xs"
            >
              <Printer className="w-4 h-4 mr-1 text-slate-500" />
              Print / Save PDF
            </button>
            <button
              onClick={exportToExcel}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-800 text-white hover:bg-emerald-900 inline-flex items-center shadow-xs"
            >
              <FileSpreadsheet className="w-4 h-4 mr-1 text-emerald-300" />
              Export Excel (.xlsx)
            </button>
            <button
              onClick={exportToCSV}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-white hover:bg-slate-900 inline-flex items-center shadow-xs"
            >
              <Download className="w-4 h-4 mr-1" />
              CSV
            </button>
          </div>
        )}
      </div>

      {/* Filter Parameters Form */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3 text-xs">
        <div className="font-bold text-slate-800 uppercase tracking-wider text-[11px]">
          Configure Reporting Scope & Parameters
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          <div className="sm:col-span-2">
            <label className="block font-semibold mb-1 text-slate-700">Report Title Header</label>
            <input
              type="text"
              value={filters.title}
              onChange={e => setFilters({ ...filters, title: e.target.value })}
              className="w-full p-2 border rounded-lg"
            />
          </div>

          <div>
            <label className="block font-semibold mb-1 text-slate-700">Geographic State Scope</label>
            <select
              value={filters.state}
              onChange={e => setFilters({ ...filters, state: e.target.value })}
              className="w-full p-2 border rounded-lg bg-white"
            >
              <option value="">Statewide (All Edo LGAs)</option>
              {referenceData && Object.keys(referenceData.states_and_lgas).map(st => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold mb-1 text-slate-700">Ecological Hazard Category</label>
            <select
              value={filters.category}
              onChange={e => setFilters({ ...filters, category: e.target.value })}
              className="w-full p-2 border rounded-lg bg-white"
            >
              <option value="">All Categories</option>
              {referenceData?.hazard_categories.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold mb-1 text-slate-700">Prepared By</label>
            <input
              type="text"
              value={filters.prepared_by}
              onChange={e => setFilters({ ...filters, prepared_by: e.target.value })}
              className="w-full p-2 border rounded-lg"
            />
          </div>

          <div>
            <label className="block font-semibold mb-1 text-slate-700">Reviewed By</label>
            <input
              type="text"
              value={filters.reviewed_by}
              onChange={e => setFilters({ ...filters, reviewed_by: e.target.value })}
              className="w-full p-2 border rounded-lg"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block font-semibold mb-1 text-slate-700">Approved By (Executive Clearance)</label>
            <input
              type="text"
              value={filters.approved_by}
              onChange={e => setFilters({ ...filters, approved_by: e.target.value })}
              className="w-full p-2 border rounded-lg"
            />
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            onClick={generateReport}
            disabled={loading}
            className="px-5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white inline-flex items-center shadow-xs transition-colors cursor-pointer"
          >
            {loading ? <RefreshCw className="w-4 h-4 mr-1.5 animate-spin" /> : <FileText className="w-4 h-4 mr-1.5 text-amber-300" />}
            {loading ? 'Compiling Edo State Report...' : 'Compile & Generate Edo State Statutory Report'}
          </button>
        </div>
      </div>

      {/* Rendered Document View */}
      {reportData && (
        <div id="printable-report-document" className="bg-white p-8 rounded-xl border border-slate-300 shadow-md text-slate-800 space-y-6 max-w-5xl mx-auto text-xs">
          {/* Document Official Header */}
          <div className="text-center border-b-2 border-emerald-900 pb-4">
            <div className="text-xs font-bold uppercase tracking-widest text-emerald-950 font-serif">
              GOVERNMENT OF EDO STATE, NIGERIA
            </div>
            <div className="text-sm font-black text-emerald-950 uppercase tracking-wider mt-0.5">
              OFFICE OF THE EXECUTIVE GOVERNOR
            </div>
            <div className="text-base font-black text-emerald-800 uppercase tracking-tight mt-1">
              EDO STATE ECOLOGICAL FUND AGENCY (EDEFA)
            </div>
            <h1 className="text-lg font-black text-slate-900 mt-2">{reportData.report_metadata.report_title}</h1>
            <div className="flex items-center justify-center space-x-4 text-[11px] text-slate-500 mt-1">
              <span>Date: {reportData.report_metadata.generated_at}</span>
              <span>•</span>
              <span>Scope: {reportData.report_metadata.reporting_scope.state || 'Edo State'}</span>
            </div>
          </div>

          {/* Section 2: Executive Summary */}
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-emerald-900 mb-2 border-b border-emerald-100 pb-1">
              2. Executive Summary Statistics
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase">Total Registered Hazards</span>
                <strong className="text-xl text-slate-900">{reportData.executive_summary_stats.totalReports}</strong>
              </div>
              <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                <span className="text-[10px] text-emerald-800 block uppercase">Verified Valid</span>
                <strong className="text-xl text-emerald-900">{reportData.executive_summary_stats.verifiedReports}</strong>
              </div>
              <div className="p-3 bg-rose-50 rounded-lg border border-rose-200">
                <span className="text-[10px] text-rose-800 block uppercase">Critical Priority</span>
                <strong className="text-xl text-rose-900">{reportData.executive_summary_stats.criticalHazards}</strong>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                <span className="text-[10px] text-blue-800 block uppercase">Requiring Intervention</span>
                <strong className="text-xl text-blue-900">{reportData.executive_summary_stats.requiringIntervention}</strong>
              </div>
            </div>
          </div>

          {/* Section 3 & 4: Geographic & Category Analysis */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-3.5 rounded-lg border border-slate-200 bg-slate-50">
              <h3 className="font-bold text-slate-900 uppercase text-[11px] mb-2">
                3. Geographic Concentration by State & LGA
              </h3>
              <div className="space-y-1">
                {Object.entries(reportData.geographic_analysis.by_state).map(([st, cnt]) => (
                  <div key={st} className="flex justify-between py-0.5 border-b border-slate-100">
                    <span>{st} State</span>
                    <strong className="font-mono">{cnt} hazards</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3.5 rounded-lg border border-slate-200 bg-slate-50">
              <h3 className="font-bold text-slate-900 uppercase text-[11px] mb-2">
                4. Hazard Classification Breakdown
              </h3>
              <div className="space-y-1">
                {Object.entries(reportData.hazard_category_analysis).map(([cat, info]: [string, any]) => (
                  <div key={cat} className="flex justify-between py-0.5 border-b border-slate-100">
                    <span>{cat}</span>
                    <strong className="font-mono">{info?.count} ({info?.percentage}%)</strong>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Section 6: Comprehensive Detailed Hazard Register Table */}
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-emerald-900 mb-2 border-b border-emerald-100 pb-1">
              6. Detailed National Hazard Register
            </h2>
            <div className="overflow-x-auto border border-slate-200 rounded-lg">
              <table className="w-full text-left text-[11px]">
                <thead className="bg-slate-100 uppercase font-bold text-[10px] text-slate-700">
                  <tr>
                    <th className="p-2">ID</th>
                    <th className="p-2">Title / Category</th>
                    <th className="p-2">Location</th>
                    <th className="p-2">Severity</th>
                    <th className="p-2">Status</th>
                    <th className="p-2">Recommended Intervention</th>
                    <th className="p-2 text-right">Est. Budget (NGN)</th>
                    <th className="p-2 text-center">Photos</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-800">
                  {reportData.detailed_hazard_register.map(h => (
                    <tr key={h.hazard_id} className="hover:bg-slate-50">
                      <td className="p-2 font-mono font-bold text-slate-600">{h.hazard_id}</td>
                      <td className="p-2">
                        <div className="font-bold text-slate-900">{h.title}</div>
                        <div className="text-[10px] text-slate-500">{h.category}</div>
                      </td>
                      <td className="p-2">
                        <div>{h.community}, {h.lga}</div>
                        <div className="text-slate-500">{h.state} ({h.coordinates})</div>
                      </td>
                      <td className="p-2">
                        <span className="font-bold text-rose-700">{h.severity}</span>
                      </td>
                      <td className="p-2">{h.verification_status}</td>
                      <td className="p-2 max-w-xs truncate">{h.recommended_intervention}</td>
                      <td className="p-2 text-right font-mono font-semibold">
                        ₦{(h.estimated_cost_ngn / 1e6).toFixed(1)}M
                      </td>
                      <td className="p-2 text-center">{h.photographs.length}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 8: Planning & Budget Pipeline */}
          <div className="p-4 rounded-lg bg-emerald-50/60 border border-emerald-200 space-y-2">
            <h2 className="text-xs font-bold uppercase tracking-wider text-emerald-950">
              8. Intervention Budget Pipeline & Risk Zones
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
              <div className="p-2 bg-white rounded border border-emerald-100">
                <span className="text-[10px] text-slate-500 block">Immediate Actions</span>
                <strong className="text-base text-slate-900">{reportData.planning_analysis.immediate_intervention_requirements}</strong>
              </div>
              <div className="p-2 bg-white rounded border border-emerald-100">
                <span className="text-[10px] text-slate-500 block">Short-Term Pipeline</span>
                <strong className="text-base text-slate-900">{reportData.planning_analysis.short_term_requirements}</strong>
              </div>
              <div className="p-2 bg-white rounded border border-emerald-100">
                <span className="text-[10px] text-slate-500 block">Medium-Term</span>
                <strong className="text-base text-slate-900">{reportData.planning_analysis.medium_term_requirements}</strong>
              </div>
              <div className="p-2 bg-white rounded border border-emerald-100">
                <span className="text-[10px] text-slate-500 block">Total Pipeline Budget</span>
                <strong className="text-base text-emerald-900 font-mono">
                  ₦{(reportData.planning_analysis.total_estimated_pipeline_budget_ngn / 1e9).toFixed(2)}B
                </strong>
              </div>
            </div>
          </div>

          {/* Section 9: Conclusion */}
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-1">
              9. Technical Conclusion & Statutory Recommendations
            </h2>
            <p className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 leading-relaxed">
              {reportData.conclusion_text}
            </p>
          </div>

          {/* Section 10: Official Sign-Off Block */}
          <div className="pt-6 border-t-2 border-slate-300 grid grid-cols-3 gap-6 text-center text-[11px]">
            <div>
              <div className="border-b border-slate-400 pb-8 mb-1"></div>
              <div className="font-bold text-slate-900">{reportData.sign_off.prepared_by}</div>
              <div className="text-slate-500">Lead Technical Officer (Preparation)</div>
            </div>
            <div>
              <div className="border-b border-slate-400 pb-8 mb-1"></div>
              <div className="font-bold text-slate-900">{reportData.sign_off.reviewed_by}</div>
              <div className="text-slate-500">Director / Permanent Secretary (Review)</div>
            </div>
            <div>
              <div className="border-b border-slate-400 pb-8 mb-1"></div>
              <div className="font-bold text-slate-900">{reportData.sign_off.approved_by}</div>
              <div className="text-slate-500">Executive Authority (Approval)</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
