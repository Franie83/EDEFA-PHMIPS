import pathlib

p = pathlib.Path("src/components/verification/VerificationWorkspace.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# ---------- 1. Fix stageOf to also check `intervention` ----------
old_stage = "    if (hz.recommended_intervention) return 'DONE';"
new_stage = "    if (hz.recommended_intervention || hz.intervention) return 'DONE';"
if old_stage in src:
    src = src.replace(old_stage, new_stage)
    changes.append("stageOf: also checks hz.intervention")

# ---------- 2. Insert the stage banner just after the tabs div ----------
# The tabs div ends at line 289-290 with `</div>` then `</div>` then `)}`
# We insert the banner AFTER the whole tabs container, at the top of the content region.
old_tabs_close = """                >
                  3. Formulation
                </button>
              </div>
            </div>
          )}"""
new_tabs_close = """                >
                  3. Formulation
                </button>
              </div>
            </div>
          )}

          {/* Stage banner */}
          {selectedHazard && (
            <div className={`mx-6 mt-4 rounded-xl border px-4 py-3 text-xs flex items-center justify-between ${
              stage === 'VERIFICATION' ? 'bg-amber-50 border-amber-200 text-amber-900' :
              stage === 'ASSESSMENT' ? 'bg-blue-50 border-blue-200 text-blue-900' :
              stage === 'INTERVENTION' ? 'bg-purple-50 border-purple-200 text-purple-900' :
              'bg-emerald-50 border-emerald-200 text-emerald-900'
            }`}>
              <div className="flex items-center gap-2">
                <Info className="w-4 h-4 shrink-0" />
                <span className="font-semibold">{stageLabel[stage]}</span>
              </div>
              {stage === 'DONE' && (
                <span className="font-mono text-[11px] opacity-80">
                  Intervention: {(selectedHazard as any)?.recommended_intervention?.intervention_id || (selectedHazard as any)?.intervention?.id || '—'}
                </span>
              )}
            </div>
          )}"""
if old_tabs_close in src and "Stage banner" not in src:
    src = src.replace(old_tabs_close, new_tabs_close)
    changes.append("inserted stage banner")
else:
    changes.append("tab close pattern NOT FOUND or already patched")

# ---------- 3. Disable Verification submit if not on VERIFICATION stage ----------
old_v_btn = """                <button
                  type="submit"
                  disabled={isVerifying}
                  className="px-5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white disabled:opacity-50 inline-flex items-center"
                >
                  <CheckSquare className="w-4 h-4 mr-1.5" />
                  {isVerifying ? 'Saving...' : 'Submit Verification & Proceed to Assessment'}
                </button>"""
new_v_btn = """                <button
                  type="submit"
                  disabled={isVerifying || stage !== 'VERIFICATION'}
                  className="px-5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center"
                  title={stage !== 'VERIFICATION' ? 'Already verified — see status banner' : ''}
                >
                  <CheckSquare className="w-4 h-4 mr-1.5" />
                  {isVerifying
                    ? 'Saving...'
                    : stage === 'VERIFICATION'
                      ? 'Submit Verification & Proceed to Assessment'
                      : '✓ Already Verified'}
                </button>"""
if old_v_btn in src:
    src = src.replace(old_v_btn, new_v_btn)
    changes.append("disabled Verification submit when step already done")
else:
    changes.append("verification submit pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)