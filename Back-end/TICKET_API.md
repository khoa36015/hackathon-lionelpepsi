# 🎫 API Mua Vé Bảo Tàng

## 📋 Tổng Quan

API mua vé với thanh toán ngân hàng giả lập. Giá vé: **50,000đ/người**.

## 🏦 Tài Khoản Ngân Hàng Giả Lập

### GET `/api/bank/accounts`

Lấy danh sách tài khoản ngân hàng test.

**Response:**
```json
{
  "ok": true,
  "accounts": [
    {
      "account_number": "1234567890",
      "name": "Nguyen Van A",
      "balance": 1000000
    },
    {
      "account_number": "0987654321",
      "name": "Tran Thi B",
      "balance": 500000
    },
    {
      "account_number": "1111222233",
      "name": "Le Van C",
      "balance": 2000000
    }
  ],
  "note": "Mật khẩu cho tất cả tài khoản: 123456",
  "ticket_price": 50000
}
```

**Mật khẩu:** `123456` (cho tất cả tài khoản)

---

## 🎟️ Mua Vé

### POST `/api/ticket/purchase`

Mua vé với thanh toán ngân hàng.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "bank_account": "1234567890",
  "bank_password": "123456"
}
```

**Success Response (200):**
```json
{
  "ok": true,
  "message": "Mua vé thành công!",
  "ticket_code": "VE2025011012345678",
  "purchase_date": "2025-01-10 15:30:45",
  "amount_paid": 50000,
  "remaining_balance": 950000,
  "user": {
    "user_id": "john_doe",
    "trang_thai": 1,
    "ma_ve": "VE2025011012345678",
    "ngay_mua_ve": "2025-01-10 15:30:45",
    "so_tien_thanh_toan": 50000
  }
}
```

**Error Responses:**

**401 - Chưa đăng nhập:**
```json
{
  "ok": false,
  "error": "Chưa đăng nhập"
}
```

**400 - Đã mua vé:**
```json
{
  "ok": false,
  "error": "Bạn đã mua vé rồi",
  "ticket_code": "VE2025011012345678"
}
```

**404 - Tài khoản không tồn tại:**
```json
{
  "ok": false,
  "error": "Tài khoản ngân hàng không tồn tại"
}
```

**401 - Sai mật khẩu:**
```json
{
  "ok": false,
  "error": "Mật khẩu ngân hàng không đúng"
}
```

**400 - Không đủ tiền:**
```json
{
  "ok": false,
  "error": "Số dư không đủ. Cần 50,000đ, còn 30,000đ"
}
```

---

## ✅ Kiểm Tra Trạng Thái Vé

### GET `/api/ticket/status`

Kiểm tra xem user đã mua vé chưa và lấy mã vé.

**Headers:**
```
Authorization: Bearer <token>
```

**Success Response (200):**
```json
{
  "ok": true,
  "has_ticket": true,
  "ticket_code": "VE2025011012345678",
  "purchase_date": "2025-01-10 15:30:45",
  "amount_paid": 50000,
  "user": {
    "user_id": "john_doe",
    "trang_thai": 1,
    "ma_ve": "VE2025011012345678",
    "ngay_mua_ve": "2025-01-10 15:30:45",
    "so_tien_thanh_toan": 50000
  }
}
```

**Chưa mua vé:**
```json
{
  "ok": true,
  "has_ticket": false,
  "ticket_code": null,
  "purchase_date": null,
  "amount_paid": 0,
  "user": {
    "user_id": "john_doe",
    "trang_thai": 0,
    "ma_ve": null,
    "ngay_mua_ve": null,
    "so_tien_thanh_toan": 0
  }
}
```

---

## 🔍 Xác Minh Mã Vé (Cổng Vào)

### POST `/api/ticket/verify`

Xác minh mã vé khi vào cổng bảo tàng.

**Body:**
```json
{
  "ticket_code": "VE2025011012345678"
}
```

**Success Response (200):**
```json
{
  "ok": true,
  "message": "Mã vé hợp lệ",
  "ticket_code": "VE2025011012345678",
  "owner": "john_doe",
  "purchase_date": "2025-01-10 15:30:45"
}
```

**Error Responses:**

**404 - Mã vé không hợp lệ:**
```json
{
  "ok": false,
  "error": "Mã vé không hợp lệ"
}
```

**400 - Vé đã bị hủy:**
```json
{
  "ok": false,
  "error": "Vé đã bị hủy"
}
```

---

## 📊 Database Schema

### Bảng `users` - Cột mới:

```sql
ALTER TABLE users ADD COLUMN ma_ve VARCHAR(20) DEFAULT NULL;
ALTER TABLE users ADD COLUMN ngay_mua_ve DATETIME DEFAULT NULL;
ALTER TABLE users ADD COLUMN so_tien_thanh_toan INT DEFAULT 0;
```

**Cột:**
- `ma_ve`: Mã vé (VD: VE2025011012345678)
- `ngay_mua_ve`: Ngày giờ mua vé
- `so_tien_thanh_toan`: Số tiền đã thanh toán (50000)
- `trang_thai`: 1 = đã mua vé, 0 = chưa mua

---

## 🧪 Test Flow

### 1. Lấy danh sách tài khoản ngân hàng:
```bash
curl http://localhost:3000/api/bank/accounts
```

### 2. Đăng nhập:
```bash
curl -X POST http://localhost:3000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "password123"}' \
  -c cookies.txt
