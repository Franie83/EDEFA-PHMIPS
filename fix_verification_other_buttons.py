import pathlib

p = pathlib.Path("src/components/verification/VerificationWorkspace.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# ---------- Assessment submit button (lines 585-592) ----------
old_assess = """                <button
                  type="submit"
                  disabled={isAssessing}
                  className="px-5 py-2 rounded-lg text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white inline-flex items-center transition-colors"
                >
                  <Compass className="w-4 h-4 mr-1.5" />
                  {isAssessing ? 'Recording...' : 'Commit Technical Assessment & Move to Formulation'}
                </button>"""

new_assess = """                <button
                  type="submit"
                  disabled={isAssessing || stage !== 'ASSESSMENT'}
                  className="px-5 py-2 rounded-lg text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white inline-flex items-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title={stage !== 'ASSESSMENT' ? (stage === 'VERIFICATION' ? 'Hazard not yet verified' : 'Assessment already completed') : ''}
                >
                  <Compass className="w-4 h-4 mr-1.5" />
                  {isAssessing
                    ? 'Recording...'
                    : stage === 'ASSESSMENT'
                      ? 'Commit Technical Assessment & Move to Formulation'
                      : stage === 'VERIFICATION'
                        ? 'Verify hazard first'
                        : '✓ Assessment Recorded'}
                </button>"""

if old_assess in src:
    src = src.replace(old_assess, new_assess)
    changes.append("disabled Assessment submit when step already done")
else:
    changes.append("Assessment button pattern NOT FOUND")

# ---------- Intervention submit button (lines 712-719) ----------
old_interv = """                <button
                  type="submit"
                  disabled={isSavingIntervention}
                  className="px-5 py-2 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center transition-colors"
                >
                  <Send className="w-4 h-4 mr-1.5" />
                  {isSavingIntervention ? 'Saving...' : 'Register Intervention in National Pipeline'}
                </button>"""

new_interv = """                <button
                  type="submit"
                  disabled={isSavingIntervention || stage !== 'INTERVENTION'}
                  className="px-5 py-2 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title={stage !== 'INTERVENTION' ? (stage === 'DONE' ? 'Intervention already registered' : 'Assessment required first') : ''}
                >
                  <Send className="w-4 h-4 mr-1.5" />
                  {isSavingIntervention
                    ? 'Saving...'
                    : stage === 'INTERVENTION'
                      ? 'Register Intervention in National Pipeline'
                      : stage === 'DONE'
                        ? '✓ Intervention Already Registered'
                        : 'Assessment required first'}
                </button>"""

if old_interv in src:
    src = src.replace(old_interv, new_interv)
    changes.append("disabled Intervention submit when step already done")
else:
    changes.append("Intervention button pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)