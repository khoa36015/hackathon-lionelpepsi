import os, json, requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from rag_core import retrieve, ensure_index

# === Load environment ===
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
RAG_LLM_MODEL = os.getenv("RAG_LLM_MODEL", "openai/gpt-4o-mini").strip()
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

app = Flask(__name__)
CORS(app)

SYSTEM_PROMPT = (
    "You are a bilingual (Vietnamese/English) museum AI guide. "
    "Answer strictly based on the provided CONTEXT. "
    "Be friendly, natural, and youthful. "
    "If the question is in Vietnamese, answer in Vietnamese; "
    "if in English, answer in English. "
    "Avoid politics and always stay humane."
)

def call_openrouter(messages, max_tokens=600, temperature=0.3):
    """
    Gọi OpenRouter API với headers đầy đủ.
    Nếu key sai hoặc hết hạn → trả lỗi rõ ràng.
    """
    if not OPENROUTER_API_KEY:
        return "⚠️ OPENROUTER_API_KEY chưa được thiết lập. Hãy thêm vào file .env"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "RAG Museum AI",
    }

    payload = {
        "model": RAG_LLM_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers, json=payload, timeout=60
        )
        if not resp.ok:
            # Trả về lỗi gốc để debug nhanh
            return f"❌ OpenRouter {resp.status_code}: {resp.text}"
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Lỗi gọi OpenRouter: {str(e)}"

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": RAG_LLM_MODEL})

@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    question = data.get("question", "").strip()
    top_k = int(data.get("top_k", 6))
    max_tokens = int(data.get("max_tokens", 600))

    if not question:
        return jsonify({"error": "Thiếu trường 'question'"}), 400

    # Retrieve context
    hits = retrieve(question, top_k=top_k)
    context_blocks = []
    for h in hits:
        meta = h.get("meta", {})
        label = meta.get("name_vi") or meta.get("title_vi") or meta.get("section")
        context_blocks.append(f"- [{label}] {h['text']}")

    context_str = "\n".join(context_blocks)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"CONTEXT:\n{context_str}\n\nQUESTION: {question}"}
    ]

    answer = call_openrouter(messages, max_tokens=max_tokens)
    return jsonify({
        "question": question,
        "answer": answer,
        "citations": [
            {"name": h.get("meta", {}).get("name_vi"), "score": h["score"]}
            for h in hits
        ],
        "model": RAG_LLM_MODEL
    })

@app.route("/api/reindex", methods=["POST"])
def reindex():
    import shutil
    vec_dir = os.getenv("VECTOR_DIR", "./vectorstore")
    if os.path.exists(vec_dir):
        shutil.rmtree(vec_dir)
    ensure_index()
    return jsonify({"status": "done"})

if __name__ == "__main__":
    print(f"🚀 Running on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT)
