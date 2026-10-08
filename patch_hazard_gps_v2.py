import pathlib

p = pathlib.Path("src/components/hazards/HazardReportModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# ---------- 1. Clear hardcoded lat/lng defaults ----------
if "latitude: 6.2209," in src:
    src = src.replace("    latitude: 6.2209,\n    longitude: 7.0722,",
                      "    latitude: '' as any,\n    longitude: '' as any,", 1)
    changes.append("cleared default lat/lng")

if "latitude: editHazard.latitude ?? 6.2209," in src:
    src = src.replace("      latitude: editHazard.latitude ?? 6.2209,",
                      "      latitude: editHazard.latitude ?? ('' as any),")
    changes.append("cleared edit-mode lat fallback")

if "longitude: editHazard.longitude ?? 7.0722," in src:
    src = src.replace("      longitude: editHazard.longitude ?? 7.0722,",
                      "      longitude: editHazard.longitude ?? ('' as any),")
    changes.append("cleared edit-mode lng fallback")

# ---------- 2. Add gpsAccuracy state (keep statusMessage, add accuracy) ----------
old_state = """  const [gpsDetecting, setGpsDetecting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);"""
new_state = """  const [gpsDetecting, setGpsDetecting] = useState(false);
  const [gpsAccuracy, setGpsAccuracy] = useState<number | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);"""
if old_state in src and "gpsAccuracy" not in src:
    src = src.replace(old_state, new_state)
    changes.append("added gpsAccuracy state")

# ---------- 3. Replace the whole handleDetectGps ----------
old_fn = """  const handleDetectGps = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      return;
    }
    setGpsDetecting(true);
    navigator.geolocation.getCurrentPosition(
      pos => {
        setFormData(prev => ({
          ...prev,
          latitude: parseFloat(pos.coords.latitude.toFixed(6)),
          longitude: parseFloat(pos.coords.longitude.toFixed(6))
        }));
        setGpsDetecting(false);
        setStatusMessage('GPS coordinates updated accurately.');
      },
      err => {
        console.warn(err);
        setGpsDetecting(false);
        alert('Could not acquire GPS position. You may type coordinates manually.');
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };"""

new_fn = """  const handleDetectGps = async () => {
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
      setFormData(prev => ({
        ...prev,
        latitude: parseFloat(pos.coords.latitude.toFixed(6)),
        longitude: parseFloat(pos.coords.longitude.toFixed(6))
      }));
      const acc = Math.round(pos.coords.accuracy);
      setGpsAccuracy(acc);
      setStatusMessage(`Location captured — accuracy ±${acc} m`);
    } catch (err: any) {
      const msg =
        err?.code === 1 ? 'Permission denied — enable location in browser settings.' :
        err?.code === 2 ? 'Location unavailable — check that device GPS is on.' :
        err?.code === 3 ? 'GPS timed out — try again outdoors or enter coordinates manually.' :
        'Unable to detect location — you may type coordinates manually.';
      setStatusMessage(msg);
    } finally {
      setGpsDetecting(false);
    }
  };"""

if old_fn in src:
    src = src.replace(old_fn, new_fn)
    changes.append("upgraded handleDetectGps with accuracy + error codes")

# ---------- 4. Add submit-time coordinate validation ----------
old_submit = """    if (!formData.title || !formData.community || !formData.reporter_name) {
      alert('Please fill out the required title, community, and reporter name fields.');
      return;
    }"""
new_submit = """    if (!formData.title || !formData.community || !formData.reporter_name) {
      alert('Please fill out the required title, community, and reporter name fields.');
      return;
    }
    if (formData.latitude === '' || formData.longitude === '' || formData.latitude === null || formData.longitude === null) {
      alert('Coordinates are required. Click "Detect Coordinates (Device GPS)" or enter them manually.');
      return;
    }"""
if old_submit in src:
    src = src.replace(old_submit, new_submit)
    changes.append("added coordinate validation on submit")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)