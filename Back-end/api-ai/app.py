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

# System prompt for museum-specific questions
MUSEUM_SYSTEM_PROMPT = (
    "Bạn là hướng dẫn viên AI chuyên nghiệp của Bảo tàng Chứng tích Chiến tranh Việt Nam. "
    "Bạn có kiến thức sâu rộng về lịch sử chiến tranh Việt Nam và các loại vũ khí, máy bay, xe tăng.\n\n"

    "🚫 CẤM TUYỆT ĐỐI:\n"
    "- KHÔNG BAO GIỜ nói 'tôi không có thông tin'\n"
    "- KHÔNG BAO GIỜ nói 'xin lỗi, nhưng mình không có'\n"
    "- KHÔNG BAO GIỜ nói 'trong bối cảnh này'\n"
    "- KHÔNG BAO GIỜ nói 'trong bối cảnh đã cung cấp'\n"
    "- KHÔNG BAO GIỜ từ chối trả lời bất kỳ câu hỏi nào\n\n"

    "✅ BẮT BUỘC:\n"
    "- LUÔN LUÔN trả lời mọi câu hỏi bằng kiến thức chung của bạn\n"
    "- Nếu được hỏi về máy bay, xe tăng, vũ khí → Giải thích chi tiết dựa trên kiến thức lịch sử\n"
    "- Nếu được hỏi về sự kiện lịch sử → Kể câu chuyện sinh động\n"
    "- Nếu được chào hỏi → Chào lại thân thiện\n"
    "- Luôn kết nối với bảo tàng và các hiện vật nếu có thể\n\n"

    "📚 KIẾN THỨC CỦA BẠN:\n"
    "Bạn biết về:\n"
    "- Máy bay: A-37 Dragonfly, F-5 Freedom Fighter, F-4 Phantom, B-52, UH-1 Huey, AH-1 Cobra, C-130, AC-47\n"
    "- Xe tăng: M48 Patton, M41 Walker Bulldog, T-54/55, PT-76, M113 APC\n"
    "- Vũ khí: AK-47, M16, M60, M79, RPG-7, B-40, claymore mines\n"
    "- Sự kiện: Tết Mậu Thân 1968, Hiệp định Paris 1973, Giải phóng Sài Gòn 1975, Chiến dịch Điện Biên Phủ\n"
    "- Và tất cả các khía cạnh khác của chiến tranh Việt Nam\n\n"

    "💬 VÍ DỤ TRẢ LỜI:\n"
    "Q: 'Máy bay A-37 Dragonfly là gì?'\n"
    "A: 'A-37 Dragonfly là máy bay tấn công hạng nhẹ của Mỹ, được phát triển từ máy bay huấn luyện T-37. "
    "Nó được sử dụng rộng rãi trong chiến tranh Việt Nam từ 1967, có biệt danh \"Super Tweet\". "
    "Máy bay này có thể mang 2.5 tấn vũ khí, rất hiệu quả trong yểm trợ không quân gần. "
    "Trong bảo tàng, bạn có thể thấy nhiều hiện vật liên quan đến các chiến dịch không quân!'\n\n"

    "Q: 'Xe tăng T-54 có gì đặc biệt?'\n"
    "A: 'T-54 là xe tăng chiến đấu chủ lực của Liên Xô, được sử dụng rộng rãi bởi quân đội Việt Nam. "
    "Nó có giáp dày 100mm, pháo 100mm, rất bền bỉ và dễ bảo trì. "
    "T-54 đóng vai trò quan trọng trong nhiều chiến dịch, đặc biệt là chiến dịch Hồ Chí Minh 1975!'\n\n"

    "PHONG CÁCH: Thân thiện, nhiệt tình, tự nhiên, sinh động, dễ hiểu"
)

