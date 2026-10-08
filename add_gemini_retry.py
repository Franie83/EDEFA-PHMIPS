import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

old = '''  try:
   from google import genai
   client=genai.Client(api_key=key); compact=[{k:x.get(k) for k in ("id","title","category","state","lga","severity","urgency","status","priority_score")} for x in hs]
   prompt=f"Answer the user's operational query using only these records. Return JSON with answer, matching_hazard_ids, suggested_filters, risk_summary. User query: {q}\\nRecords: {json.dumps(compact)}"
   resp=client.models.generate_content(model=os.getenv("GEMINI_MODEL","gemini-3.8-flash"),contents=prompt,config={"response_mime_type":"application/json"})
   out=json.loads(resp.text or "{}")
   matched=[x for x in hs if x.get("id") in set(out.get("matching_hazard_ids",[]))]
   return jsonify({"success":True,"query":q,**out,"matched_records":matched,"is_ai_powered":True})'''

new = '''  try:
   import time as _time
   from google import genai
   from google.genai.errors import ServerError as _GeminiServerError
   client=genai.Client(api_key=key); compact=[{k:x.get(k) for k in ("id","title","category","state","lga","severity","urgency","status","priority_score")} for x in hs]
   prompt=f"Answer the user's operational query using only these records. Return JSON with answer, matching_hazard_ids, suggested_filters, risk_summary. User query: {q}\\nRecords: {json.dumps(compact)}"
   _model=os.getenv("GEMINI_MODEL","gemini-3.8-flash")
   resp=None; _last_exc=None
   for _attempt in range(1, 7):
    try:
     resp=client.models.generate_content(model=_model,contents=prompt,config={"response_mime_type":"application/json"})
     break
    except _GeminiServerError as _e:
     _last_exc=_e
     print(f"[GEMINI RETRY] attempt {_attempt} got 503, sleeping 3s", flush=True)
     _time.sleep(3)
   if resp is None:
    raise _last_exc or RuntimeError("Gemini unavailable after retries")
   out=json.loads(resp.text or "{}")
   matched=[x for x in hs if x.get("id") in set(out.get("matching_hazard_ids",[]))]
   return jsonify({"success":True,"query":q,**out,"matched_records":matched,"is_ai_powered":True})'''

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Patched app.py — added retry loop (6 attempts, 3s apart)")
elif "GEMINI RETRY" in src:
    print("Already patched.")
else:
    print("Pattern not found. Manual edit needed around line 1291-1301.")
    print("Current lines 1291-1301:")
    for i, line in enumerate(src.splitlines(), 1):
        if 1291 <= i <= 1301:
            print(f"  {i}: {line}")