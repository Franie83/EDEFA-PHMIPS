import pathlib

p = pathlib.Path("src/components/hazards/HazardReportModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add Leaflet import at the top of the file
if "leaflet/dist/leaflet.css" not in src:
    marker = "import { offlineDrafts } from '../../services/api.ts';"
    if marker in src:
        src = src.replace(
            marker,
            marker + "\nimport 'leaflet/dist/leaflet.css';\nimport L from 'leaflet';"
        )
        changes.append("added leaflet import + CSS")
    else:
        changes.append("leaflet import anchor NOT FOUND")

# 2. Add the MapPicker component just before the main modal export
map_component = '''

// ============================================================
// Inline Leaflet map picker — click anywhere to drop a pin
// ============================================================
const MapPicker: React.FC<{
  lat: number | string;
  lng: number | string;
  onPick: (lat: number, lng: number) => void;
}> = ({ lat, lng, onPick }) => {
  const containerRef = React.useRef<HTMLDivElement | null>(null);
  const mapRef = React.useRef<any>(null);
  const markerRef = React.useRef<any>(null);

  React.useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const defaultLat = typeof lat === 'number' && !isNaN(lat) ? lat : 6.335;
    const defaultLng = typeof lng === 'number' && !isNaN(lng) ? lng : 5.603;

    const map = L.map(containerRef.current, {
      center: [defaultLat, defaultLng],
      zoom: 8,
      attributionControl: false,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '© OpenStreetMap contributors',
    }).addTo(map);

    map.on('click', (e: any) => {
      onPick(
        parseFloat(e.latlng.lat.toFixed(6)),
        parseFloat(e.latlng.lng.toFixed(6))
      );
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update marker when lat/lng changes externally (e.g. GPS button)
  React.useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const nlat = typeof lat === 'number' ? lat : parseFloat(String(lat));
    const nlng = typeof lng === 'number' ? lng : parseFloat(String(lng));
    if (isNaN(nlat) || isNaN(nlng)) {
      if (markerRef.current) {
        markerRef.current.remove();
        markerRef.current = null;
      }
      return;
    }
    if (markerRef.current) {
      markerRef.current.setLatLng([nlat, nlng]);
    } else {
      markerRef.current = L.marker([nlat, nlng]).addTo(map);
    }
    map.setView([nlat, nlng], Math.max(map.getZoom(), 12), { animate: true });
  }, [lat, lng]);

  return (
    <div
      ref={containerRef}
      style={{ width: '100%', height: '280px', borderRadius: '0.75rem' }}
      className="border border-slate-200 overflow-hidden"
    />
  );
};

'''

if "MapPicker" not in src:
    marker2 = "export const HazardReportModal: React.FC<HazardReportModalProps> = ({"
    if marker2 in src:
        src = src.replace(marker2, map_component + marker2)
        changes.append("inserted MapPicker component")
    else:
        changes.append("MapPicker insert anchor NOT FOUND")
else:
    changes.append("MapPicker already present")

# 3. Add the map inside the form — after the Detect GPS button block
old_gps_block = """              <button
                type="button"
                onClick={handleDetectGps}
                disabled={gpsDetecting}
                className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-100 hover:bg-emerald-200 text-emerald-800 transition-colors"
              >
                <Compass className={`w-4 h-4 mr-1.5 ${gpsDetecting ? 'animate-spin' : ''}`} />
                {gpsDetecting ? 'Detecting device GPS...' : 'Detect Coordinates (Device GPS)'}
              </button>
              <span className="text-[11px] text-slate-400">
                Coordinates will center point on national GIS map
              </span>
            </div>"""

new_gps_block = """              <button
                type="button"
                onClick={handleDetectGps}
                disabled={gpsDetecting}
                className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-100 hover:bg-emerald-200 text-emerald-800 transition-colors"
              >
                <Compass className={`w-4 h-4 mr-1.5 ${gpsDetecting ? 'animate-spin' : ''}`} />
                {gpsDetecting ? 'Detecting device GPS...' : 'Detect Coordinates (Device GPS)'}
              </button>
              <span className="text-[11px] text-slate-400">
                Or click on the map below to drop a pin
              </span>
            </div>

            {/* Interactive map picker */}
            <div className="mt-3">
              <MapPicker
                lat={formData.latitude}
                lng={formData.longitude}
                onPick={(nlat, nlng) => {
                  setFormData(prev => ({
                    ...prev,
                    latitude: nlat,
                    longitude: nlng,
                  }));
                  setStatusMessage(`Pin dropped at ${nlat}, ${nlng}`);
                }}
              />
            </div>"""

if old_gps_block in src:
    src = src.replace(old_gps_block, new_gps_block)
    changes.append("inserted interactive map picker into form")
else:
    changes.append("GPS button block NOT FOUND — paste it here to adjust")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)