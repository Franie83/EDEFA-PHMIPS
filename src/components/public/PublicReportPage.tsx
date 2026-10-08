import React, { useRef, useState, useEffect } from 'react';
import { AlertTriangle, ArrowLeft, CheckCircle2, MapPin, Send, Image as ImageIcon, Video, Trash2, Copy } from 'lucide-react';
import { api } from '../../services/api';
import { PublicUserBanner } from './PublicUserBanner.tsx';

interface Props {
  onBack?: () => void;
  currentUser?: any;
  onSignOut?: () => void;
}

const CATEGORIES = [
  'Gully erosion', 'Flooding', 'Landslide', 'Soil instability',
  'Coastal erosion', 'Deforestation', 'Illegal dumping', 'Desertification', 'Other'
];
const SEVERITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
const EDO_LGAS = [
  'Akoko Edo', 'Egor', 'Esan Central', 'Esan North-East', 'Esan South-East',
  'Esan West', 'Etsako Central', 'Etsako East', 'Etsako West', 'Igueben',
  'Ikpoba-Okha', 'Oredo', 'Orhionmwon', 'Ovia North-East', 'Ovia South-West',
  'Owan East', 'Owan West', 'Uhunmwonde'
];

type Attachment = {
  file_name: string;
  file_type: string;
  file_size: number;
  media_type: 'photo' | 'video';
  base64_data: string;
  description: string;
};

const fileToBase64 = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ''));
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsDataURL(file);
  });

