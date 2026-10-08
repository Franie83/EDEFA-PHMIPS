import pathlib

p = pathlib.Path("src/components/hazards/HazardReportModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Rewrite handleDetectGps to accept a minAccuracy parameter
old_fn = """  const handleDetectGps = async () => {
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

new_fn = """  const handleDetectGps = async (opts: { auto?: boolean } = {}) => {
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
  }, [isOpen]);"""

if old_fn in src:
    src = src.replace(old_fn, new_fn)
    changes.append("upgraded handleDetectGps with accuracy filter + auto-trigger")
else:
    changes.append("handleDetectGps pattern NOT FOUND")

# 2. Update the button to pass no options (manual click still works)
old_btn = """                onClick={handleDetectGps}"""
new_btn = """                onClick={() => handleDetectGps()}"""
if old_btn in src:
    src = src.replace(old_btn, new_btn, 1)
    changes.append("button click still calls handleDetectGps()")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)