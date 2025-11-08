# ✅ Đã Thêm Nút AI Trợ Lý Vào Header!

## 🎯 Yêu Cầu

Thêm một nút vào Header để gọi AI agent lên, AI này có thể trả lời **TẤT CẢ câu hỏi** (không chỉ về bảo tàng).

## 🔧 Những Gì Đã Làm

### 1. **Thêm Nút "AI Trợ Lý" Vào Header** ✅

#### **Desktop:**
```svelte
<!-- AI Agent Button -->
<button
  class="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium 
         bg-gradient-to-r from-indigo-500 to-purple-600 text-white 
         hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 
         shadow-md hover:shadow-lg"
  on:click={() => aiAgentOpen = true}
>
  <svg class="w-5 h-5">...</svg>
  <span>AI Trợ Lý</span>
</button>
```

#### **Mobile:**
```svelte
<!-- AI Agent Button (Mobile) -->
<button
  class="w-full flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium 
         bg-gradient-to-r from-indigo-500 to-purple-600 text-white"
  on:click={() => { aiAgentOpen = true; mobileOpen = false; }}
>
  <svg class="w-5 h-5">...</svg>
  <span>AI Trợ Lý</span>
</button>
```

### 2. **Tạo 2 System Prompts Riêng Biệt** ✅

#### **Museum AI (Bảo tàng):**
```python
MUSEUM_SYSTEM_PROMPT = (
    "Bạn là hướng dẫn viên AI chuyên nghiệp của Bảo tàng Chứng tích Chiến tranh Việt Nam. "
    "Bạn có kiến thức sâu rộng về lịch sử chiến tranh Việt Nam và các loại vũ khí, máy bay, xe tăng.\n\n"
    # ... museum-specific instructions
)
```

#### **General AI (Đa năng):**
```python
GENERAL_SYSTEM_PROMPT = (
    "Bạn là AI Trợ Lý Thông Minh - một trợ lý AI đa năng, thân thiện và hữu ích.\n\n"
    
    "🎯 NHIỆM VỤ:\n"
    "- Trả lời MỌI câu hỏi của người dùng một cách chi tiết, chính xác và dễ hiểu\n"
    "- Có thể trò chuyện về BẤT KỲ chủ đề nào: khoa học, công nghệ, lịch sử, văn hóa, giải trí, đời sống\n"
    "- Giúp đỡ người dùng với các vấn đề: học tập, công việc, tư vấn, giải thích, hướng dẫn\n"
    "- Có thể viết code, giải toán, dịch thuật, sáng tạo nội dung\n\n"
    
    "✅ PHONG CÁCH:\n"
    "- Thân thiện, nhiệt tình, tự nhiên\n"
    "- Trả lời ngắn gọn nhưng đầy đủ thông tin\n"
    "- Sử dụng emoji phù hợp để sinh động\n"
    "- Giải thích dễ hiểu, tránh thuật ngữ phức tạp\n"
)
```

### 3. **Thêm Endpoint Mới `/api/ask-general`** ✅

```python
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
    
    # Use general system prompt
    messages = [
        {"role": "system", "content": GENERAL_SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
    answer = call_openrouter(messages, max_tokens=600, temperature=0.7)
    return jsonify({
        "answer": answer,
        "question": question,
        "mode": "general"
    })
```

### 4. **Cập Nhật VoiceInteractionModal** ✅

#### **Thêm Prop `isGeneralAgent`:**
```svelte
export let show = false;
export let itemName = '';
export let onClose = () => {};
export let isGeneralAgent = false; // true = general AI, false = museum AI
```

#### **Dynamic Endpoint Selection:**
```javascript
async function handleUserQuestion(question) {
  // Choose endpoint based on agent type
  const endpoint = isGeneralAgent ? `${API_AI}/ask-general` : `${API_AI}/ask`;
  
  // For general agent, send question as-is
  const message = isGeneralAgent ? question : `${question} (Về ${itemName})`;
  
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  // ...
}
```

#### **Dynamic Greetings:**
```javascript
function playInitialPrompt() {
  let greetings;
  
  if (isGeneralAgent) {
    // General AI greetings
    greetings = [
      `Xin chào! Mình là AI Trợ Lý Thông Minh. Bạn có thể hỏi mình bất cứ điều gì!`,
      `Chào bạn! Mình có thể giúp bạn về nhiều chủ đề: học tập, công việc, đời sống.`,
      `Xin chào! Mình sẵn sàng trả lời mọi câu hỏi của bạn. Hãy hỏi mình nhé!`
    ];
  } else {
    // Museum AI greetings
    greetings = [
      `Xin chào! Mình là trợ lý AI của bảo tàng. Bạn muốn tìm hiểu gì về ${itemName}?`,
      `Chào bạn! Bạn có câu hỏi nào về ${itemName} không?`
    ];
  }
  // ...
}
```

### 5. **Cập Nhật Header Component** ✅

```svelte
<!-- Modal AI Agent -->
<VoiceInteractionModal 
  show={aiAgentOpen} 
  itemName="AI Trợ Lý Thông Minh"
  isGeneralAgent={true}
  onClose={() => (aiAgentOpen = false)}
/>
```

## 📊 So Sánh 2 Chế Độ

