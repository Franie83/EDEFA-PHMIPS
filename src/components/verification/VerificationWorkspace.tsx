import React, { useState, useEffect } from 'react';
import { Hazard, HazardSeverity, ReferenceData } from '../../types/index.ts';
import {
  CheckSquare,
  Compass,
  AlertTriangle,
  Scale,
  DollarSign,
  Calendar,
  Building,
  CheckCircle,
  XCircle,
  Send,
  Sliders,
  Info
} from 'lucide-react';

interface VerificationWorkspaceProps {
  hazards: Hazard[];
  referenceData: ReferenceData | null;
  onVerify: (hazardId: string, is_valid: boolean, notes: string, requestInspection: boolean) => Promise<void>;
  onAssess: (hazardId: string, assessmentData: any) => Promise<void>;
  onRecommendIntervention: (hazardId: string, interventionData: any) => Promise<void>;
  onSelectHazard: (hazard: Hazard) => void;
  initialHazardId?: string;                       // ← NEW
}

export const VerificationWorkspace: React.FC<VerificationWorkspaceProps> = ({
  hazards,
  referenceData,
  onVerify,
  onAssess,
  onRecommendIntervention,
  onSelectHazard,
  initialHazardId                                 // ← NEW
}) => {
  const [selectedHazardId, setSelectedHazardId] = useState<string>(
    initialHazardId || hazards[0]?.id || ''       // ← was: hazards[0]?.id || ''
  );
  const [activeTab, setActiveTab] = useState<'VERIFICATION' | 'ASSESSMENT' | 'INTERVENTION'>('VERIFICATION');

  // If the parent supplies a new initial hazard (e.g. from "Perform Verification"
  // on a register row), jump to it.                          ← NEW block
  useEffect(() => {
    if (initialHazardId && initialHazardId !== selectedHazardId) {
      setSelectedHazardId(initialHazardId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialHazardId]);

  const selectedHazard = hazards.find(h => h.id === selectedHazardId) || hazards[0];

  // Determine the hazard's current workflow stage from its data
  const stageOf = (hz: any): 'VERIFICATION' | 'ASSESSMENT' | 'INTERVENTION' | 'DONE' => {
    if (!hz) return 'VERIFICATION';
    if (hz.recommended_intervention || hz.intervention) return 'DONE';
    if (hz.assessment) return 'INTERVENTION';
    if (hz.verified_by) return 'ASSESSMENT';
    return 'VERIFICATION';
  };

  // Auto-advance to the correct tab when the hazard changes
  useEffect(() => {
    const s = stageOf(selectedHazard);
    if (s !== 'DONE') setActiveTab(s);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedHazard?.id, selectedHazard?.verified_by, selectedHazard?.assessment, selectedHazard?.recommended_intervention]);

  const stage = stageOf(selectedHazard);
  const stageLabel: Record<string, string> = {
    VERIFICATION: 'Awaiting Verification',
    ASSESSMENT: 'Verified — ready for Risk Assessment',
    INTERVENTION: 'Assessed — ready for Intervention Formulation',
    DONE: 'Intervention Approved — workflow complete',
  };

  // Verification Form State
  const [isValid, setIsValid] = useState(true);
  const [verificationNotes, setVerificationNotes] = useState('');
  const [requestInspection, setRequestInspection] = useState(true);
  const [isVerifying, setIsVerifying] = useState(false);

  // Assessment Form State
  const [severityScore, setSeverityScore] = useState(8);
  const [urgencyScore, setUrgencyScore] = useState(8);
  const [exposureScore, setExposureScore] = useState(7);
  const [impactScore, setImpactScore] = useState(8);
  const [escalationScore, setEscalationScore] = useState(8);
  const [environmentalImpact, setEnvironmentalImpact] = useState('Severe soil loss and river siltation downstream');
  const [economicImpact, setEconomicImpact] = useState('Direct threat to 14 commercial and residential properties');
  const [socialImpact, setSocialImpact] = useState('Risk to primary school access road; 800 pupils affected');
  const [technicalFindings, setTechnicalFindings] = useState('Unconsolidated sandy-clay soil with high runoff velocity causing headward collapse.');
  const [recommendedInterventionType, setRecommendedInterventionType] = useState('Structural Gully Control Works');
  const [isAssessing, setIsAssessing] = useState(false);

  // Intervention Formulation State
  const [interventionTitle, setInterventionTitle] = useState('');
  const [interventionScope, setInterventionScope] = useState('');
  const [estimatedCost, setEstimatedCost] = useState(350000000);
  const [proposedFunding, setProposedFunding] = useState('Federal Ecological Fund');
  const [responsibleDepartment, setResponsibleDepartment] = useState('Soil Erosion and Flood Control Department');
  const [responsibleOfficer, setResponsibleOfficer] = useState('Engr. Chidi Okafor');
  const [proposedStartDate, setProposedStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [proposedCompletionDate, setProposedCompletionDate] = useState('2026-12-31');
  const [expectedOutcome, setExpectedOutcome] = useState('Total stabilization of 1.2km ravine, construction of concrete chutes, and re-vegetation.');
  const [isSavingIntervention, setIsSavingIntervention] = useState(false);

  // Calculate Priority Score dynamically based on weights
  const weights = referenceData?.priority_weights || {
    severity_weight: 0.25,
    urgency_weight: 0.20,
    exposure_weight: 0.20,
    impact_weight: 0.20,
    escalation_weight: 0.15,
    critical_threshold: 80,
    high_threshold: 65,
    medium_threshold: 45
  };

  const calculatedPriorityScore = Math.round(
    (severityScore * 10 * weights.severity_weight) +
    (urgencyScore * 10 * weights.urgency_weight) +
    (exposureScore * 10 * weights.exposure_weight) +
    (impactScore * 10 * weights.impact_weight) +
    (escalationScore * 10 * weights.escalation_weight)
  );

  let calculatedPriority: HazardSeverity = 'LOW';
  if (calculatedPriorityScore >= weights.critical_threshold) calculatedPriority = 'CRITICAL';
  else if (calculatedPriorityScore >= weights.high_threshold) calculatedPriority = 'HIGH';
  else if (calculatedPriorityScore >= weights.medium_threshold) calculatedPriority = 'MEDIUM';

  const handleVerifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHazard) return;
    setIsVerifying(true);
    try {
      await onVerify(selectedHazard.id, isValid, verificationNotes, requestInspection);
      setActiveTab('ASSESSMENT');
    } catch (e: any) {
      alert(e.message || 'Verification error');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleAssessSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHazard) return;
    setIsAssessing(true);
    try {
      await onAssess(selectedHazard.id, {
        severity_score: severityScore,
        urgency_score: urgencyScore,
        exposure_score: exposureScore,
        impact_score: impactScore,
        escalation_risk_score: escalationScore,
        calculated_priority_score: calculatedPriorityScore,
        recommended_priority: calculatedPriority,
        environmental_impact: environmentalImpact,
        economic_impact: economicImpact,
        social_impact: socialImpact,
        technical_findings: technicalFindings,
        recommended_intervention_type: recommendedInterventionType
      });
      // Prepopulate intervention title
      setInterventionTitle(`Remediation & Control of ${selectedHazard.title}`);
      setInterventionScope(technicalFindings);
      setActiveTab('INTERVENTION');
    } catch (e: any) {
      alert(e.message || 'Assessment error');
    } finally {
      setIsAssessing(false);
    }
  };

  const handleInterventionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHazard) return;
    setIsSavingIntervention(true);
    try {
      await onRecommendIntervention(selectedHazard.id, {
        title: interventionTitle || `Remediation of ${selectedHazard.title}`,
        scope_description: interventionScope,
        estimated_cost_ngn: estimatedCost,
        proposed_funding: proposedFunding,
        responsible_department: responsibleDepartment,
        responsible_officer: responsibleOfficer,
        proposed_start_date: proposedStartDate,
        proposed_completion_date: proposedCompletionDate,
        expected_outcome: expectedOutcome
      });
      alert('Intervention recommendation saved to national planning pipeline.');
    } catch (e: any) {
      alert(e.message || 'Intervention formulation error');
    } finally {
      setIsSavingIntervention(false);
    }
  };

  return (
    <div id="verification-workspace-module" className="space-y-4">
      {/* Title */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Technical Verification & Assessment Workspace</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Module 8: Multi-criteria risk scoring, technical validation, and intervention pipeline formulation.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column: Hazard Selector */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs h-[750px] flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Hazard Queue ({hazards.length})
            </h3>
            <span className="text-[11px] text-slate-400">Select to evaluate</span>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-slate-100 pt-2 space-y-1">
            {hazards.map(h => {
              const isSelected = selectedHazard?.id === h.id;
              return (
                <div
                  key={h.id}
                  id={`verify-queue-${h.id}`}
                  onClick={() => {
                    setSelectedHazardId(h.id);
                    if (h.assessment) {
                      setSeverityScore(h.assessment.severity_score);
                      setUrgencyScore(h.assessment.urgency_score);
                      setExposureScore(h.assessment.exposure_score);
                      setImpactScore(h.assessment.impact_score);
                      setEscalationScore(h.assessment.escalation_risk_score);
                    }
                  }}
                  className={`p-3 rounded-lg cursor-pointer transition-colors text-xs ${
                    isSelected
                      ? 'bg-emerald-50 border border-emerald-300 text-emerald-950 font-medium'
                      : 'hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[10px] text-slate-500">{h.id}</span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700">
                      {h.status}
                    </span>
                  </div>
                  <div className="font-bold text-slate-900 mt-1 truncate">{h.title}</div>
                  <div className="text-[11px] text-slate-500 mt-0.5">{h.community}, {h.state}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right column: 3-step Workflow (Verification, Assessment, Intervention) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-xs flex flex-col">
          {/* Active Record Preview & Tabs */}
          {selectedHazard && (
            <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded">
                    {selectedHazard.id}
                  </span>
                  <span className="font-bold text-xs text-slate-700 uppercase">{selectedHazard.category}</span>
                </div>
                <h3 className="text-sm font-bold text-slate-900 mt-1">{selectedHazard.title}</h3>
                <p className="text-[11px] text-slate-500">{selectedHazard.community}, {selectedHazard.lga}, {selectedHazard.state}</p>
              </div>

              {/* Workflow Step Tabs */}
              <div className="flex items-center space-x-1 bg-slate-200/80 p-1 rounded-lg text-xs font-semibold">
                <button
                  onClick={() => setActiveTab('VERIFICATION')}
                  className={`px-3 py-1.5 rounded-md transition-colors ${
                    activeTab === 'VERIFICATION' ? 'bg-white text-emerald-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  1. Verification
                </button>
                <button
                  onClick={() => setActiveTab('ASSESSMENT')}
                  className={`px-3 py-1.5 rounded-md transition-colors ${
                    activeTab === 'ASSESSMENT' ? 'bg-white text-emerald-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  2. Risk Assessment
                </button>
                <button
                  onClick={() => setActiveTab('INTERVENTION')}
                  className={`px-3 py-1.5 rounded-md transition-colors ${
                    activeTab === 'INTERVENTION' ? 'bg-white text-emerald-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  3. Formulation
                </button>
              </div>
            </div>
          )}

          {/* Stage banner */}
          {selectedHazard && (
            <div className={`mx-6 mt-4 rounded-xl border px-4 py-3 text-xs flex items-center justify-between ${
              stage === 'VERIFICATION' ? 'bg-amber-50 border-amber-200 text-amber-900' :
              stage === 'ASSESSMENT' ? 'bg-blue-50 border-blue-200 text-blue-900' :
              stage === 'INTERVENTION' ? 'bg-purple-50 border-purple-200 text-purple-900' :
              'bg-emerald-50 border-emerald-200 text-emerald-900'
            }`}>
              <div className="flex items-center gap-2">
                <Info className="w-4 h-4 shrink-0" />
                <span className="font-semibold">{stageLabel[stage]}</span>
              </div>
              {stage === 'DONE' && (
                <span className="font-mono text-[11px] opacity-80">
                  Intervention: {(selectedHazard as any)?.recommended_intervention?.intervention_id || (selectedHazard as any)?.intervention?.id || '—'}
                </span>
              )}
            </div>
          )}

          {/* Tab 1: Verification Form */}
          {activeTab === 'VERIFICATION' && selectedHazard && (
            <form onSubmit={handleVerifySubmit} className="p-6 space-y-5 text-xs text-slate-700 flex-1 overflow-y-auto">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-2">
                  Technical Validity Determination
                </h4>
                <p className="text-slate-500 mb-4">
                  Review the report and determine whether this represents a bona-fide ecological hazard within the statutory mandate of the Edo State Ecological Fund Agency (EDEFA).
                </p>

                <div className="grid grid-cols-2 gap-4 max-w-md">
                  <label
                    className={`border rounded-xl p-4 cursor-pointer flex items-center space-x-3 transition-colors ${
                      isValid ? 'border-emerald-600 bg-emerald-50 text-emerald-950 font-bold' : 'border-slate-200'
                    }`}
                  >
                    <input
                      type="radio"
                      name="validity"
                      checked={isValid}
                      onChange={() => setIsValid(true)}
                      className="text-emerald-600"
                    />
                    <div>
                      <CheckCircle className="w-5 h-5 text-emerald-600 mb-1" />
                      <div>Verified Valid Hazard</div>
                      <div className="text-[10px] text-slate-500 font-normal">Authentic ecological threat</div>
                    </div>
                  </label>

                  <label
                    className={`border rounded-xl p-4 cursor-pointer flex items-center space-x-3 transition-colors ${
                      !isValid ? 'border-rose-600 bg-rose-50 text-rose-950 font-bold' : 'border-slate-200'
                    }`}
                  >
                    <input
                      type="radio"
                      name="validity"
                      checked={!isValid}
                      onChange={() => setIsValid(false)}
                      className="text-rose-600"
                    />
                    <div>
                      <XCircle className="w-5 h-5 text-rose-600 mb-1" />
                      <div>Reject as Invalid / Duplicate</div>
                      <div className="text-[10px] text-slate-500 font-normal">Non-ecological or false</div>
                    </div>
                  </label>
                </div>
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Verification Findings & Technical Notes *</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Record satellite verification cross-checks, GIS proximity to known drainage basins, or local government liaison confirmations..."
                  value={verificationNotes}
                  onChange={e => setVerificationNotes(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-1 focus:ring-emerald-600"
                />
              </div>

              <div className="flex items-center space-x-2">
                <label className="inline-flex items-center cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={requestInspection}
                    onChange={e => setRequestInspection(e.target.checked)}
                    className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 mr-2"
                  />
                  <span className="font-semibold text-slate-800">Dispatch field inspection officer for physical on-site assessment</span>
                </label>
              </div>

              <div className="pt-4 border-t border-slate-200 flex justify-end">
                <button
                  type="submit"
                  disabled={isVerifying || stage !== 'VERIFICATION'}
                  className="px-5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white inline-flex items-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title={stage !== 'VERIFICATION' ? 'Already verified — see status banner' : ''}
                >
                  <CheckSquare className="w-4 h-4 mr-1.5" />
                  {isVerifying
                    ? 'Saving...'
                    : stage === 'VERIFICATION'
                      ? 'Submit Verification & Proceed to Assessment'
                      : '✓ Already Verified'}
                </button>
              </div>
            </form>
          )}

          {/* Tab 2: Assessment Form (Multi-Criteria Scoring Engine) */}
          {activeTab === 'ASSESSMENT' && selectedHazard && (
            <form onSubmit={handleAssessSubmit} className="p-6 space-y-6 text-xs text-slate-700 flex-1 overflow-y-auto">
              {/* Dynamic Score Calculator Banner */}
              <div className="p-4 rounded-xl bg-slate-900 text-white flex items-center justify-between shadow-md">
                <div>
                  <span className="text-[10px] font-mono uppercase text-emerald-400">Multi-Criteria Evaluation Engine</span>
                  <div className="text-xl font-black mt-0.5">
                    Calculated Score: <span className="text-amber-400">{calculatedPriorityScore}</span> / 100
                  </div>
                  <p className="text-[11px] text-slate-300">
                    Weighted algorithm: Severity (25%) + Urgency (20%) + Exposure (20%) + Impact (20%) + Escalation (15%)
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-[10px] uppercase text-slate-400 block">Recommended Category</span>
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-xs font-bold tracking-wide mt-1 ${
                      calculatedPriority === 'CRITICAL'
                        ? 'bg-rose-500 text-white'
                        : calculatedPriority === 'HIGH'
                        ? 'bg-orange-500 text-white'
                        : calculatedPriority === 'MEDIUM'
                        ? 'bg-amber-500 text-slate-950'
                        : 'bg-emerald-500 text-white'
                    }`}
                  >
                    {calculatedPriority}
                  </span>
                </div>
              </div>

              {/* 5 Sliders for Multi-Criteria Scoring */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="flex justify-between font-semibold mb-1">
                    <span>Severity (Scale 1-10)</span>
                    <span className="font-mono text-emerald-800">{severityScore}/10 (Weight: 25%)</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={severityScore}
                    onChange={e => setSeverityScore(parseInt(e.target.value))}
                    className="w-full accent-emerald-700 cursor-pointer"
                  />
                  <span className="text-[10px] text-slate-400">Physical magnitude of degradation / ravine depth</span>
                </div>

                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="flex justify-between font-semibold mb-1">
                    <span>Urgency (Scale 1-10)</span>
                    <span className="font-mono text-emerald-800">{urgencyScore}/10 (Weight: 20%)</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={urgencyScore}
                    onChange={e => setUrgencyScore(parseInt(e.target.value))}
                    className="w-full accent-emerald-700 cursor-pointer"
                  />
                  <span className="text-[10px] text-slate-400">Proximity to next rainfall season or sudden collapse</span>
                </div>

                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="flex justify-between font-semibold mb-1">
                    <span>Population Exposure (Scale 1-10)</span>
                    <span className="font-mono text-emerald-800">{exposureScore}/10 (Weight: 20%)</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={exposureScore}
                    onChange={e => setExposureScore(parseInt(e.target.value))}
                    className="w-full accent-emerald-700 cursor-pointer"
                  />
                  <span className="text-[10px] text-slate-400">Density of settlement and vulnerable demographics</span>
                </div>

                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="flex justify-between font-semibold mb-1">
                    <span>Socio-Economic Impact (Scale 1-10)</span>
                    <span className="font-mono text-emerald-800">{impactScore}/10 (Weight: 20%)</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={impactScore}
                    onChange={e => setImpactScore(parseInt(e.target.value))}
                    className="w-full accent-emerald-700 cursor-pointer"
                  />
                  <span className="text-[10px] text-slate-400">Destruction of roads, farmlands, markets, water sources</span>
                </div>

                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 sm:col-span-2">
                  <div className="flex justify-between font-semibold mb-1">
                    <span>Escalation Risk if Unaddressed (Scale 1-10)</span>
                    <span className="font-mono text-emerald-800">{escalationScore}/10 (Weight: 15%)</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={escalationScore}
                    onChange={e => setEscalationScore(parseInt(e.target.value))}
                    className="w-full accent-emerald-700 cursor-pointer"
                  />
                  <span className="text-[10px] text-slate-400">Rate of lateral expansion and cost multiplier if delayed</span>
                </div>
              </div>

              {/* Impact Breakdown Fields */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block font-semibold mb-1 text-slate-800">Environmental Impact</label>
                  <textarea
                    rows={2}
                    value={environmentalImpact}
                    onChange={e => setEnvironmentalImpact(e.target.value)}
                    className="w-full p-2 rounded-lg border border-slate-300"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1 text-slate-800">Economic Impact</label>
                  <textarea
                    rows={2}
                    value={economicImpact}
                    onChange={e => setEconomicImpact(e.target.value)}
                    className="w-full p-2 rounded-lg border border-slate-300"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1 text-slate-800">Social / Community Impact</label>
                  <textarea
                    rows={2}
                    value={socialImpact}
                    onChange={e => setSocialImpact(e.target.value)}
                    className="w-full p-2 rounded-lg border border-slate-300"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Engineering Assessment & Technical Findings *</label>
                <textarea
                  rows={3}
                  required
                  value={technicalFindings}
                  onChange={e => setTechnicalFindings(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-slate-300"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Recommended Intervention Type</label>
                <select
                  value={recommendedInterventionType}
                  onChange={e => setRecommendedInterventionType(e.target.value)}
                  className="w-full p-2 rounded-lg border border-slate-300 bg-white"
                >
                  {(referenceData?.intervention_types || [
                    'Structural Gully Control Works',
                    'Drainage Channelization',
                    'Shoreline Protection & Groynes',
                    'Shelterbelt Afforestation',
                    'Retention Basin & Terracing',
                    'Mine Pit Backfilling & Remediation'
                  ]).map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              <div className="pt-4 border-t border-slate-200 flex justify-end">
                <button
                  type="submit"
                  disabled={isAssessing || stage !== 'ASSESSMENT'}
                  className="px-5 py-2 rounded-lg text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white inline-flex items-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title={stage !== 'ASSESSMENT' ? (stage === 'VERIFICATION' ? 'Hazard not yet verified' : 'Assessment already completed') : ''}
                >
                  <Compass className="w-4 h-4 mr-1.5" />
                  {isAssessing
                    ? 'Recording...'
                    : stage === 'ASSESSMENT'
                      ? 'Commit Technical Assessment & Move to Formulation'
                      : stage === 'VERIFICATION'
                        ? 'Verify hazard first'
                        : '✓ Assessment Recorded'}
                </button>
              </div>
            </form>
          )}

          {/* Tab 3: Intervention Formulation */}
          {activeTab === 'INTERVENTION' && selectedHazard && (
            <form onSubmit={handleInterventionSubmit} className="p-6 space-y-5 text-xs text-slate-700 flex-1 overflow-y-auto">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-1">
                  Edo State Intervention Pipeline Formulation
                </h4>
                <p className="text-slate-500 mb-4">
                  Define the engineering intervention project scope, budget estimation, and implementation timelines.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="sm:col-span-2">
                  <label className="block font-semibold mb-1 text-slate-800">Intervention Project Title *</label>
                  <input
                    type="text"
                    required
                    value={interventionTitle}
                    onChange={e => setInterventionTitle(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block font-semibold mb-1 text-slate-800">Scope of Civil / Bio-Engineering Works *</label>
                  <textarea
                    rows={3}
                    required
                    value={interventionScope}
                    onChange={e => setInterventionScope(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300"
                  />
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-800">Estimated Cost (NGN) *</label>
                  <input
                    type="number"
                    required
                    value={estimatedCost}
                    onChange={e => setEstimatedCost(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 font-mono"
                  />
                  <span className="text-[10px] text-slate-400 mt-0.5 block">
                    ₦{(estimatedCost / 1e6).toFixed(1)} Million
                  </span>
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-800">Proposed Funding Envelope</label>
                  <select
                    value={proposedFunding}
                    onChange={e => setProposedFunding(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
                  >
                    <option value="Edo State Ecological Fund Direct Allocation">Edo State Ecological Fund (EDEFA Direct)</option>
                    <option value="State-Federal Ecological Matching Grant">State-Federal Ecological Matching Grant</option>
                    <option value="World Bank NEWMAP / ACRESAL Edo Sub-grant">World Bank NEWMAP / ACRESAL Edo Sub-grant</option>
                    <option value="Edo State Emergency Ecological Reserve">Edo State Emergency Ecological Reserve</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-800">Responsible Department</label>
                  <input
                    type="text"
                    value={responsibleDepartment}
                    onChange={e => setResponsibleDepartment(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300"
                  />
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-800">Responsible Lead Officer</label>
                  <input
                    type="text"
                    value={responsibleOfficer}
                    onChange={e => setResponsibleOfficer(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300"
                  />
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-800">Proposed Start Date</label>
                  <input
                    type="date"
                    value={proposedStartDate}
                    onChange={e => setProposedStartDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300"
                  />
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-800">Target Completion Date</label>
                  <input
                    type="date"
                    value={proposedCompletionDate}
                    onChange={e => setProposedCompletionDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block font-semibold mb-1 text-slate-800">Expected Ecological & Socioeconomic Outcome</label>
                  <input
                    type="text"
                    value={expectedOutcome}
                    onChange={e => setExpectedOutcome(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300"
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-slate-200 flex justify-end">
                <button
                  type="submit"
                  disabled={isSavingIntervention || stage !== 'INTERVENTION'}
                  className="px-5 py-2 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title={stage !== 'INTERVENTION' ? (stage === 'DONE' ? 'Intervention already registered' : 'Assessment required first') : ''}
                >
                  <Send className="w-4 h-4 mr-1.5" />
                  {isSavingIntervention
                    ? 'Saving...'
                    : stage === 'INTERVENTION'
                      ? 'Register Intervention in National Pipeline'
                      : stage === 'DONE'
                        ? '✓ Intervention Already Registered'
                        : 'Assessment required first'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};