export const PublicReportPage: React.FC<Props> = ({ onBack, currentUser, onSignOut }) => {
  const [form, setForm] = useState({
    title: '',
    category: 'Gully erosion',
    description: '',
    reporter_name: '',
    reporter_contact: '',
    state: 'Edo',
    lga: 'Oredo',
    ward: '',
    community: '',
    address_description: '',
    latitude: '6.335',
    longitude: '5.603',
    severity: 'MEDIUM',
    estimated_affected_population: '',
    estimated_affected_area_sqm: '',
  });

  const [photos, setPhotos] = useState<Attachment[]>([]);
  const [videos, setVideos] = useState<Attachment[]>([]);
  const photoInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<{ tracking_code: string; hazard_id: string } | null>(null);
  const [copied, setCopied] = useState(false);

  // Scroll to the top when the success screen appears — the code lives near the top.
  useEffect(() => {
    if (result) {
      try { window.scrollTo({ top: 0, behavior: 'smooth' }); } catch {}
    }
  }, [result]);

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm({ ...form, [k]: e.target.value });

  const addFiles = async (files: FileList | null, kind: 'photo' | 'video') => {
    if (!files) return;
    const maxBytes = kind === 'photo' ? 15 * 1024 * 1024 : 50 * 1024 * 1024;
    const list = Array.from(files);
    const out: Attachment[] = [];
    for (const f of list) {
      if (f.size > maxBytes) {
        alert(`${f.name} is too large (max ${kind === 'photo' ? '15 MB' : '50 MB'})`);
        continue;
      }
      const data = await fileToBase64(f);
      out.push({
        file_name: f.name,
        file_type: f.type || (kind === 'video' ? 'video/mp4' : 'image/jpeg'),
        file_size: f.size,
        media_type: kind,
        base64_data: data,
        description: '',
      });
    }
    if (kind === 'photo') setPhotos((p) => [...p, ...out]);
    else setVideos((p) => [...p, ...out]);
  };

  const removeAttachment = (kind: 'photo' | 'video', index: number) => {
    if (kind === 'photo') setPhotos((p) => p.filter((_, i) => i !== index));
    else setVideos((p) => p.filter((_, i) => i !== index));
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      const payload: any = { ...form };
      if (form.latitude) payload.latitude = parseFloat(form.latitude);
      if (form.longitude) payload.longitude = parseFloat(form.longitude);
      if (form.estimated_affected_population) payload.estimated_affected_population = parseInt(form.estimated_affected_population);
      if (form.estimated_affected_area_sqm) payload.estimated_affected_area_sqm = parseFloat(form.estimated_affected_area_sqm);
      const evidence = [...photos, ...videos];
      if (evidence.length) payload.evidence = evidence;
      const r = await api.submitPublicReport(payload);
      console.log('[PublicReportPage] Submission succeeded:', r);
      setResult({ tracking_code: r.tracking_code, hazard_id: r.hazard_id });
    } catch (e: any) {
      console.error('[PublicReportPage] Submission failed:', e);
      setError(e.message || 'Submission failed');
    } finally {
      setBusy(false);
    }
  };

  const goBack = () => {
    if (onBack) return onBack();
    window.history.pushState({}, '', '/');
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const copyTrackingCode = async () => {
    if (!result?.tracking_code) return;
    try {
      await navigator.clipboard.writeText(result.tracking_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Fallback for browsers without clipboard API
      const ta = document.createElement('textarea');
      ta.value = result.tracking_code;
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); setCopied(true); setTimeout(() => setCopied(false), 2500); } catch {}
      document.body.removeChild(ta);
    }
  };

  if (result) {
    return (
      <div className="min-h-screen bg-slate-950 text-white">
        <PublicUserBanner currentUser={currentUser} onSignOut={onSignOut} />
        <div className="flex items-center justify-center p-6">
          <div className="max-w-lg w-full rounded-2xl bg-emerald-950 border border-emerald-800 p-8 text-center shadow-2xl">
            <CheckCircle2 className="w-16 h-16 text-emerald-400 mx-auto mb-4" />
            <h1 className="text-2xl font-bold mb-2">Report Submitted</h1>
            <p className="text-sm text-emerald-200 mb-6">
              Your ecological hazard report has been received by the Ecological Fund Office.
            </p>

            <div className="rounded-xl bg-slate-900 border-2 border-amber-500/60 p-5 mb-6 shadow-inner">
              <div className="text-[11px] uppercase tracking-widest text-amber-400 font-bold mb-2">
                ⭐ Your Tracking Code
              </div>
              <div className="text-2xl sm:text-3xl font-mono font-black text-amber-300 break-all tracking-wider leading-tight">
                {result.tracking_code}
              </div>
              <div className="text-[11px] text-slate-400 mt-3">
                Hazard ID: <span className="font-mono text-slate-300">{result.hazard_id}</span>
              </div>
              <button
                type="button"
                onClick={copyTrackingCode}
                className={`mt-4 w-full inline-flex items-center justify-center gap-1.5 text-[11px] font-bold py-2 rounded-lg border transition-colors ${
                  copied
                    ? 'bg-emerald-900 border-emerald-600 text-emerald-200'
                    : 'bg-slate-800 border-slate-600 text-slate-200 hover:bg-slate-700 hover:border-slate-500'
                }`}
              >
                <Copy className="w-3.5 h-3.5" />
                {copied ? 'Copied to clipboard ✓' : 'Copy Tracking Code'}
              </button>
            </div>

            <div className="rounded-lg bg-amber-950/40 border border-amber-900 p-3 text-[11px] text-amber-200 text-left mb-5">
              <strong>Save this code.</strong> You can use it to check the status of your report without logging in.
              Bookmark the tracking page or take a screenshot.
            </div>

            <div className="flex gap-2">
              <button
                onClick={goBack}
                className="flex-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-semibold py-2.5"
              >
                Return Home
              </button>
              <button
                onClick={() => {
                  window.history.pushState({}, '', `/public/track/${result.tracking_code}`);
                  window.dispatchEvent(new PopStateEvent('popstate'));
                }}
                className="flex-1 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-emerald-950 font-bold py-2.5"
              >
                Track Status
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <PublicUserBanner currentUser={currentUser} onSignOut={onSignOut} />
      <div className="max-w-3xl mx-auto p-4 sm:p-6">
        <button onClick={goBack} className="flex items-center gap-2 text-slate-400 hover:text-white text-sm mb-4">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <div className="rounded-2xl bg-slate-900 border border-slate-700 p-6 sm:p-8 shadow-2xl">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 rounded-xl bg-amber-900/40 border border-amber-800 flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Report an Ecological Hazard</h1>
              <p className="text-xs text-slate-400">Edo State Ecological Fund Agency — Public Portal</p>
            </div>
          </div>
          <p className="text-sm text-slate-300 mt-4 mb-6">
            Report gully erosion, flooding, landslides, or any ecological hazard in your community.
            {currentUser
              ? ' Your report will be linked to your account so you can be notified of status changes.'
              : ' You do not need to log in. You will receive a tracking code to follow up.'}
          </p>

          {error && (
            <div className="rounded-lg bg-rose-950 border border-rose-800 text-rose-200 text-xs p-3 mb-4">
              {error}
            </div>
          )}

          <form onSubmit={submit} className="space-y-5">
            <div>
              <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-2">1. The Hazard</div>
              <div className="space-y-3">
                <label className="block text-xs font-semibold text-slate-300">
                  Short title *
                  <input required value={form.title} onChange={set('title')} maxLength={120}
                    placeholder="e.g. Deep gully at Ugbogui Road junction"
                    className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600" />
                </label>
                <div className="grid sm:grid-cols-2 gap-3">
                  <label className="block text-xs font-semibold text-slate-300">
                    Category *
                    <select value={form.category} onChange={set('category')}
                      className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600">
                      {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                  </label>
                  <label className="block text-xs font-semibold text-slate-300">
                    Severity (your estimate) *
                    <select value={form.severity} onChange={set('severity')}
                      className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600">
                      {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </label>
                </div>
                <label className="block text-xs font-semibold text-slate-300">
                  Description
                  <textarea value={form.description} onChange={set('description')} rows={4}
                    placeholder="Describe what you see, when it started, what is at risk…"
                    className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600 resize-y" />
                </label>
              </div>
            </div>

            <div>
              <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-2">2. Location</div>
              <div className="grid sm:grid-cols-2 gap-3">
                <label className="block text-xs font-semibold text-slate-300">
                  State *
                  <input value={form.state} onChange={set('state')}
                    className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600" />
                </label>
                <label className="block text-xs font-semibold text-slate-300">
                  LGA *
                  <select value={form.lga} onChange={set('lga')}
                    className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600">
                    {EDO_LGAS.map(l => <option key={l} value={l}>{l}</option>)}
                  </select>
                </label>
                <label className="block text-xs font-semibold text-slate-300">
                  Ward
                  <input value={form.ward} onChange={set('ward')} placeholder="e.g. Ward 3"
                    className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600" />
                </label>
                <label className="block text-xs font-semibold text-slate-300">
                  Community / Village
                  <input value={form.community} onChange={set('community')} placeholder="e.g. Ugbogui"
                    className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600" />
                </label>
              </div>
              <label className="block text-xs font-semibold text-slate-300 mt-3">
                Nearby landmark / address
                <input value={form.address_description} onChange={set('address_description')}
                  placeholder="e.g. Opposite the primary school on Ring Road"
                  className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600" />
              </label>
              <div className="grid sm:grid-cols-2 gap-3 mt-3">
                <label className="block text-xs font-semibold text-slate-300">
                  <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5" /> Latitude (optional)</span>
                  <input value={form.latitude} onChange={set('latitude')} placeholder="6.335"
                    className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600 font-mono text-sm" />
                </label>
                <label className="block text-xs font-semibold text-slate-300">
                  <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5" /> Longitude (optional)</span>
                  <input value={form.longitude} onChange={set('longitude')} placeholder="5.603"
                    className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600 font-mono text-sm" />
                </label>
              </div>
            </div>

            <div>
              <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-2">3. Impact (optional)</div>
              <div className="grid sm:grid-cols-2 gap-3">
                <label className="block text-xs font-semibold text-slate-300">
                  Estimated people affected
                  <input type="number" value={form.estimated_affected_population} onChange={set('estimated_affected_population')}
                    placeholder="e.g. 350"
                    className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600" />
                </label>
                <label className="block text-xs font-semibold text-slate-300">
                  Estimated area affected (m²)
                  <input type="number" value={form.estimated_affected_area_sqm} onChange={set('estimated_affected_area_sqm')}
                    placeholder="e.g. 5000"
                    className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600" />
                </label>
              </div>
            </div>

            <div>
              <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-2">
                4. Photographic &amp; Video Evidence
              </div>
              <div className="grid sm:grid-cols-2 gap-3">
                <div className="rounded-lg border border-dashed border-slate-600 bg-slate-800/40 p-3">
                  <button type="button" onClick={() => photoInputRef.current?.click()}
                    className="w-full flex items-center justify-center gap-2 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium">
                    <ImageIcon className="w-4 h-4" /> Add Photographs
                  </button>
                  <div className="text-[10px] text-slate-500 mt-1.5 text-center">JPG, PNG, WebP up to 15 MB each</div>
                  <input ref={photoInputRef} type="file" accept="image/*" multiple className="hidden"
                    onChange={(e) => { addFiles(e.target.files, 'photo'); if (photoInputRef.current) photoInputRef.current.value = ''; }} />
                </div>
                <div className="rounded-lg border border-dashed border-slate-600 bg-slate-800/40 p-3">
                  <button type="button" onClick={() => videoInputRef.current?.click()}
                    className="w-full flex items-center justify-center gap-2 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium">
                    <Video className="w-4 h-4" /> Add Video Recordings
                  </button>
                  <div className="text-[10px] text-slate-500 mt-1.5 text-center">MP4, WebM up to 50 MB each</div>
                  <input ref={videoInputRef} type="file" accept="video/*" multiple className="hidden"
                    onChange={(e) => { addFiles(e.target.files, 'video'); if (videoInputRef.current) videoInputRef.current.value = ''; }} />
                </div>
              </div>

              {photos.length > 0 && (
                <div className="mt-3">
                  <div className="text-[10px] uppercase tracking-wider text-slate-400 mb-2">Photos ({photos.length})</div>
                  <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                    {photos.map((p, i) => (
                      <div key={i} className="relative group rounded-lg overflow-hidden border border-slate-700">
                        <img src={p.base64_data} alt={p.file_name} className="w-full h-20 object-cover" />
                        <button type="button" onClick={() => removeAttachment('photo', i)}
                          className="absolute top-1 right-1 p-1 rounded bg-rose-600 hover:bg-rose-500 text-white opacity-0 group-hover:opacity-100 transition">
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {videos.length > 0 && (
                <div className="mt-3">
                  <div className="text-[10px] uppercase tracking-wider text-slate-400 mb-2">Videos ({videos.length})</div>
                  <div className="space-y-1">
                    {videos.map((v, i) => (
                      <div key={i} className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-800/40 px-3 py-2">
                        <div className="flex items-center gap-2 min-w-0">
                          <Video className="w-4 h-4 text-slate-400 shrink-0" />
                          <span className="text-xs text-slate-300 truncate">{v.file_name}</span>
                          <span className="text-[10px] text-slate-500 shrink-0">
                            {(v.file_size / 1024 / 1024).toFixed(1)} MB
                          </span>
                        </div>
                        <button type="button" onClick={() => removeAttachment('video', i)} className="text-rose-400 hover:text-rose-300 p-1">
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div>
              <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-2">5. Your Contact (optional)</div>
              <div className="grid sm:grid-cols-2 gap-3">
                <label className="block text-xs font-semibold text-slate-300">
                  Your name
                  <input
                    value={form.reporter_name || currentUser?.name || ''}
                    onChange={set('reporter_name')}
                    placeholder="Anonymous Citizen"
                    className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600" />
                </label>
                <label className="block text-xs font-semibold text-slate-300">
                  Phone or email
                  <input
                    value={form.reporter_contact || currentUser?.phone || currentUser?.email || ''}
                    onChange={set('reporter_contact')}
                    placeholder="+234…"
                    className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 outline-none focus:border-emerald-600" />
                </label>
              </div>
              <div className="text-[10px] text-slate-500 mt-2">
                {currentUser
                  ? 'You are signed in — your name and contact are pre-filled from your account.'
                  : 'You may leave these blank to report anonymously.'}
              </div>
            </div>

            <button type="submit" disabled={busy || !form.title}
              className="w-full rounded-lg bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-amber-950 font-bold py-3 flex items-center justify-center gap-2">
              <Send className="w-4 h-4" />
              {busy ? 'Submitting…' : `Submit Report${photos.length + videos.length ? ` (${photos.length + videos.length} file${photos.length + videos.length === 1 ? '' : 's'})` : ''}`}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};