| Tính Năng | Museum AI | General AI |
|-----------|-----------|------------|
| **Endpoint** | `/api/ask` | `/api/ask-general` |
| **System Prompt** | `MUSEUM_SYSTEM_PROMPT` | `GENERAL_SYSTEM_PROMPT` |
| **Context** | Bảo tàng + RAG database | Không giới hạn |
| **Câu hỏi** | Về bảo tàng, chiến tranh VN | Bất kỳ chủ đề nào |
| **Lời chào** | "Về ${itemName}" | "Hỏi bất cứ điều gì" |
| **Temperature** | 0.3 (chính xác) | 0.7 (sáng tạo) |
| **Trigger** | Click vào card | Click nút Header |

## 🧪 Test Cases

### Test 1: Nút AI Trợ Lý Trong Header

**Steps:**
1. Mở http://localhost:5173
2. Nhìn vào Header (góc phải)
3. Thấy nút **"AI Trợ Lý"** màu gradient tím-xanh

**Expected:**
- ✅ Nút hiển thị đẹp với icon 💡
- ✅ Hover có hiệu ứng shadow
- ✅ Click mở modal AI

### Test 2: General AI - Câu Hỏi Tổng Quát

**Steps:**
1. Click nút "AI Trợ Lý" trong Header
2. Modal mở → Nghe lời chào: "Mình là AI Trợ Lý Thông Minh..."
3. Hỏi: "Python là gì?"

**Expected:**
- ✅ AI trả lời về Python (ngôn ngữ lập trình)
- ✅ Không nói về bảo tàng
- ✅ Trả lời chi tiết, dễ hiểu

### Test 3: General AI - Nhiều Chủ Đề

**Steps:**
1. Hỏi: "Làm sao để học tốt tiếng Anh?"
2. Hỏi: "Giải thích AI là gì?"
3. Hỏi: "Viết code Python in Hello World"

**Expected:**
- ✅ Tất cả câu hỏi đều được trả lời
- ✅ Không từ chối câu hỏi nào
- ✅ Trả lời tự nhiên, thân thiện

### Test 4: Museum AI - Vẫn Hoạt Động

**Steps:**
1. Click vào một card (ví dụ: Máy bay A-37)
2. Modal mở → Nghe lời chào: "Về Máy bay A-37..."
3. Hỏi: "Máy bay này có gì đặc biệt?"

**Expected:**
- ✅ AI trả lời về máy bay A-37
- ✅ Kết nối với bảo tàng
- ✅ Sử dụng RAG context

### Test 5: Mobile - Nút AI Trợ Lý

**Steps:**
1. Mở trên mobile (hoặc resize browser < 768px)
2. Click hamburger menu (☰)
3. Thấy nút "AI Trợ Lý" trong menu

**Expected:**
- ✅ Nút hiển thị full width
- ✅ Click mở modal AI
- ✅ Menu tự động đóng

## 🎯 Kết Quả

- ✅ **Nút "AI Trợ Lý" đã được thêm vào Header** (desktop + mobile)
- ✅ **General AI có thể trả lời TẤT CẢ câu hỏi** (không giới hạn bảo tàng)
- ✅ **2 chế độ AI hoạt động độc lập:**
  - Museum AI: Click vào card → Hỏi về hiện vật
  - General AI: Click nút Header → Hỏi bất cứ điều gì
- ✅ **UI đẹp, gradient tím-xanh, có icon**
- ✅ **Lời chào khác nhau cho 2 chế độ**
- ✅ **Debug info hiển thị mode rõ ràng**

## 📝 Files Đã Thay Đổi

### Frontend:
- ✅ `frontend/src/lib/components/Header.svelte`
  - Thêm import `VoiceInteractionModal`
  - Thêm state `aiAgentOpen`
  - Thêm nút "AI Trợ Lý" (desktop + mobile)
  - Thêm modal với `isGeneralAgent={true}`

- ✅ `frontend/src/lib/components/VoiceInteractionModal.svelte`
  - Thêm prop `isGeneralAgent`
  - Dynamic endpoint selection
  - Dynamic greetings
  - Update debug info

### Backend:
- ✅ `Back-end/api-ai/app.py`
  - Tạo `GENERAL_SYSTEM_PROMPT`
  - Rename `SYSTEM_PROMPT` → `MUSEUM_SYSTEM_PROMPT`
  - Thêm endpoint `/api/ask-general`

## 🚀 Cách Test

```bash
# 1. Khởi động AI server (nếu chưa chạy)
cd Back-end/api-ai
python app.py

# 2. Frontend đã chạy, chỉ cần refresh
# Ctrl + Shift + R (hard refresh)
```

**Test Flow:**
1. Mở http://localhost:5173
2. **Test General AI:**
   - Click nút "AI Trợ Lý" trong Header
   - Hỏi: "Python là gì?"
   - Hỏi: "Làm sao để học tốt tiếng Anh?"
   - Hỏi: "Giải thích AI là gì?"
3. **Test Museum AI:**
   - Click vào một card
   - Hỏi: "Máy bay này có gì đặc biệt?"

## 💡 Ví Dụ Câu Hỏi Cho General AI

- "Python là gì?"
- "Làm sao để học tốt tiếng Anh?"
- "Giải thích AI là gì?"
- "Viết code Python in Hello World"
- "Cách nấu phở ngon?"
- "Lịch sử Việt Nam có gì đặc biệt?"
- "Cách giải phương trình bậc 2?"
- "Dịch sang tiếng Anh: Xin chào"

Tất cả đều được trả lời! 🎉

