import React, { useState, useEffect } from 'react';
import { Project, Site, SiteVisit } from '../../types/index.ts';
import {
  X,
  ClipboardCheck,
  Compass,
  Camera,
  Save,
  Send,
  AlertTriangle,
  CheckCircle,
  FileText
} from 'lucide-react';
import { DirectionsLink } from '../common/DirectionsLink.tsx';

interface FieldVisitFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
  projects: Project[];
  sites: Site[];
  defaultProject?: Project | null;
}

export const FieldVisitForm: React.FC<FieldVisitFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  projects,
  sites,
  defaultProject
}) => {
  const [projectId, setProjectId] = useState(defaultProject?.id || projects[0]?.id || '');
  const [siteId, setSiteId] = useState(sites[0]?.id || '');

  // Whenever the modal opens, force the project to the default (or first project).
  // Also clear evidence + reset GPS so nothing leaks from a previous session.
  useEffect(() => {
    if (!isOpen) return;
    const targetProject = defaultProject?.id || projects[0]?.id || '';
    setProjectId(targetProject);
    setEvidenceFiles([]);
    setGpsLatitude(defaultProject?.latitude || 6.2209);
    setGpsLongitude(defaultProject?.longitude || 7.0722);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, defaultProject?.id]);

  // Whenever the project changes (or the modal opens), reset siteId to a site
  // that belongs to the current project. Prevents a stale site_id from another
  // project leaking into this visit.
  useEffect(() => {
    if (!isOpen) return;
    const candidates = sites.filter(s => s.project_id === projectId);
    const target = candidates[0]?.id || '';
    setSiteId(target);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, projectId, sites.length]);
  const [officerName, setOfficerName] = useState('Engr. Samuel Adebayo');
  const [visitDate, setVisitDate] = useState(new Date().toISOString().split('T')[0]);
  const [gpsLatitude, setGpsLatitude] = useState(defaultProject?.latitude || 6.2209);
  const [gpsLongitude, setGpsLongitude] = useState(defaultProject?.longitude || 7.0722);
  const [purpose, setPurpose] = useState('Routine Physical Verification & Quality Audit');
  const [weatherConditions, setWeatherConditions] = useState('Dry sunny morning, clear visibility, 32°C');
  const [activitiesObserved, setActivitiesObserved] = useState('Pouring of reinforced concrete in chute floor section; earth compaction with vibratory roller.');
  const [progressPercentage, setProgressPercentage] = useState(45);
  const [workCompleted, setWorkCompleted] = useState('650 meters of reinforced concrete drainage chute completed; stilling basin excavated.');
  const [workOutstanding, setWorkOutstanding] = useState('Installation of gabion mattresses at drop structure and vetiver grass planting along steep slopes.');
  const [materialsEquipment, setMaterialsEquipment] = useState('2 excavators, 1 bulldozer, 1 cement mixer, 450 bags of Dangote 42.5R cement on site.');
  const [qualityObservations, setQualityObservations] = useState('Concrete slump test performed at 75mm; cube compressive test samples taken on site.');
  const [safetyObservations, setSafetyObservations] = useState('All site workers equipped with hard hats, safety boots, and high-visibility vests. Edge fall protection barriers installed.');
  const [problemsChallenges, setProblemsChallenges] = useState('Minor diesel supply delays due to localized fuel scarcity; mitigated by reserve fuel tanks.');
  const [recommendations, setRecommendations] = useState('Accelerate slope stabilization before start of peak August rainfall break.');
  const [officerComments, setOfficerComments] = useState('Contractor performance is satisfactory. Quality adheres to Federal Ministry of Works civil engineering standards.');
  const [stage, setStage] = useState<'Initial' | 'Visit 1' | 'Visit 2' | 'Visit 3' | 'Current' | 'Follow-up'>('Current');
  const [stageTag, setStageTag] = useState<'before' | 'during' | 'after'>('during');

  const [evidenceFiles, setEvidenceFiles] = useState<any[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [gpsDetecting, setGpsDetecting] = useState(false);

  if (!isOpen) return null;

  const handleDetectGps = () => {
    if (!navigator.geolocation) return;
    setGpsDetecting(true);
    navigator.geolocation.getCurrentPosition(
      pos => {
        setGpsLatitude(parseFloat(pos.coords.latitude.toFixed(6)));
        setGpsLongitude(parseFloat(pos.coords.longitude.toFixed(6)));
        setGpsDetecting(false);
      },
      () => setGpsDetecting(false),
      { timeout: 10000 }
    );
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const reader = new FileReader();
      reader.onload = (uploadEvent: any) => {
        const newEvidence = {
          file_name: file.name,
          file_type: file.type,
          file_size: file.size,
          media_type: 'photo',
          file_url: uploadEvent.target.result,
          description: `Field inspection evidence [${stageTag}] - ${purpose}`,
          gps_latitude: gpsLatitude,
          gps_longitude: gpsLongitude,
          stage_tag: stageTag
        };
        setEvidenceFiles(prev => [...prev, newEvidence]);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) {
      alert('Please select a project before saving the visit.');
      return;
    }
    if (!siteId) {
      alert('Please select a site before saving the visit. If no sites exist yet, create one from the Sites tab.');
      return;
    }
    setIsSubmitting(true);
    try {
      await onSubmit({
        project_id: projectId,
        site_id: siteId,
        officer_name: officerName,
        visit_date: visitDate,
        gps_latitude: gpsLatitude,
        gps_longitude: gpsLongitude,
        purpose,
        weather_conditions: weatherConditions,
        activities_observed: activitiesObserved,
        progress_percentage: progressPercentage,
        work_completed: workCompleted,
        work_outstanding: workOutstanding,
        materials_equipment: materialsEquipment,
        quality_observations: qualityObservations,
        safety_observations: safetyObservations,
        problems_challenges: problemsChallenges,
        recommendations,
        officer_comments: officerComments,
        stage,
        stage_tag: stageTag,
        evidence: evidenceFiles
      });
      onClose();
    } catch (err: any) {
      alert(err.message || 'Error submitting visit log');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div id="field-visit-modal" className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200 text-xs">
        {/* Header */}
        <div className="px-6 py-4 bg-emerald-950 text-white flex items-center justify-between border-b border-emerald-900">
          <div className="flex items-center space-x-2">
            <ClipboardCheck className="w-5 h-5 text-amber-400" />
            <div>
              <h2 className="text-base font-bold text-white">Log Physical Field Inspection Visit</h2>
              <p className="text-xs text-emerald-300">
                Official supervision entry with GPS timestamp, QA/QC observations & photographic proof
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded text-emerald-300 hover:text-white hover:bg-emerald-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-5 text-slate-700">
          {/* Project & Officer */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block font-semibold mb-1 text-slate-800">Project *</label>
              <select
                value={projectId}
                onChange={e => setProjectId(e.target.value)}
                className="w-full p-2 border rounded-lg bg-white"
              >
                {projects.map(p => (
                  <option key={p.id} value={p.id}>{p.id} - {p.title}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Field Inspector Name *</label>
              <input
                type="text"
                required
                value={officerName}
                onChange={e => setOfficerName(e.target.value)}
                className="w-full p-2 border rounded-lg"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Visit Date *</label>
              <input
                type="date"
                required
                value={visitDate}
                onChange={e => setVisitDate(e.target.value)}
                className="w-full p-2 border rounded-lg"
              />
            </div>
          </div>

          {/* Coordinates & Stage */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
            <div>
              <label className="block font-semibold mb-1 text-slate-800">GPS Latitude</label>
              <input
                type="number"
                step="0.000001"
                value={gpsLatitude}
                onChange={e => setGpsLatitude(parseFloat(e.target.value) || 0)}
                className="w-full p-2 border rounded-lg font-mono"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">GPS Longitude</label>
              <input
                type="number"
                step="0.000001"
                value={gpsLongitude}
                onChange={e => setGpsLongitude(parseFloat(e.target.value) || 0)}
                className="w-full p-2 border rounded-lg font-mono"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Inspection Stage Tag</label>
              <select
                value={stageTag}
                onChange={e => setStageTag(e.target.value as any)}
                className="w-full p-2 border rounded-lg bg-white font-bold text-emerald-800"
              >
                <option value="before">BEFORE (Baseline condition)</option>
                <option value="during">DURING (Works in progress)</option>
                <option value="after">AFTER (Remediated / Handover)</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                type="button"
                onClick={handleDetectGps}
                className="w-full py-2 rounded-lg bg-emerald-100 hover:bg-emerald-200 text-emerald-800 font-semibold inline-flex items-center justify-center"
              >
                <Compass className="w-4 h-4 mr-1" />
                Acquire GPS
              </button>
              <DirectionsLink
                lat={gpsLatitude}
                lng={gpsLongitude}
                label="Directions to these coordinates"
                className="mt-2 text-blue-700 hover:text-blue-950 text-[11px] font-semibold inline-flex items-center"
              />
            </div>
          </div>

          {/* Progress & Activities */}
          <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 space-y-3">
            <div className="flex items-center justify-between">
              <label className="font-bold text-slate-900">Physical Work Progress Milestone</label>
              <span className="font-mono text-base font-black text-emerald-800">{progressPercentage}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={progressPercentage}
              onChange={e => setProgressPercentage(parseInt(e.target.value))}
              className="w-full accent-emerald-700"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold mb-1 text-slate-800">Activities Observed on Site *</label>
              <textarea
                rows={2}
                required
                value={activitiesObserved}
                onChange={e => setActivitiesObserved(e.target.value)}
                className="w-full p-2 border rounded-lg"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Materials & Equipment on Site</label>
              <textarea
                rows={2}
                value={materialsEquipment}
                onChange={e => setMaterialsEquipment(e.target.value)}
                className="w-full p-2 border rounded-lg"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Work Completed (Cumulative)</label>
              <textarea
                rows={2}
                value={workCompleted}
                onChange={e => setWorkCompleted(e.target.value)}
                className="w-full p-2 border rounded-lg"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Work Outstanding / Pending Tasks</label>
              <textarea
                rows={2}
                value={workOutstanding}
                onChange={e => setWorkOutstanding(e.target.value)}
                className="w-full p-2 border rounded-lg"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Quality Assurance & Specifications</label>
              <textarea
                rows={2}
                value={qualityObservations}
                onChange={e => setQualityObservations(e.target.value)}
                className="w-full p-2 border rounded-lg"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Occupational Health & Safety (HSE)</label>
              <textarea
                rows={2}
                value={safetyObservations}
                onChange={e => setSafetyObservations(e.target.value)}
                className="w-full p-2 border rounded-lg"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold mb-1 text-slate-800">Problems, Bottlenecks & Challenges</label>
              <textarea
                rows={2}
                value={problemsChallenges}
                onChange={e => setProblemsChallenges(e.target.value)}
                className="w-full p-2 border rounded-lg"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Technical Recommendations & Corrective Actions</label>
              <textarea
                rows={2}
                value={recommendations}
                onChange={e => setRecommendations(e.target.value)}
                className="w-full p-2 border rounded-lg"
              />
            </div>
          </div>

          {/* Photo Attachments */}
          <div>
            <label className="block font-semibold mb-1 text-slate-800">
              Attach Time-Stamped Inspection Photographs ({evidenceFiles.length})
            </label>
            <label className="border-2 border-dashed border-emerald-300 bg-emerald-50/40 hover:bg-emerald-50 rounded-xl p-3 text-center cursor-pointer block">
              <Camera className="w-5 h-5 mx-auto mb-1 text-emerald-700" />
              <span className="font-semibold text-emerald-900 block">Click to Upload Inspection Photos</span>
              <span className="text-[10px] text-slate-500">Tagging photos automatically as: [{stageTag.toUpperCase()}]</span>
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>

            {evidenceFiles.length > 0 && (
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 mt-2">
                {evidenceFiles.map((ev, i) => (
                  <div key={i} className="relative rounded border overflow-hidden">
                    <img src={ev.file_url} alt="" className="h-16 w-full object-cover" />
                    <span className="absolute bottom-0 inset-x-0 bg-black/70 text-white text-[9px] text-center uppercase">
                      {ev.stage_tag}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submit */}
          <div className="pt-4 border-t flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white font-bold inline-flex items-center"
            >
              <Send className="w-4 h-4 mr-1.5" />
              {isSubmitting ? 'Logging...' : 'Save Inspection Visit Log'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
