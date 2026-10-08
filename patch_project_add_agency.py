import pathlib

p = pathlib.Path("src/components/projects/ProjectModal.tsx")
src = p.read_text(encoding="utf-8")

# Find the closing of the Funding Source <div> and add a new field after it
old_marker = """              <select
                value={formData.funding_source}
                onChange={e => setFormData({ ...formData, funding_source: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
              >
                {(referenceData?.funding_sources || [formData.funding_source]).map((fs: string) => (
                  <option key={fs} value={fs}>{fs}</option>
                ))}
              </select>
            </div>
          </div>"""

new_block = """              <select
                value={formData.funding_source}
                onChange={e => setFormData({ ...formData, funding_source: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
              >
                {(referenceData?.funding_sources || [formData.funding_source]).map((fs: string) => (
                  <option key={fs} value={fs}>{fs}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-800">Implementing Agency</label>
              <select
                value={formData.implementing_agency}
                onChange={e => setFormData({ ...formData, implementing_agency: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
              >
                {(referenceData?.implementing_agencies || [formData.implementing_agency]).map((a: string) => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>
            </div>
          </div>"""

if old_marker in src:
    src = src.replace(old_marker, new_block, 1)
    p.write_text(src, encoding="utf-8")
    print("Added Implementing Agency dropdown")
else:
    print("Marker pattern NOT FOUND — paste the Funding Source block")