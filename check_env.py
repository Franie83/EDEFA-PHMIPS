import os
from dotenv import load_dotenv
load_dotenv()

print("CWD:               ", os.getcwd())
print("GEMINI_API_KEY set:", bool(os.getenv("GEMINI_API_KEY")))
print("Key first 6:       ", (os.getenv("GEMINI_API_KEY") or "")[:6])
print("Key length:        ", len(os.getenv("GEMINI_API_KEY") or ""))
print("DATABASE_URL:      ", os.getenv("DATABASE_URL"))