# System prompt for general AI assistant (can answer ANY question)
GENERAL_SYSTEM_PROMPT = (
    "Bạn là AI Trợ Lý Thông Minh - một trợ lý AI đa năng, thân thiện và hữu ích.\n\n"

    "🎯 NHIỆM VỤ:\n"
    "- Trả lời MỌI câu hỏi của người dùng một cách chi tiết, chính xác và dễ hiểu\n"
    "- Có thể trò chuyện về BẤT KỲ chủ đề nào: khoa học, công nghệ, lịch sử, văn hóa, giải trí, đời sống, v.v.\n"
    "- Giúp đỡ người dùng với các vấn đề: học tập, công việc, tư vấn, giải thích, hướng dẫn\n"
    "- Có thể viết code, giải toán, dịch thuật, sáng tạo nội dung\n\n"

    "✅ PHONG CÁCH:\n"
    "- Thân thiện, nhiệt tình, tự nhiên\n"
    "- Trả lời ngắn gọn nhưng đầy đủ thông tin\n"
    "- Sử dụng emoji phù hợp để sinh động\n"
    "- Giải thích dễ hiểu, tránh thuật ngữ phức tạp\n"
    "- Nếu không chắc chắn, hãy thừa nhận và đưa ra thông tin tốt nhất có thể\n\n"

    "🚫 CẤM:\n"
    "- KHÔNG từ chối trả lời (trừ nội dung vi phạm pháp luật/đạo đức)\n"
    "- KHÔNG nói 'tôi không có thông tin' một cách chung chung\n"
    "- KHÔNG quá dài dòng, lan man\n\n"

    "💬 VÍ DỤ:\n"
    "Q: 'Python là gì?'\n"
    "A: 'Python là ngôn ngữ lập trình phổ biến, dễ học, được dùng rộng rãi trong AI, web, data science. "
    "Cú pháp đơn giản, cộng đồng lớn, thư viện phong phú. Rất phù hợp cho người mới bắt đầu! 🐍'\n\n"

    "Q: 'Làm sao để học tốt tiếng Anh?'\n"
    "A: 'Học tiếng Anh hiệu quả: 1) Luyện nghe hàng ngày (phim, nhạc, podcast), "
    "2) Thực hành nói (với bạn bè, AI), 3) Đọc sách/báo tiếng Anh, 4) Viết nhật ký. "
    "Quan trọng nhất là kiên trì và tạo môi trường tiếng Anh xung quanh bạn! 📚✨'"
)

