import pathlib

# --- Fix app.py ---
p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")
changes = []

old_model = 'model=os.getenv("GEMINI_MODEL","gemini-2.5-flash")'
new_model = 'model=os.getenv("GEMINI_MODEL","gemini-3.8-flash")'
if old_model in src:
    src = src.replace(old_model, new_model)
    changes.append("model default -> gemini-3.8-flash")
elif new_model in src:
    changes.append("model default already gemini-3.8-flash")

old_exc = '  except Exception as exc:\n   logger.warning("Gemini query failed: %s",exc)'
new_exc = (
    '  except Exception as exc:\n'
    '   import traceback\n'
    '   print(f"[GEMINI ERROR] {type(exc).__name__}: {exc}", flush=True)\n'
    '   traceback.print_exc()'
)
if old_exc in src:
    src = src.replace(old_exc, new_exc)
    changes.append("added visible Gemini error traceback")
elif "[GEMINI ERROR]" in src:
    changes.append("error traceback already visible")

p.write_text(src, encoding="utf-8")
print("app.py changes:", changes)

# --- Fix .env ---
env = pathlib.Path(".env")
env_src = env.read_text(encoding="utf-8")
if "GEMINI_MODEL=" not in env_src:
    if not env_src.endswith("\n"):
        env_src += "\n"
    env_src += "GEMINI_MODEL=gemini-3.8-flash\n"
    env.write_text(env_src, encoding="utf-8")
    print(".env: added GEMINI_MODEL=gemini-3.8-flash")
else:
    # Replace whatever value is there
    import re
    env_src = re.sub(r'GEMINI_MODEL=.*', 'GEMINI_MODEL=gemini-3.8-flash', env_src)
    env.write_text(env_src, encoding="utf-8")
    print(".env: GEMINI_MODEL set to gemini-3.8-flash")