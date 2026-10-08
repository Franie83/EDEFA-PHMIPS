import os
import time
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai.errors import ServerError

key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
client = genai.Client(api_key=key)

for attempt in range(1, 21):
    try:
        print(f"[{attempt}/20] Calling {model}...", flush=True)
        r = client.models.generate_content(
            model=model,
            contents="Say hello in one word."
        )
        print("RESPONSE:", r.text)
        break
    except ServerError as e:
        print(f"  -> 503 / ServerError, retrying in 5s... ({e})", flush=True)
        time.sleep(5)
    except Exception as e:
        print(f"  -> Non-retryable error: {type(e).__name__}: {e}")
        break
else:
    print("Gave up after 20 attempts.")