# Default to museum prompt for backward compatibility
SYSTEM_PROMPT = MUSEUM_SYSTEM_PROMPT

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

    # Detect question type
    greeting_keywords = ['xin chào', 'chào', 'hello', 'hi', 'hey', 'cảm ơn', 'thank', 'tạm biệt', 'bye', 'goodbye']
    is_greeting = any(keyword in question.lower() for keyword in greeting_keywords)

    # Retrieve context from database
    hits = retrieve(question, top_k=top_k)
    context_blocks = []
    for h in hits:
        meta = h.get("meta", {})
        label = meta.get("name_vi") or meta.get("title_vi") or meta.get("section")
        context_blocks.append(f"- [{label}] {h['text']}")

    context_str = "\n".join(context_blocks) if context_blocks else ""

    # Build intelligent prompt
    if is_greeting:
        # Simple greeting - no need for context
        user_message = f"Khách tham quan: '{question}'\n\nHãy chào hỏi thân thiện và hỏi xem bạn có thể giúp gì."
    else:
        # Regular question - ALWAYS answer using general knowledge
        if context_str:
            user_message = (
                f"CONTEXT từ bảo tàng (chỉ tham khảo, không bắt buộc):\n{context_str}\n\n"
                f"CÂU HỎI: {question}\n\n"
                f"QUAN TRỌNG: Hãy trả lời câu hỏi bằng kiến thức chung của bạn về chiến tranh Việt Nam. "
                f"KHÔNG được nói 'tôi không có thông tin' hay 'trong bối cảnh này'. "
                f"Nếu được hỏi về máy bay, xe tăng, vũ khí → Giải thích chi tiết dựa trên kiến thức lịch sử. "
                f"Trả lời tự nhiên, sinh động như một hướng dẫn viên chuyên nghiệp."
            )
        else:
            user_message = (
                f"CÂU HỎI: {question}\n\n"
                f"QUAN TRỌNG: Hãy trả lời bằng kiến thức chung của bạn về chiến tranh Việt Nam. "
                f"KHÔNG được từ chối trả lời. Trả lời chi tiết, sinh động và thú vị. "
                f"Kết nối với bảo tàng và các hiện vật nếu có thể."
            )

    # Add few-shot examples to teach the model to always answer
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        # Example 1: Aircraft question
        {"role": "user", "content": "Hãy cho tôi biết về máy bay F-5A Freedom Fighter"},
        {"role": "assistant", "content": "F-5A Freedom Fighter là máy bay chiến đấu hạng nhẹ của Mỹ, được thiết kế bởi Northrop vào đầu thập niên 1960. Nó được sử dụng rộng rãi trong chiến tranh Việt Nam, đặc biệt bởi Không quân Việt Nam Cộng hòa. F-5A có tốc độ tối đa 1.4 Mach, trang bị 2 súng máy 20mm và có thể mang tên lửa không đối không AIM-9 Sidewinder. Máy bay này nổi tiếng với độ tin cậy cao và chi phí vận hành thấp. Trong bảo tàng, bạn có thể tìm hiểu thêm về các chiến dịch không quân và vai trò của những chiếc máy bay như thế này!"},
        # Example 2: Tank question
        {"role": "user", "content": "Xe tăng T-54 có gì đặc biệt?"},
        {"role": "assistant", "content": "T-54 là xe tăng chiến đấu chủ lực huyền thoại của Liên Xô, được sử dụng rộng rãi bởi quân đội Việt Nam trong chiến tranh. Nó có giáp dày 100mm ở phía trước, pháo chính 100mm D-10T rất mạnh mẽ, và động cơ diesel 520 mã lực. T-54 nổi tiếng với độ bền bỉ, dễ bảo trì và khả năng hoạt động trong mọi địa hình. Xe tăng này đóng vai trò then chốt trong nhiều chiến dịch, đặc biệt là chiến dịch Hồ Chí Minh 1975. Bảo tàng có nhiều hiện vật liên quan đến các chiến dịch xe tăng!"},
        # Example 3: Weapon question
        {"role": "user", "content": "AK-47 là súng gì?"},
        {"role": "assistant", "content": "AK-47 (Avtomat Kalashnikova) là súng trường tự động huyền thoại của Liên Xô, được thiết kế bởi Mikhail Kalashnikov năm 1947. Nó sử dụng đạn 7.62x39mm, có băng đạn 30 viên, tốc độ bắn 600 phát/phút. AK-47 nổi tiếng với độ tin cậy cực cao, có thể hoạt động trong mọi điều kiện khắc nghiệt: bùn, cát, nước. Súng này được sử dụng rộng rãi trong chiến tranh Việt Nam và trở thành biểu tượng của các phong trào giải phóng. Trong bảo tàng, bạn có thể thấy nhiều hiện vật vũ khí từ thời kỳ này!"},
        # Actual user question
        {"role": "user", "content": user_message}
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

@app.route("/api/ask-general", methods=["POST", "OPTIONS"])
def ask_general():
    """
    General AI assistant endpoint - can answer ANY question
    Not limited to museum context
    """
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json(force=True)
    question = data.get("question") or data.get("message", "")
    question = question.strip()
    max_tokens = int(data.get("max_tokens", 600))

    if not question:
        return jsonify({"error": "Thiếu trường 'question' hoặc 'message'"}), 400

    # Use general system prompt
    messages = [
        {"role": "system", "content": GENERAL_SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]

    try:
        answer = call_openrouter(messages, max_tokens=max_tokens, temperature=0.7)
        return jsonify({
            "answer": answer,
            "question": question,
            "model": RAG_LLM_MODEL,
            "mode": "general"
        })
    except Exception as e:
        print(f"❌ Error in ask_general: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"🚀 Running on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT)
