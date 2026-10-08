import pathlib

p = pathlib.Path("src/components/hazards/HazardReportModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Change defaults from hardcoded to blank
old_defaults = """    latitude: 6.2209,
    longitude: 7.0722,"""
new_defaults = """    latitude: '' as any,
    longitude: '' as any,"""
if old_defaults in src:
    src = src.replace(old_defaults, new_defaults, 1)
    changes.append("cleared default lat/lng")
else:
    changes.append("default lat/lng pattern NOT FOUND")

# 2. Change edit-mode fallback too
old_edit = """      latitude: editHazard.latitude ?? 6.2209,"""
new_edit = """      latitude: editHazard.latitude ?? ('' as any),"""
if old_edit in src:
    src = src.replace(old_edit, new_edit)
    changes.append("edit-mode lat fallback updated")

old_edit_lng = """      longitude: editHazard.longitude ?? 7.0722,"""
new_edit_lng = """      longitude: editHazard.longitude ?? ('' as any),"""
if old_edit_lng in src:
    src = src.replace(old_edit_lng, new_edit_lng)
    changes.append("edit-mode lng fallback updated")

# 3. Make the number inputs accept blank values
old_lat_input = """                <input
                  type="number"
                  step="0.000001"
                  value={formData.latitude}
                  onChange={e => handleFieldChange('latitude', parseFloat(e.target.value) || 0)}"""
new_lat_input = """                <input
                  type="number"
                  step="0.000001"
                  placeholder="Auto-fill via GPS"
                  value={formData.latitude}
                  onChange={e => handleFieldChange('latitude', e.target.value)}"""
if old_lat_input in src:
    src = src.replace(old_lat_input, new_lat_input)
    changes.append("lat input allows blank")
else:
    changes.append("lat input pattern NOT FOUND (may need manual edit)")

old_lng_input = """                <input
                  type="number"
                  step="0.000001"
                  value={formData.longitude}
                  onChange={e => handleFieldChange('longitude', parseFloat(e.target.value) || 0)}"""
new_lng_input = """                <input
                  type="number"
                  step="0.000001"
                  placeholder="Auto-fill via GPS"
                  value={formData.longitude}
                  onChange={e => handleFieldChange('longitude', e.target.value)}"""
if old_lng_input in src:
    src = src.replace(old_lng_input, new_lng_input)
    changes.append("lng input allows blank")
else:
    changes.append("lng input pattern NOT FOUND (may need manual edit)")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)