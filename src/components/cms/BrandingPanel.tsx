import React, { useEffect, useRef, useState } from 'react';
import { Save, Upload, X } from 'lucide-react';
import { api } from '../../services/api';

type Branding = {
  app_name: string;
  app_tagline: string;
  agency_name: string;
  footer_text: string;
  primary_color: string;
  logo_url: string;
};

const DEFAULTS: Branding = {
  app_name: 'EDEFA-PHMIPS',
  app_tagline: 'Ecological Fund Project & Hazard Management',
  agency_name: 'Edo State Ecological Fund Agency',
  footer_text: '(c) Edo State Ecological Fund Agency',
  primary_color: '#0F5132',
  logo_url: '',
};

export const BrandingPanel: React.FC = () => {
  const [form, setForm] = useState<Branding>(DEFAULTS);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [logoBase64, setLogoBase64] = useState<string>('');
  const [logoMime, setLogoMime] = useState<string>('');
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api
      .cmsBranding()
      .then((b) => setForm({ ...DEFAULTS, ...b }))
      .catch((e) => alert(e.message || 'Failed to load branding'))
      .finally(() => setLoading(false));
  }, []);

  const onPick = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 2 * 1024 * 1024) {
      alert('Logo must be under 2 MB');
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const result = String(reader.result || '');
      setLogoBase64(result);
      setLogoMime(f.type);
    };
    reader.readAsDataURL(f);
  };

  const save = async () => {
    setSaving(true);
    try {
      const payload: any = { ...form };
      if (logoBase64) {
        payload.logo_base64 = logoBase64;
        payload.logo_mime = logoMime;
      }
      const updated = await api.cmsUpdateBranding(payload);
      setForm({ ...DEFAULTS, ...updated });
      setLogoBase64('');
      setLogoMime('');
      if (fileRef.current) fileRef.current.value = '';
      alert('Branding saved.');
      window.dispatchEvent(new CustomEvent('branding-updated', { detail: updated }));
    } catch (e: any) {
      alert(e.message || 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-6 text-slate-400 text-sm">Loading branding…</div>;
  }

  const preview = logoBase64 || form.logo_url;

  return (
    <div className="p-6 space-y-5 max-w-3xl">
      <div>
        <h3 className="text-lg font-semibold text-white mb-1">Application Branding</h3>
        <p className="text-xs text-slate-400">
          Change app name, tagline, logo, and colours without editing code.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Field label="Application Name">
          <input
            type="text"
            value={form.app_name}
            onChange={(e) => setForm({ ...form, app_name: e.target.value })}
            className="cms-input"
          />
        </Field>

        <Field label="Agency Name">
          <input
            type="text"
            value={form.agency_name}
            onChange={(e) => setForm({ ...form, agency_name: e.target.value })}
            className="cms-input"
          />
        </Field>

        <Field label="Tagline" full>
          <input
            type="text"
            value={form.app_tagline}
            onChange={(e) => setForm({ ...form, app_tagline: e.target.value })}
            className="cms-input"
          />
        </Field>

        <Field label="Footer Text" full>
          <input
            type="text"
            value={form.footer_text}
            onChange={(e) => setForm({ ...form, footer_text: e.target.value })}
            className="cms-input"
          />
        </Field>

        <Field label="Primary Colour">
          <div className="flex items-center gap-3">
            <input
              type="color"
              value={form.primary_color}
              onChange={(e) => setForm({ ...form, primary_color: e.target.value })}
              className="w-12 h-10 rounded border border-slate-700 bg-slate-900 cursor-pointer"
            />
            <input
              type="text"
              value={form.primary_color}
              onChange={(e) => setForm({ ...form, primary_color: e.target.value })}
              className="cms-input flex-1"
            />
          </div>
        </Field>

        <Field label="Logo">
          <div className="flex items-center gap-3">
            {preview && (
              <img
                src={preview}
                alt="logo"
                className="h-10 w-10 rounded object-contain bg-slate-800 border border-slate-700"
              />
            )}
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              className="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 text-xs"
            >
              <Upload className="w-3.5 h-3.5" /> Upload Logo
            </button>
            {logoBase64 && (
              <button
                type="button"
                onClick={() => {
                  setLogoBase64('');
                  setLogoMime('');
                  if (fileRef.current) fileRef.current.value = '';
                }}
                className="text-slate-500 hover:text-rose-400"
              >
                <X className="w-4 h-4" />
              </button>
            )}
            <input
              ref={fileRef}
              type="file"
              accept="image/png,image/jpeg,image/svg+xml"
              onChange={onPick}
              className="hidden"
            />
          </div>
        </Field>
      </div>

      <div className="flex justify-end pt-3 border-t border-slate-800">
        <button
          onClick={save}
          disabled={saving}
          className="flex items-center gap-2 px-5 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-sm font-medium disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {saving ? 'Saving…' : 'Save Branding'}
        </button>
      </div>
    </div>
  );
};

const Field: React.FC<{ label: string; full?: boolean; children: React.ReactNode }> = ({
  label,
  full,
  children,
}) => (
  <label className={`block ${full ? 'md:col-span-2' : ''}`}>
    <span className="block text-xs font-medium text-slate-400 mb-1.5">{label}</span>
    {children}
  </label>
);