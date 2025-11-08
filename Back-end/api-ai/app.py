import os, json, requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from rag_core import retrieve, ensure_index
from fpt_tts import synthesize_speech, get_available_voices

# === Load environment ===
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
RAG_LLM_MODEL = os.getenv("RAG_LLM_MODEL", "openai/gpt-4o-mini").strip()
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

app = Flask(__name__)

# Configure CORS to allow all origins and methods
CORS(app,
     resources={r"/*": {
         "origins": "*",
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "Accept"],
         "expose_headers": ["Content-Type"],
         "max_age": 3600
     }},
     supports_credentials=False)  # Set to False when using origins="*"

SYSTEM_PROMPT = (
    "Bạn là trợ lý AI thông minh của Bảo tàng Chứng tích Chiến tranh. "
    "Nhiệm vụ của bạn là trả lời MỌI câu hỏi về các hiện vật, hình ảnh, và lịch sử chiến tranh Việt Nam. "
    "Sử dụng CONTEXT được cung cấp để trả lời. Nếu CONTEXT không có thông tin cụ thể, "
    "hãy dựa vào kiến thức chung về chiến tranh Việt Nam để đưa ra câu trả lời hữu ích. "
    "KHÔNG BAO GIỜ từ chối trả lời hoặc nói 'không có thông tin'. "
    "Luôn cố gắng cung cấp thông tin hữu ích, thân thiện và tự nhiên. "
    "Nếu câu hỏi bằng tiếng Việt, trả lời bằng tiếng Việt. "
    "Nếu câu hỏi bằng tiếng Anh, trả lời bằng tiếng Anh. "
    "Tránh chính trị, luôn giữ thái độ nhân văn và khách quan."
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

@app.route("/api/health", methods=["GET", "OPTIONS"])
def health():
    return jsonify({"status": "ok", "model": RAG_LLM_MODEL})

@app.route("/api/ask", methods=["POST", "OPTIONS"])
def ask():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    data = request.get_json(force=True)
    # Accept both 'question' and 'message' for compatibility
    question = data.get("question") or data.get("message", "")
    question = question.strip()
    top_k = int(data.get("top_k", 6))
    max_tokens = int(data.get("max_tokens", 600))

    if not question:
        return jsonify({"error": "Thiếu trường 'question' hoặc 'message'"}), 400

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
        "response": answer,  # Add 'response' field for frontend compatibility
        "message": answer,   # Add 'message' field for frontend compatibility
        "citations": [
            {"name": h.get("meta", {}).get("name_vi"), "score": h["score"]}
            for h in hits
        ],
        "model": RAG_LLM_MODEL
    })

@app.route("/api/reindex", methods=["POST", "OPTIONS"])
def reindex():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    import shutil
    vec_dir = os.getenv("VECTOR_DIR", "./vectorstore")
    if os.path.exists(vec_dir):
        shutil.rmtree(vec_dir)
    ensure_index()
    return jsonify({"status": "done"})

@app.route("/api/tts", methods=["POST", "OPTIONS"])
def text_to_speech():
    """
    Convert text to speech using FPT.AI
    Request body: { "text": "...", "voice": "banmai", "speed": 0 }
    """
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    voice = data.get("voice", "banmai")
    speed = int(data.get("speed", 0))

    if not text:
        return jsonify({"error": "Missing 'text' field"}), 400

    result = synthesize_speech(text, voice=voice, speed=speed)

    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route("/api/tts/voices", methods=["GET", "OPTIONS"])
def list_voices():
    """
    Get list of available Vietnamese voices
    """
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    voices = get_available_voices()
    return jsonify({
        "voices": [
            {"code": code, "name": name}
            for code, name in voices.items()
        ]
    })

if __name__ == "__main__":
    print(f"🚀 Running on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT)
