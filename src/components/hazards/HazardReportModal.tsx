import React, { useState, useEffect } from 'react';
import { Hazard, HazardSeverity, HazardUrgency } from '../../types/index.ts';
import {
  X,
  MapPin,
  Camera,
  Video,
  Upload,
  Save,
  Send,
  AlertTriangle,
  Info,
  CheckCircle,
  Compass,
  FileText
} from 'lucide-react';
import { offlineDrafts } from '../../services/api.ts';

interface HazardReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (formData: any) => Promise<void>;
  statesAndLgas: Record<string, string[]>;
  categories: string[];
  editHazard?: Hazard | null;
  referenceData?: any;
}



export const HazardReportModal: React.FC<HazardReportModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories,
  editHazard,
  referenceData
}) => {
  const isEditMode = Boolean(editHazard);
  const [formData, setFormData] = useState({
    title: '',
    category: categories[0] || 'Gully Erosion',
    hazard_type: '',
    description: '',
    date_observed: new Date().toISOString().split('T')[0],
    state: Object.keys(statesAndLgas)[0] || 'Anambra',
    lga: '',
    ward: '',
    community: '',
    address_description: '',
    latitude: '' as any,
    longitude: '' as any,
    estimated_affected_area_sqm: 5000,
    estimated_affected_population: 500,
    estimated_affected_assets: 'Residential houses, access roads, agricultural farmlands',
    potential_impact: 'Risk of structural collapse, loss of farmland, and road severance during next rainfall season.',
    severity: 'HIGH' as HazardSeverity,
    urgency: 'HIGH' as HazardUrgency,
    reporter_name: '',
    reporter_type: 'FIELD_OFFICER' as const,
    reporter_contact: '',
    is_recurring: false,
    recurring_count: 1
  });

  const [evidenceFiles, setEvidenceFiles] = useState<any[]>([]);

  // Load hazard into form when entering edit mode
  useEffect(() => {
    if (!editHazard || !isOpen) return;
    setFormData({
      title: editHazard.title || '',
      category: editHazard.category || categories[0] || 'Gully Erosion',
      hazard_type: (editHazard as any).hazard_type || '',
      description: editHazard.description || '',
      date_observed: editHazard.date_observed || new Date().toISOString().split('T')[0],
      state: editHazard.state || Object.keys(statesAndLgas)[0] || 'Edo',
      lga: editHazard.lga || '',
      ward: editHazard.ward || '',
      community: editHazard.community || '',
      address_description: editHazard.address_description || '',
      latitude: editHazard.latitude ?? ('' as any),
      longitude: editHazard.longitude ?? ('' as any),
      estimated_affected_area_sqm: editHazard.estimated_affected_area_sqm ?? 5000,
      estimated_affected_population: editHazard.estimated_affected_population ?? 500,
      estimated_affected_assets: editHazard.estimated_affected_assets || '',
      potential_impact: editHazard.potential_impact || '',
      severity: (editHazard.severity || 'HIGH') as HazardSeverity,
      urgency: (editHazard.urgency || 'HIGH') as HazardUrgency,
      reporter_name: editHazard.reporter_name || '',
      reporter_type: ((editHazard as any).reporter_type || 'FIELD_OFFICER') as any,
      reporter_contact: editHazard.reporter_contact || '',
      is_recurring: (editHazard as any).is_recurring ?? false,
      recurring_count: (editHazard as any).recurring_count ?? 1,
    });
  }, [editHazard, isOpen]);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [gpsDetecting, setGpsDetecting] = useState(false);
  const [gpsAccuracy, setGpsAccuracy] = useState<number | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  // Available LGAs based on selected state
  const availableLgas = statesAndLgas[formData.state] || [];

  // Update LGA when state changes
  useEffect(() => {
    if (availableLgas.length > 0 && !availableLgas.includes(formData.lga)) {
      setFormData(prev => ({ ...prev, lga: availableLgas[0] }));
    }
  }, [formData.state, availableLgas]);

  // Load draft if available on open
  useEffect(() => {
    if (isOpen) {
      const saved = offlineDrafts.getDraft('new_hazard_report');
      if (saved && saved.data) {
        setFormData(saved.data);
        setStatusMessage('Restored draft from local storage.');
      }
    }
  }, [isOpen]);

  // Auto-trigger GPS detection when the modal opens in create-mode
  useEffect(() => {
    if (!isOpen || isEditMode) return;
    // Only auto-detect if we don't already have coordinates
    if (formData.latitude !== '' && formData.latitude !== null) return;
    // Give the modal a moment to mount, then auto-detect
    const timer = setTimeout(() => {
      handleDetectGps({ auto: true });
    }, 500);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  if (!isOpen) return null;

  const handleFieldChange = (key: string, value: any) => {
    const updated = { ...formData, [key]: value };
    setFormData(updated);
    offlineDrafts.saveDraft('new_hazard_report', updated);
  };

  const handleDetectGps = async (opts: { auto?: boolean } = {}) => {
    if (!navigator.geolocation) {
      setStatusMessage('Geolocation is not supported by this browser.');
      return;
    }
    setGpsDetecting(true);
    setGpsAccuracy(null);
    setStatusMessage('Requesting device location…');
    try {
      const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 15000,
          maximumAge: 0,
        });
      });
      const acc = Math.round(pos.coords.accuracy);
      // Reject very low-quality fixes (typical of desktop without GPS)
      if (acc > 500) {
        setGpsAccuracy(acc);
        setStatusMessage(
          `GPS accuracy is poor (±${acc} m). Enter coordinates manually — or open this page on a phone with GPS.`
        );
        return;
      }
      setFormData(prev => ({
        ...prev,
        latitude: parseFloat(pos.coords.latitude.toFixed(6)),
        longitude: parseFloat(pos.coords.longitude.toFixed(6))
      }));
      setGpsAccuracy(acc);
      setStatusMessage(`Location captured — accuracy ±${acc} m`);
    } catch (err: any) {
      // Silence permission errors on auto-detect (user hasn't been prompted yet)
      if (opts.auto && err?.code === 1) {
        setStatusMessage('');
        return;
      }
      const msg =
        err?.code === 1 ? 'Permission denied — enable location in browser settings.' :
        err?.code === 2 ? 'Location unavailable — check that device GPS is on.' :
        err?.code === 3 ? 'GPS timed out — try again outdoors or enter coordinates manually.' :
        'Unable to detect location — you may type coordinates manually.';
      setStatusMessage(msg);
    } finally {
      setGpsDetecting(false);
    }
  };



  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>, mediaType: 'photo' | 'video' | 'document') => {
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
          media_type: mediaType,
          file_url: uploadEvent.target.result,
          description: `Field photo/video evidence captured at ${formData.community || 'site'}`,
          gps_latitude: formData.latitude,
          gps_longitude: formData.longitude,
          stage_tag: 'evidence'
        };
        setEvidenceFiles(prev => [...prev, newEvidence]);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title || !formData.community || !formData.reporter_name) {
      alert('Please fill out the required title, community, and reporter name fields.');
      return;
    }
    if (formData.latitude === '' || formData.longitude === '' || formData.latitude === null || formData.longitude === null) {
      alert('Coordinates are required. Click "Detect Coordinates (Device GPS)" or enter them manually.');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        ...formData,
        evidence: evidenceFiles
      });
      offlineDrafts.clearDraft('new_hazard_report');
      onClose();
    } catch (error: any) {
      alert(`Submission failed: ${error.message || 'Unknown error'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div id="hazard-report-modal" className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200">
        {/* Header */}
        <div className="px-6 py-4 bg-emerald-950 text-white flex items-center justify-between border-b border-emerald-900">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <div>
              <h2 className="text-base font-bold text-white">Report New Ecological Hazard</h2>
              <p className="text-xs text-emerald-300">
                Official registration into the Edo State Ecological Hazard Database (EDEFA)
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-emerald-300 hover:text-white hover:bg-emerald-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {statusMessage && (
          <div className="bg-emerald-50 px-4 py-2 text-xs text-emerald-800 border-b border-emerald-200 flex items-center justify-between">
            <span>{statusMessage}</span>
            <button onClick={() => setStatusMessage(null)} className="text-emerald-900 font-bold ml-2">×</button>
          </div>
        )}

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-6 text-xs text-slate-700">
          {/* Section 1: Classification */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-900 mb-3 pb-1 border-b border-emerald-100 flex items-center">
              <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center mr-2 text-[10px] font-bold">1</span>
              Hazard Classification & Details
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              <div className="sm:col-span-2">
                <label className="block font-semibold mb-1 text-slate-800">Hazard Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Severe Gully Encroachment Threatening Nkpor-Obosi Link Road"
                  value={formData.title}
                  onChange={e => handleFieldChange('title', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-1 focus:ring-emerald-600 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Ecological Category *</label>
                <select
                  value={formData.category}
                  onChange={e => handleFieldChange('category', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-1 focus:ring-emerald-600 focus:outline-hidden bg-white"
                >
                  {categories.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Specific Hazard Type</label>
                <input
                  type="text"
                  placeholder="e.g., Catastrophic Headward Gully, Riverbank Scouring"
                  value={formData.hazard_type}
                  onChange={e => handleFieldChange('hazard_type', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-1 focus:ring-emerald-600 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Date Observed *</label>
                <input
                  type="date"
                  required
                  value={formData.date_observed}
                  onChange={e => handleFieldChange('date_observed', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-1 focus:ring-emerald-600 focus:outline-hidden"
                />
              </div>

              <div className="flex items-center space-x-2 pt-6">
                <label className="inline-flex items-center cursor-pointer select-none font-medium">
                  <input
                    type="checkbox"
                    checked={formData.is_recurring}
                    onChange={e => handleFieldChange('is_recurring', e.target.checked)}
                    className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 mr-2"
                  />
                  <span>Is this a recurring hazard?</span>
                </label>
              </div>
            </div>

            <div className="mt-3">
              <label className="block font-semibold mb-1 text-slate-800">Description of Ecological Problem *</label>
              <textarea
                rows={3}
                required
                placeholder="Describe the nature of the ecological degradation, physical evidence observed, depth/width of ravines, water levels, or sand dune movement..."
                value={formData.description}
                onChange={e => handleFieldChange('description', e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-1 focus:ring-emerald-600 focus:outline-hidden"
              />
            </div>
          </div>

          {/* Section 2: Location & GPS */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-900 mb-3 pb-1 border-b border-emerald-100 flex items-center">
              <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center mr-2 text-[10px] font-bold">2</span>
              Geographic Location & Coordinates
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <label className="block font-semibold mb-1 text-slate-800">State *</label>
                <select
                  value={formData.state}
                  onChange={e => handleFieldChange('state', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-1 focus:ring-emerald-600 bg-white"
                >
                  {Object.keys(statesAndLgas).map(st => (
                    <option key={st} value={st}>{st}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">LGA *</label>
                <select
                  value={formData.lga}
                  onChange={e => handleFieldChange('lga', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-1 focus:ring-emerald-600 bg-white"
                >
                  {availableLgas.map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Ward</label>
                <input
                  type="text"
                  placeholder="e.g., Ward 04"
                  value={formData.ward}
                  onChange={e => handleFieldChange('ward', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-1 focus:ring-emerald-600"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Community / Village *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Umuoji Community"
                  value={formData.community}
                  onChange={e => handleFieldChange('community', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-1 focus:ring-emerald-600"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block font-semibold mb-1 text-slate-800">Address / Landmark Description</label>
                <input
                  type="text"
                  placeholder="e.g., 200m south of Central Primary School junction"
                  value={formData.address_description}
                  onChange={e => handleFieldChange('address_description', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-1 focus:ring-emerald-600"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Latitude (Decimal)</label>
                <input
                  type="number"
                  step="0.000001"
                  placeholder="Auto-fill via GPS"
                  value={formData.latitude}
                  onChange={e => handleFieldChange('latitude', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 font-mono text-xs"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Longitude (Decimal)</label>
                <input
                  type="number"
                  step="0.000001"
                  placeholder="Auto-fill via GPS"
                  value={formData.longitude}
                  onChange={e => handleFieldChange('longitude', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 font-mono text-xs"
                />
              </div>
            </div>

            <div className="mt-2 flex items-center justify-between">
              <button
                type="button"
                onClick={() => handleDetectGps()}
                disabled={gpsDetecting}
                className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-100 hover:bg-emerald-200 text-emerald-800 transition-colors"
              >
                <Compass className={`w-4 h-4 mr-1.5 ${gpsDetecting ? 'animate-spin' : ''}`} />
                {gpsDetecting ? 'Detecting device GPS...' : 'Detect Coordinates (Device GPS)'}
              </button>
              <span className="text-[11px] text-slate-400">
                Coordinates will center point on national GIS map
              </span>
            </div>
          </div>

          {/* Section 3: Impact Assessment */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-900 mb-3 pb-1 border-b border-emerald-100 flex items-center">
              <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center mr-2 text-[10px] font-bold">3</span>
              Impact Scope & Initial Risk Grading
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <label className="block font-semibold mb-1 text-slate-800">Estimated Area (sq. meters)</label>
                <input
                  type="number"
                  value={formData.estimated_affected_area_sqm}
                  onChange={e => handleFieldChange('estimated_affected_area_sqm', parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Exposed Population</label>
                <input
                  type="number"
                  value={formData.estimated_affected_population}
                  onChange={e => handleFieldChange('estimated_affected_population', parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Initial Severity</label>
                <select
                  value={formData.severity}
                  onChange={e => handleFieldChange('severity', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white font-semibold"
                >
                  {(referenceData?.severities || ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']).map((s: string) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Action Urgency</label>
                <select
                  value={formData.urgency}
                  onChange={e => handleFieldChange('urgency', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
                >
                  {(referenceData?.urgencies || ['IMMEDIATE', 'HIGH', 'NORMAL', 'ROUTINE']).map((u: string) => (
                    <option key={u} value={u}>{u}</option>
                  ))}
                </select>
              </div>

              <div className="sm:col-span-2">
                <label className="block font-semibold mb-1 text-slate-800">Exposed Assets & Infrastructure</label>
                <input
                  type="text"
                  placeholder="e.g., 12 residential compounds, electric transformers, culvert"
                  value={formData.estimated_affected_assets}
                  onChange={e => handleFieldChange('estimated_affected_assets', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block font-semibold mb-1 text-slate-800">Potential Escalation Consequences</label>
                <input
                  type="text"
                  placeholder="e.g., Total cutoff of highway during upcoming rainy season"
                  value={formData.potential_impact}
                  onChange={e => handleFieldChange('potential_impact', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300"
                />
              </div>
            </div>
          </div>

          {/* Section 4: Photographic & Video Evidence */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-900 mb-3 pb-1 border-b border-emerald-100 flex items-center">
              <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center mr-2 text-[10px] font-bold">4</span>
              Photographic & Video Evidence Attachments
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
              <label className="border-2 border-dashed border-emerald-300 bg-emerald-50/40 hover:bg-emerald-50 rounded-xl p-4 text-center cursor-pointer block transition-colors">
                <Camera className="w-6 h-6 mx-auto mb-1 text-emerald-700" />
                <span className="font-semibold text-emerald-900 block">Add Photographs</span>
                <span className="text-[10px] text-slate-500">JPG, PNG, WebP up to 15MB each</span>
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={e => handleFileUpload(e, 'photo')}
                  className="hidden"
                />
              </label>

              <label className="border-2 border-dashed border-amber-300 bg-amber-50/40 hover:bg-amber-50 rounded-xl p-4 text-center cursor-pointer block transition-colors">
                <Video className="w-6 h-6 mx-auto mb-1 text-amber-700" />
                <span className="font-semibold text-amber-900 block">Add Video Recordings</span>
                <span className="text-[10px] text-slate-500">MP4, WebM aerial/field footage</span>
                <input
                  type="file"
                  multiple
                  accept="video/*"
                  onChange={e => handleFileUpload(e, 'video')}
                  className="hidden"
                />
              </label>
            </div>

            {/* Evidence preview grid */}
            {evidenceFiles.length > 0 && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2">
                {evidenceFiles.map((ev, idx) => (
                  <div key={idx} className="relative rounded-lg border border-slate-200 bg-slate-50 overflow-hidden group">
                    {ev.media_type === 'photo' ? (
                      <img src={ev.file_url} alt={ev.file_name} className="h-20 w-full object-cover" />
                    ) : (
                      <div className="h-20 w-full bg-slate-800 flex items-center justify-center text-white">
                        <Video className="w-6 h-6 text-amber-400" />
                      </div>
                    )}
                    <div className="p-1.5 text-[10px]">
                      <div className="font-semibold truncate">{ev.file_name}</div>
                      <div className="text-slate-400 font-mono">{(ev.file_size / 1024).toFixed(0)} KB</div>
                    </div>
                    <button
                      type="button"
                      onClick={() => setEvidenceFiles(prev => prev.filter((_, i) => i !== idx))}
                      className="absolute top-1 right-1 bg-rose-600 text-white rounded-full p-0.5 opacity-80 hover:opacity-100"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Section 5: Reporter Details */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-900 mb-3 pb-1 border-b border-emerald-100 flex items-center">
              <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center mr-2 text-[10px] font-bold">5</span>
              Reporter Details & Verification Contacts
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block font-semibold mb-1 text-slate-800">Reporter Full Name *</label>
                <input
                  type="text"
                  required
                  placeholder="Engr. / Mr. / Dr. ..."
                  value={formData.reporter_name}
                  onChange={e => handleFieldChange('reporter_name', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Reporter Category</label>
                <select
                  value={formData.reporter_type}
                  onChange={e => handleFieldChange('reporter_type', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
                >
                  {(referenceData?.reporter_types || ['FIELD_OFFICER', 'LGA_OFFICIAL', 'COMMUNITY_LEADER', 'PUBLIC']).map((r: string) => (
                    <option key={r} value={r}>{r.replace(/_/g, ' ')}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-800">Phone / Email Contact *</label>
                <input
                  type="text"
                  required
                  placeholder="+234 ... / email"
                  value={formData.reporter_contact}
                  onChange={e => handleFieldChange('reporter_contact', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300"
                />
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
            <div className="flex items-center space-x-2 text-[11px] text-slate-500">
              <CheckCircle className="w-4 h-4 text-emerald-600" />
              <span>Auto-saved to local offline storage</span>
            </div>

            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white transition-colors shadow-xs inline-flex items-center"
              >
                <Send className="w-4 h-4 mr-1.5" />
                {isSubmitting ? (isEditMode ? 'Saving...' : 'Registering...') : (isEditMode ? 'Save Changes' : 'Register Hazard Report')}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
