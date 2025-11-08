python - << 'PY'
import os; from dotenv import load_dotenv; load_dotenv()
k=os.getenv("OPENROUTER_API_KEY",""); print("Key loaded?:", bool(k), "len:", len(k))
print("Model:", os.getenv("RAG_LLM_MODEL"))
PY