# 📍 API Check-in Địa Điểm với AI & Quiz

## 📋 Tổng Quan

API check-in thông minh cho bảo tàng:
1. **Quét QR/Check-in** tại địa điểm
2. **AI tự động generate** thông tin về địa điểm
3. **Quiz tự động** với 3 câu hỏi
4. **Điểm thưởng** khi trả lời đúng (giảm giá vé lần sau)

---

## 🎯 Flow Hoàn Chỉnh

```
User quét QR tại địa điểm
    ↓
Check-in thành công
    ↓
AI generate thông tin về địa điểm (3-4 câu)
    ↓
AI generate 3 câu hỏi quiz
    ↓
User trả lời quiz
    ↓
Tính điểm + Tặng điểm thưởng
    ↓
Điểm thưởng tích lũy (dùng giảm giá vé)
```

---

## 📍 API 1: Check-in + AI Info + Quiz

### `GET/POST /api/checkin/scan-with-info`

Quét QR hoặc check-in tại địa điểm, nhận thông tin AI và quiz.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Params (GET) hoặc Body (POST):**
```json
{
  "dia_diem": "Ảnh Em bé Napalm (Kim Phúc)"
}
```

**Success Response - Lần đầu check-in (200):**
```json
{
  "ok": true,
  "message": "Đã check-in Ảnh Em bé Napalm (Kim Phúc)",
  "already_visited": false,
  "checkin_time": "2025-01-10 23:45:30",
  "location_info": "Bức ảnh 'Em bé Napalm' do Nick Út chụp năm 1972 là biểu tượng phản chiến toàn cầu. Ảnh ghi lại cảnh em bé Kim Phúc chạy khỏi làng bị tấn công bằng bom napalm. Bức ảnh đoạt giải Pulitzer và góp phần thay đổi dư luận thế giới về chiến tranh Việt Nam.",
  "quiz": [
    {
      "question": "Bức ảnh 'Em bé Napalm' được chụp vào năm nào?",
      "options": ["1970", "1972", "1975", "1968"],
      "correct": 1
    },
    {
      "question": "Nhiếp ảnh gia chụp bức ảnh này là ai?",
      "options": ["Robert Capa", "Nick Út", "Eddie Adams", "Larry Burrows"],
      "correct": 1
    },
    {
      "question": "Bức ảnh này đã đoạt giải thưởng nào?",
      "options": ["Oscar", "Grammy", "Pulitzer", "Nobel"],
      "correct": 2
    }
  ],
  "quiz_completed": false
}
```

**Success Response - Đã check-in trước đó (200):**
```json
{
  "ok": true,
  "message": "Bạn đã check-in Ảnh Em bé Napalm (Kim Phúc) trước đó",
  "already_visited": true,
  "checkin_time": "2025-01-10 15:30:00",
  "quiz_completed": true,
  "quiz_score": 100
}
```

**Error Responses:**

**401 - Chưa đăng nhập:**
```json
{
  "ok": false,
  "error": "Chưa đăng nhập. Hãy đăng nhập rồi quét lại."
}
```

**400 - Thiếu địa điểm:**
```json
{
  "ok": false,
  "error": "Thiếu dia_diem"
}
```

---

## ✅ API 2: Submit Quiz

### `POST /api/checkin/submit-quiz`

Nộp câu trả lời quiz và nhận điểm thưởng.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "dia_diem": "Ảnh Em bé Napalm (Kim Phúc)",
  "answers": [1, 1, 2],
  "correct_answers": [1, 1, 2]
}
```

**Giải thích:**
- `answers`: Mảng index (0-3) của đáp án user chọn
- `correct_answers`: Mảng index đáp án đúng (từ quiz trước đó)

**Success Response (200):**
```json
{
  "ok": true,
  "message": "Đã hoàn thành quiz!",
  "score": 100,
  "correct_count": 3,
  "total_questions": 3,
  "points_earned": 50,
  "total_points": 150,
  "feedback": "🎉 Xuất sắc! Bạn đã trả lời đúng tất cả!"
}
```

**Điểm thưởng:**
- **100% đúng** → 50 điểm
- **≥66% đúng** (2/3) → 30 điểm
- **≥33% đúng** (1/3) → 10 điểm
- **<33% đúng** → 0 điểm

**Feedback messages:**
- 100%: "🎉 Xuất sắc! Bạn đã trả lời đúng tất cả!"
- ≥66%: "👍 Tốt lắm! Bạn đã hiểu khá rõ về địa điểm này."
- ≥33%: "💪 Cố gắng lên! Hãy đọc kỹ thông tin hơn nhé."
- <33%: "📚 Hãy tìm hiểu thêm về địa điểm này nhé!"

**Error Responses:**

**401 - Chưa đăng nhập:**
```json
{
  "ok": false,
  "error": "Chưa đăng nhập"
}
```

**400 - Thiếu dữ liệu:**
```json
{
  "ok": false,
  "error": "Thiếu dia_diem"
}
```

---

## 📊 Database Schema

### Bảng `checkin` - Cột mới:

```sql
ALTER TABLE checkin ADD COLUMN checkin_time DATETIME DEFAULT NULL;
ALTER TABLE checkin ADD COLUMN quiz_completed TINYINT(1) DEFAULT 0;
ALTER TABLE checkin ADD COLUMN quiz_score INT DEFAULT 0;
```

**Cột:**
- `user` VARCHAR(190) - User ID
- `dia_diem` VARCHAR(255) - Tên địa điểm
- `checkin` TINYINT(1) - Đã check-in (0/1)
- `checkin_time` DATETIME - Thời gian check-in
- `quiz_completed` TINYINT(1) - Đã làm quiz (0/1)
- `quiz_score` INT - Điểm quiz (0-100)

### Bảng `users` - Cột điểm thưởng:

**Cột `diem_thuong`:**
- Tích lũy điểm từ quiz
- Dùng để giảm giá vé lần sau
- VD: 100 điểm = giảm 10,000đ

---

## 🧪 Test Flow

### 1. Check-in lần đầu:

```bash
curl -X POST http://localhost:3000/api/checkin/scan-with-info \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"dia_diem": "Ảnh Em bé Napalm (Kim Phúc)"}'
```

**Response:**
- ✅ Check-in thành công
- ✅ Nhận thông tin AI về địa điểm
- ✅ Nhận 3 câu hỏi quiz

### 2. Submit quiz:

```bash
curl -X POST http://localhost:3000/api/checkin/submit-quiz \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "dia_diem": "Ảnh Em bé Napalm (Kim Phúc)",
    "answers": [1, 1, 2],
    "correct_answers": [1, 1, 2]
  }'