```

### 3. Mua vé:
```bash
curl -X POST http://localhost:3000/api/ticket/purchase \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"bank_account": "1234567890", "bank_password": "123456"}' \
  -b cookies.txt
```

### 4. Kiểm tra trạng thái vé:
```bash
curl http://localhost:3000/api/ticket/status \
  -H "Authorization: Bearer <token>" \
  -b cookies.txt
```

### 5. Xác minh mã vé (cổng vào):
```bash
curl -X POST http://localhost:3000/api/ticket/verify \
  -H "Content-Type: application/json" \
  -d '{"ticket_code": "VE2025011012345678"}'
```

---

## 🎯 Use Cases

### Use Case 1: Mua vé thành công
1. User đăng nhập
2. User chọn tài khoản ngân hàng
3. User nhập mật khẩu ngân hàng
4. Hệ thống kiểm tra số dư
5. Hệ thống trừ tiền và tạo mã vé
6. User nhận mã vé

### Use Case 2: Vào cổng bảo tàng
1. Nhân viên quét/nhập mã vé
2. Hệ thống xác minh mã vé
3. Hiển thị thông tin: chủ vé, ngày mua
4. Cho phép vào

### Use Case 3: Kiểm tra vé đã mua
1. User đăng nhập
2. User vào trang "Vé của tôi"
3. Hiển thị mã vé, ngày mua, số tiền

---

## 🔐 Security Notes

**⚠️ ĐÂY LÀ API GIẢ LẬP CHO MỤC ĐÍCH DEMO:**

1. Mật khẩu ngân hàng hardcoded: `123456`
2. Số dư ngân hàng lưu trong memory (không persistent)
3. Không có encryption cho thông tin thanh toán
4. Không có rate limiting
5. Không có transaction rollback

**Trong production thực tế cần:**
- Tích hợp cổng thanh toán thật (VNPay, MoMo, ZaloPay)
- Mã hóa thông tin thanh toán
- Transaction management
- Audit logging
- Rate limiting
- 2FA cho thanh toán

---

## 📱 Frontend Integration

Xem file `frontend/src/lib/api.js` để thêm các functions:

```javascript
export async function purchaseTicket(bankAccount, bankPassword) {
  const res = await fetch(`${API_AUTH}/ticket/purchase`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ bank_account: bankAccount, bank_password: bankPassword })
  });
  return await res.json();
}

export async function getTicketStatus() {
  const res = await fetch(`${API_AUTH}/ticket/status`, {
    method: 'GET',
    credentials: 'include'
  });
  return await res.json();
}

export async function verifyTicket(ticketCode) {
  const res = await fetch(`${API_AUTH}/ticket/verify`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticket_code: ticketCode })
  });
  return await res.json();
}

export async function getBankAccounts() {
  const res = await fetch(`${API_AUTH}/bank/accounts`, {
    method: 'GET'
  });
  return await res.json();
}
```

