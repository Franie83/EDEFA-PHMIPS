import pathlib
import re

p = pathlib.Path("src/components/hazards/HazardReportModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Remove the Leaflet imports
src = src.replace(
    "\nimport 'leaflet/dist/leaflet.css';\nimport L from 'leaflet';",
    ""
)
changes.append("removed leaflet imports")

# 2. Remove the MapPicker component
# It starts with "// Inline Leaflet map picker" and ends before "export const HazardReportModal"
pattern = re.compile(
    r"\n// =+\n// Inline Leaflet map picker.*?\n};\n\n(?=export const HazardReportModal)",
    re.DOTALL
)
src, n = pattern.subn("\n", src)
if n:
    changes.append(f"removed MapPicker component ({n} match)")
else:
    # Fallback: try a simpler cut
    start = src.find("// Inline Leaflet map picker")
    end = src.find("export const HazardReportModal")
    if start > 0 and end > start:
        # find the start of the comment line
        line_start = src.rfind("\n", 0, start) + 1
        src = src[:line_start] + src[end:]
        changes.append("removed MapPicker (fallback cut)")
    else:
        changes.append("MapPicker NOT FOUND — no removal needed")

# 3. Revert the GPS button block back to its pre-map form
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

if new_gps_block in src:
    src = src.replace(new_gps_block, old_gps_block)
    changes.append("reverted GPS button block")
else:
    changes.append("GPS button revert pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)

# Sanity check
remaining = src.count("MapPicker") + src.count("leaflet")
print(f"\nRemaining 'MapPicker'/'leaflet' references: {remaining}")