```

**Response:**
- ✅ Tính điểm: 100%
- ✅ Tặng 50 điểm thưởng
- ✅ Tổng điểm: 150

### 3. Check-in lại (đã visit):

```bash
curl -X POST http://localhost:3000/api/checkin/scan-with-info \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"dia_diem": "Ảnh Em bé Napalm (Kim Phúc)"}'
```

**Response:**
- ✅ Thông báo đã check-in trước đó
- ✅ Hiển thị thời gian check-in
- ✅ Hiển thị điểm quiz đã làm

---

## 🎯 Use Cases

### Use Case 1: Tham quan bảo tàng

1. User vào bảo tàng, mua vé
2. Đi đến địa điểm 1: "Ảnh Em bé Napalm"
3. Quét QR code tại địa điểm
4. Nhận thông tin AI về bức ảnh
5. Làm quiz 3 câu hỏi
6. Trả lời đúng 3/3 → Nhận 50 điểm
7. Đi tiếp đến địa điểm 2, 3, 4...
8. Tích lũy điểm thưởng

### Use Case 2: Sử dụng điểm thưởng

1. User có 200 điểm thưởng
2. Lần sau mua vé, dùng điểm giảm giá
3. VD: 200 điểm = giảm 20,000đ
4. Vé 50,000đ → Chỉ trả 30,000đ

### Use Case 3: Gamification

1. Leaderboard: Top users có nhiều điểm nhất
2. Badges: Hoàn thành tất cả địa điểm
3. Challenges: Check-in 10 địa điểm trong 1 ngày

---

## 🤖 AI Integration

### AI API Endpoint:
```
http://localhost:8000/api/ask
```

### AI Prompts:

**1. Generate Location Info:**
```
Hãy cung cấp thông tin chi tiết về '{location_name}' trong Bảo Tàng Chứng Tích Chiến Tranh. 
Bao gồm: lịch sử, ý nghĩa, và những điểm đặc biệt. 
Trả lời bằng tiếng Việt, ngắn gọn khoảng 3-4 câu.
```

**2. Generate Quiz:**
```
Dựa trên thông tin sau về '{location_name}':
{location_info}

Hãy tạo 3 câu hỏi trắc nghiệm về địa điểm này. 
Mỗi câu hỏi có 4 đáp án, chỉ 1 đáp án đúng.

Trả lời theo format JSON...
```

### Fallback Quiz:

Nếu AI fail, sử dụng quiz mặc định:
1. Địa điểm thuộc bảo tàng nào?
2. Bảo tàng ở thành phố nào?
3. Mục đích trưng bày là gì?

---

## 🔐 Security & Performance

**Rate Limiting:**
- Mỗi user chỉ check-in 1 lần/địa điểm
- Không thể làm quiz lại sau khi hoàn thành

**Caching:**
- Cache AI responses để giảm API calls
- Cache quiz questions

**Validation:**
- Validate `dia_diem` tồn tại trong database
- Validate `answers` array length = `correct_answers` length

---

## 📱 Frontend Integration

Xem file `frontend/src/lib/api.js` để thêm:

```javascript
export async function checkinWithInfo(diaD iem) {
  const res = await fetch(`${API_AUTH}/checkin/scan-with-info`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dia_diem: diaDiem })
  });
  return await res.json();
}

export async function submitQuiz(diaDiem, answers, correctAnswers) {
  const res = await fetch(`${API_AUTH}/checkin/submit-quiz`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      dia_diem: diaDiem, 
      answers, 
      correct_answers: correctAnswers 
    })
  });
  return await res.json();
}
```

---

## 🎉 Summary

- ✅ **Check-in API** với AI info + Quiz
- ✅ **AI auto-generate** thông tin địa điểm
- ✅ **Quiz system** với 3 câu hỏi
- ✅ **Điểm thưởng** tự động tính toán
- ✅ **Database tracking** lịch sử check-in
- ✅ **Gamification** ready

**API đang chạy tại:** `http://localhost:3000` 🚀

