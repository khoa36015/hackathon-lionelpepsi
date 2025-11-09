# ======================== IMPORTS ========================
from flask import Flask, jsonify, request, abort, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_session import Session
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import mysql.connector
import secrets
import urllib.parse
import requests  # ✅ cần cho OpenWeather
import json
import os
# Dữ liệu bảo tàng
from data import  bao_tang_chung_tich  # ✅ bạn đã có file data.py

# Load museum data
PHAN_LOAI = bao_tang_chung_tich.get("phan_loai", {})
TEN_BAO_TANG = bao_tang_chung_tich.get("ten", "Bảo tàng Chứng tích Chiến tranh")
DIA_CHI_BAO_TANG = bao_tang_chung_tich.get("dia_chi", "Không rõ địa chỉ")

# Load extended artifacts from data.json
EXTENDED_ARTIFACTS = []
DATA_JSON_PATH = os.path.join(os.path.dirname(__file__), "data.json")
try:
    with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
        data_json = json.load(f)
        EXTENDED_ARTIFACTS = data_json.get("extended_artifacts", [])
        print(f"[INFO] Loaded {len(EXTENDED_ARTIFACTS)} extended artifacts from data.json")
except Exception as e:
    print(f"[WARNING] Could not load data.json: {e}")
    EXTENDED_ARTIFACTS = []

# ======================== CONFIG ========================
# ---- DB AUTH (giữ như file của bạn) ----
DB_HOST = "34.136.163.31"
DB_PORT = 3306
DB_USER = "admin"
DB_PASS = "Kv135791!"
DB_NAME = "authen"  # tên database trong file authen.sql

# ---- Feedback DB (giữ như file của bạn) ----
def db_conn(db_name):
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=db_name
    )

# ---- Flask app (KHỞI TẠO 1 LẦN DUY NHẤT) ----
app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config.update(
    SECRET_KEY="change_this_secret_123",     # đổi khi dùng thật
    JSON_AS_ASCII=False,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    SESSION_TYPE="filesystem",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,             # dev mode
)
Session(app)

# ---- CORS (fixed for frontend) ----
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
]

CORS(app, supports_credentials=True, origins=ALLOWED_ORIGINS)

@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get('Origin')
    if origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return resp

@app.route("/api/<path:_path>", methods=["OPTIONS"])
def handle_options(_path):
    return add_cors_headers(jsonify({"message": "CORS preflight OK"}))

# ======================== DB (auth) ========================
def get_conn():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS,
        database=DB_NAME, charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

# ======================== SESSION TOKEN ===================
session_cache = {}
def create_token(user_id: str):
    token = secrets.token_hex(16)
    session_cache[token] = {"user_id": user_id, "expires": datetime.utcnow() + timedelta(hours=12)}
    return token

def verify_token(req) -> str | None:
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1].strip()
    data = session_cache.get(token)
    if not data:
        return None
    if data["expires"] < datetime.utcnow():
        session_cache.pop(token, None)
        return None
    return data["user_id"]

def verify_session_or_token(req):
    # Check session first (for cookie-based auth)
    if 'user_id' in session:
        return session['user_id']
    
    # Fallback to token-based auth
    return verify_token(req)

# ======================== AUTH ============================
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()  # Frontend sends 'username'
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"message": "Thiếu username hoặc password"}), 400

    hashed_pw = generate_password_hash(password)
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO users (user_id, mat_khau) VALUES (%s, %s)", (username, hashed_pw))
        return jsonify({"message": "Registered successfully!"})  # Frontend expects this exact message
    except pymysql.err.IntegrityError:
        return jsonify({"message": "Username đã tồn tại"}), 409
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()  # Frontend sends 'username'
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"isLoggedIn": False, "message": "Thiếu username hoặc password"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE user_id=%s", (username,))
        user = cur.fetchone()
    if not user:
        return jsonify({"isLoggedIn": False, "message": "Không tìm thấy user"}), 404
    if not check_password_hash(user["mat_khau"], password):
        return jsonify({"isLoggedIn": False, "message": "Sai mật khẩu"}), 401

    # Set session for cookie-based auth
    session['user_id'] = username
    session.permanent = True
    
    token = create_token(username)
    return jsonify({"isLoggedIn": True, "message": "Đăng nhập thành công", "username": username, "token": token})

@app.route("/api/check-session", methods=["GET"])
def check_session():
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"isLoggedIn": False, "username": None})
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT user_id, trang_thai, diem_thuong FROM users WHERE user_id=%s", (user_id,))
        user = cur.fetchone()
    if not user:
        return jsonify({"isLoggedIn": False, "username": None})
    return jsonify({"isLoggedIn": True, "username": user["user_id"]})

@app.route("/api/logout", methods=["POST"])
def logout():
    # Clear session
    session.pop('user_id', None)

    # Clear token
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1].strip()
        session_cache.pop(token, None)
    return jsonify({"message": "Đã đăng xuất"})

@app.route("/api/profile", methods=["GET"])
def get_profile():
    """Get user profile information"""
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT user_id, trang_thai, ma_ve, diem_thuong
                FROM users
                WHERE user_id=%s
            """, (user_id,))
            user = cur.fetchone()

        if not user:
            return jsonify({"ok": False, "error": "Không tìm thấy người dùng"}), 404

        return jsonify({
            "ok": True,
            "username": user["user_id"],
            "ticket_code": user.get("ma_ve"),
            "reward_points": user.get("diem_thuong", 0),
            "account_status": user.get("trang_thai", "active")
        })
    except Exception as e:
        print(f"Error getting profile: {e}")
        return jsonify({"ok": False, "error": "Lỗi khi lấy thông tin"}), 500

# ======================== TICKET ==========================
# Ensure ticket columns exist in users table
def ensure_ticket_columns():
    """Add ticket-related columns to users table if they don't exist"""
    with get_conn() as conn, conn.cursor() as cur:
        # Check if columns exist
        cur.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME IN ('ma_ve', 'ngay_mua_ve', 'so_tien_thanh_toan')
        """, (DB_NAME,))
        existing_cols = {row['COLUMN_NAME'] for row in cur.fetchall()}

        # Add missing columns
        if 'ma_ve' not in existing_cols:
            cur.execute("ALTER TABLE users ADD COLUMN ma_ve VARCHAR(20) DEFAULT NULL")
        if 'ngay_mua_ve' not in existing_cols:
            cur.execute("ALTER TABLE users ADD COLUMN ngay_mua_ve DATETIME DEFAULT NULL")
        if 'so_tien_thanh_toan' not in existing_cols:
            cur.execute("ALTER TABLE users ADD COLUMN so_tien_thanh_toan INT DEFAULT 0")

ensure_ticket_columns()

# Fake bank accounts for simulation
FAKE_BANK_ACCOUNTS = {
    "1234567890": {"name": "Nguyen Van A", "balance": 1000000},
    "0987654321": {"name": "Tran Thi B", "balance": 500000},
    "1111222233": {"name": "Le Van C", "balance": 2000000},
}

TICKET_PRICE = 50000  # 50k VND per ticket

def generate_ticket_code():
    """Generate unique ticket code: VE + timestamp + random"""
    import random
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    return f"VE{timestamp[-8:]}{random_part}"

@app.route("/api/ticket/purchase", methods=["POST"])
def ticket_purchase():
    """Purchase ticket with fake bank payment"""
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    data = request.get_json(silent=True) or {}
    bank_account = (data.get("bank_account") or "").strip()
    bank_password = (data.get("bank_password") or "").strip()

    if not bank_account:
        return jsonify({"ok": False, "error": "Thiếu số tài khoản ngân hàng"}), 400

    # Check if user already has ticket
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT trang_thai, ma_ve FROM users WHERE user_id=%s", (user_id,))
        user = cur.fetchone()

        if not user:
            return jsonify({"ok": False, "error": "Không tìm thấy user"}), 404

        if user["trang_thai"] == 1 and user["ma_ve"]:
            return jsonify({
                "ok": False,
                "error": "Bạn đã mua vé rồi",
                "ticket_code": user["ma_ve"]
            }), 400

    # Simulate bank payment
    if bank_account not in FAKE_BANK_ACCOUNTS:
        return jsonify({"ok": False, "error": "Tài khoản ngân hàng không tồn tại"}), 404

    account = FAKE_BANK_ACCOUNTS[bank_account]

    # Check password (simple simulation - in real app use proper auth)
    if bank_password != "123456":  # Fake password for all accounts
        return jsonify({"ok": False, "error": "Mật khẩu ngân hàng không đúng"}), 401

    # Check balance
    if account["balance"] < TICKET_PRICE:
        return jsonify({
            "ok": False,
            "error": f"Số dư không đủ. Cần {TICKET_PRICE:,}đ, còn {account['balance']:,}đ"
        }), 400

    # Deduct money (in memory - not persistent)
    account["balance"] -= TICKET_PRICE

    # Generate ticket code
    ticket_code = generate_ticket_code()
    purchase_time = datetime.now()

    # Update user with ticket info
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            UPDATE users
            SET trang_thai=1, ma_ve=%s, ngay_mua_ve=%s, so_tien_thanh_toan=%s
            WHERE user_id=%s
        """, (ticket_code, purchase_time, TICKET_PRICE, user_id))

        cur.execute("""
            SELECT user_id, trang_thai, ma_ve, ngay_mua_ve, so_tien_thanh_toan
            FROM users WHERE user_id=%s
        """, (user_id,))
        updated_user = cur.fetchone()

    return jsonify({
        "ok": True,
        "message": "Mua vé thành công!",
        "ticket_code": ticket_code,
        "purchase_date": purchase_time.strftime("%Y-%m-%d %H:%M:%S"),
        "amount_paid": TICKET_PRICE,
        "remaining_balance": account["balance"],
        "user": updated_user
    })

@app.route("/api/ticket/status", methods=["GET"])
def ticket_status():
    """Check if user has purchased ticket and get ticket code"""
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT user_id, trang_thai, ma_ve, ngay_mua_ve, so_tien_thanh_toan
            FROM users WHERE user_id=%s
        """, (user_id,))
        user = cur.fetchone()

    if not user:
        return jsonify({"ok": False, "error": "Không tìm thấy user"}), 404

    has_ticket = bool(user["trang_thai"] == 1 and user["ma_ve"])

    return jsonify({
        "ok": True,
        "has_ticket": has_ticket,
        "ticket_code": user["ma_ve"] if has_ticket else None,
        "purchase_date": user["ngay_mua_ve"].strftime("%Y-%m-%d %H:%M:%S") if user["ngay_mua_ve"] else None,
        "amount_paid": user["so_tien_thanh_toan"],
        "user": user
    })

@app.route("/api/ticket/qr", methods=["GET"])
def ticket_qr():
    """Generate QR code for user's ticket"""
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT user_id, ma_ve, ngay_mua_ve, so_tien_thanh_toan, trang_thai
            FROM users
            WHERE user_id=%s
        """, (user_id,))
        user_data = cur.fetchone()

    if not user_data or not user_data.get("ma_ve") or user_data.get("trang_thai") != 1:
        return jsonify({"ok": False, "error": "Chưa có vé"}), 400

    # QR data format: ma_ve|user_id|ngay_mua|so_tien
    ma_ve = user_data.get("ma_ve")
    ngay_mua = user_data.get("ngay_mua_ve").strftime("%Y-%m-%d %H:%M:%S") if user_data.get("ngay_mua_ve") else ""
    so_tien = user_data.get("so_tien_thanh_toan", 0)

    qr_data = f"{ma_ve}|{user_id}|{ngay_mua}|{so_tien}"

    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return jsonify({
        "ok": True,
        "qr_image": f"data:image/png;base64,{img_str}",
        "qr_data": qr_data,
        "ma_ve": ma_ve
    })

# ======================== TOURS API ========================
# Generate locations from data.json extended_artifacts
def get_locations_from_artifacts():
    """Extract unique locations from extended_artifacts location_hint"""
    locations_map = {}
    
    # Map location_hint to standardized location names
    location_mapping = {
        "trên bầu trời và tại các bãi đáp dã chiến": "Khu Trưng Bày Ngoài Trời",
        "dọc các trục đường chiến lược": "Khu Trưng Bày Ngoài Trời",
        "trảng bàng, tây ninh": "Khu Trưng Bày Ảnh Quốc Tế",
        "khu mô phỏng nhà tù": "Phòng Trà Tân",
        "khu trưng bày nạn nhân": "Khu Trưng Bày Trong Nhà",
        "vùng đồng bằng và rừng thấp": "Khu Trưng Bày Ngoài Trời",
        "bên vai phóng viên trên chiến trường": "Khu Trưng Bày Ảnh Quốc Tế",
        "điểm liên lạc tiền phương": "Khu Trưng Bày Trong Nhà",
        "phòng chỉ huy dã chiến": "Khu Trưng Bày Trong Nhà",
        "ba lô và túi áo ngực": "Khu Trưng Bày Trong Nhà",
        "hòm thư dã chiến": "Khu Trưng Bày Trong Nhà",
        "trên chiến trường và chốt chặn": "Khu Trưng Bày Ngoài Trời",
        "cổng đơn vị/điểm kiểm soát": "Khu Trưng Bày Ngoài Trời",
        "trạm quân y dã chiến": "Khu Trưng Bày Trong Nhà",
        "hành lang bệnh xá dã chiến": "Khu Trưng Bày Trong Nhà",
        "trận địa pháo": "Khu Trưng Bày Ngoài Trời",
        "hàng rào phòng thủ": "Khu Trưng Bày Ngoài Trời",
        "công sự dã chiến": "Khu Trưng Bày Ngoài Trời",
        "tại doanh trại và ngoài chiến trường": "Khu Trưng Bày Ngoài Trời",
        "trên tay áo, túi áo": "Khu Trưng Bày Trong Nhà",
        "kho quân nhu": "Khu Trưng Bày Trong Nhà",
        "trong ba lô, chốt trực": "Khu Trưng Bày Trong Nhà",
        "vùng ô nhiễm bom mìn": "Khu Trưng Bày Ngoài Trời",
        "khu trưng bày ngoài trời": "Khu Trưng Bày Ngoài Trời",
        "phòng khách thời ấy": "Khu Trưng Bày Trong Nhà",
        "khu đô thị": "Khu Trưng Bày Ảnh Quốc Tế",
        "bên hông lính/nhân viên y tế": "Khu Trưng Bày Trong Nhà",
        "đường mòn, bìa rừng": "Khu Trưng Bày Ngoài Trời",
        "thắt lưng người lính": "Khu Trưng Bày Trong Nhà",
        "bàn gỗ cũ": "Khu Trưng Bày Trong Nhà",
        "ví tiền hoặc túi áo": "Khu Trưng Bày Trong Nhà",
    }
    
    # Standard locations
    standard_locations = [
        "Khu Trưng Bày Trong Nhà",
        "Khu Trưng Bày Ngoài Trời",
        "Khu Trưng Bày Ảnh Quốc Tế",
        "Phòng Trà Tân"
    ]
    
    # Count artifacts per location
    for artifact in EXTENDED_ARTIFACTS:
        location_hint = artifact.get("location_hint", "").lower()
        location = None
        
        # Find matching location
        for hint, loc in location_mapping.items():
            if hint in location_hint:
                location = loc
                break
        
        # Default to indoor if no match
        if not location:
            location = "Khu Trưng Bày Trong Nhà"
        
        if location not in locations_map:
            locations_map[location] = 0
        locations_map[location] += 1
    
    # Also count from PHAN_LOAI
    for photo in PHAN_LOAI.get("anh", []):
        location = "Khu Trưng Bày Ảnh Quốc Tế" if "quốc tế" in photo.get("ten", "").lower() or "phóng viên" in photo.get("ten", "").lower() else "Khu Trưng Bày Trong Nhà"
        if location not in locations_map:
            locations_map[location] = 0
        locations_map[location] += 1
    
    for artifact in PHAN_LOAI.get("di_vat", []):
        name_lower = artifact.get("ten", "").lower()
        if any(kw in name_lower for kw in ["máy bay", "xe tăng", "trực thăng"]):
            location = "Khu Trưng Bày Ngoài Trời"
        elif "tra tấn" in name_lower or "tù binh" in name_lower:
            location = "Phòng Trà Tân"
        else:
            location = "Khu Trưng Bày Trong Nhà"
        
        if location not in locations_map:
            locations_map[location] = 0
        locations_map[location] += 1
    
    # Create location list
    locations = []
    descriptions = {
        "Khu Trưng Bày Trong Nhà": "Các hiện vật và ảnh lịch sử trong nhà",
        "Khu Trưng Bày Ngoài Trời": "Vũ khí và phương tiện quân sự",
        "Khu Trưng Bày Ảnh Quốc Tế": "Ảnh từ phóng viên chiến trường quốc tế",
        "Phòng Trà Tân": "Hiện vật tra tấn và tù binh"
    }
    
    for loc in standard_locations:
        locations.append({
            "name": loc,
            "count": locations_map.get(loc, 0),
            "description": descriptions.get(loc, "")
        })
    
    return locations

TOUR_LOCATIONS = get_locations_from_artifacts()

@app.route("/api/tours/locations", methods=["GET"])
def get_tour_locations():
    """Get all unique locations from photos and artifacts"""
    try:
        # Refresh locations
        global TOUR_LOCATIONS
        TOUR_LOCATIONS = get_locations_from_artifacts()
        return jsonify({
            "ok": True,
            "locations": TOUR_LOCATIONS
        })
    except Exception as e:
        print(f"Error getting locations: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": "Lỗi khi lấy địa điểm"}), 500

@app.route("/api/tours/location-info", methods=["POST"])
def get_location_info():
    """Get AI-generated information about a location"""
    data = request.get_json(silent=True) or {}
    location = (data.get("location") or "").strip()

    if not location:
        return jsonify({"ok": False, "error": "Thiếu tên địa điểm"}), 400

    try:
        # Find location info from predefined list
        location_data = next((loc for loc in TOUR_LOCATIONS if loc["name"] == location), None)

        if location_data:
            # Generate AI info about location
            prompt = f"""Hãy cung cấp thông tin ngắn gọn (2-3 câu) về khu vực '{location}' trong Bảo Tàng Chứng Tích Chiến Tranh Việt Nam.

Mô tả: {location_data.get('description', '')}

Trả lời bằng tiếng Việt, tập trung vào ý nghĩa lịch sử và những gì du khách có thể khám phá tại đây."""

            try:
                response = requests.post(AI_API_URL, json={"message": prompt}, timeout=10)
                if response.ok:
                    ai_data = response.json()
                    info = ai_data.get("response", location_data.get("description", ""))
                else:
                    info = location_data.get("description", "")
            except:
                info = location_data.get("description", "")

            return jsonify({
                "ok": True,
                "location": location,
                "info": info,
                "item_count": location_data.get("count", 0)
            })
        else:
            return jsonify({
                "ok": True,
                "location": location,
                "info": f"Địa điểm {location} trong Bảo Tàng Chứng Tích Chiến Tranh.",
                "item_count": 0
            })
    except Exception as e:
        print(f"Error getting location info: {e}")
        return jsonify({
            "ok": True,
            "location": location,
            "info": f"Địa điểm {location} trong Bảo Tàng Chứng Tích Chiến Tranh.",
            "item_count": 0
        })

@app.route("/api/tours/items-by-location", methods=["POST"])
def get_items_by_location():
    """Get photos and artifacts from selected locations using data.json"""
    data = request.get_json(silent=True) or {}
    locations = data.get("locations", [])

    print(f"[DEBUG] Received locations: {locations}")

    if not locations:
        return jsonify({"ok": False, "error": "Thiếu danh sách địa điểm"}), 400

    try:
        # Location mapping (same as in get_locations_from_artifacts)
        location_mapping = {
            "trên bầu trời và tại các bãi đáp dã chiến": "Khu Trưng Bày Ngoài Trời",
            "dọc các trục đường chiến lược": "Khu Trưng Bày Ngoài Trời",
            "trảng bàng, tây ninh": "Khu Trưng Bày Ảnh Quốc Tế",
            "khu mô phỏng nhà tù": "Phòng Trà Tân",
            "khu trưng bày nạn nhân": "Khu Trưng Bày Trong Nhà",
            "vùng đồng bằng và rừng thấp": "Khu Trưng Bày Ngoài Trời",
            "bên vai phóng viên trên chiến trường": "Khu Trưng Bày Ảnh Quốc Tế",
            "điểm liên lạc tiền phương": "Khu Trưng Bày Trong Nhà",
            "phòng chỉ huy dã chiến": "Khu Trưng Bày Trong Nhà",
            "ba lô và túi áo ngực": "Khu Trưng Bày Trong Nhà",
            "hòm thư dã chiến": "Khu Trưng Bày Trong Nhà",
            "trên chiến trường và chốt chặn": "Khu Trưng Bày Ngoài Trời",
            "cổng đơn vị/điểm kiểm soát": "Khu Trưng Bày Ngoài Trời",
            "trạm quân y dã chiến": "Khu Trưng Bày Trong Nhà",
            "hành lang bệnh xá dã chiến": "Khu Trưng Bày Trong Nhà",
            "trận địa pháo": "Khu Trưng Bày Ngoài Trời",
            "hàng rào phòng thủ": "Khu Trưng Bày Ngoài Trời",
            "công sự dã chiến": "Khu Trưng Bày Ngoài Trời",
            "tại doanh trại và ngoài chiến trường": "Khu Trưng Bày Ngoài Trời",
            "trên tay áo, túi áo": "Khu Trưng Bày Trong Nhà",
            "kho quân nhu": "Khu Trưng Bày Trong Nhà",
            "trong ba lô, chốt trực": "Khu Trưng Bày Trong Nhà",
            "vùng ô nhiễm bom mìn": "Khu Trưng Bày Ngoài Trời",
            "khu trưng bày ngoài trời": "Khu Trưng Bày Ngoài Trời",
            "phòng khách thời ấy": "Khu Trưng Bày Trong Nhà",
            "khu đô thị": "Khu Trưng Bày Ảnh Quốc Tế",
            "bên hông lính/nhân viên y tế": "Khu Trưng Bày Trong Nhà",
            "đường mòn, bìa rừng": "Khu Trưng Bày Ngoài Trời",
            "thắt lưng người lính": "Khu Trưng Bày Trong Nhà",
            "bàn gỗ cũ": "Khu Trưng Bày Trong Nhà",
            "ví tiền hoặc túi áo": "Khu Trưng Bày Trong Nhà",
        }
        
        def get_location_from_hint(location_hint):
            """Map location_hint to standardized location"""
            location_hint_lower = location_hint.lower()
            for hint, loc in location_mapping.items():
                if hint in location_hint_lower:
                    return loc
            return "Khu Trưng Bày Trong Nhà"  # Default
        
        # Process extended artifacts from data.json
        artifacts = []
        artifact_id_counter = 1000  # Start from 1000 to avoid conflicts
        
        # Create a map of artifact data_json_id to artifact for lookup
        artifact_map = {}
        for artifact in EXTENDED_ARTIFACTS:
            artifact_map[artifact.get("id", "")] = artifact
        
        for artifact in EXTENDED_ARTIFACTS:
            location_hint = artifact.get("location_hint", "")
            location = get_location_from_hint(location_hint)
            
            if location in locations:
                artifact_data = {
                    "id": artifact_id_counter,
                    "ten": artifact.get("name_vi", ""),
                    "mo_ta": artifact.get("paragraphs_vi", [""])[0][:200] if artifact.get("paragraphs_vi") else "",
                    "hinh_anh": None,  # Extended artifacts may not have image paths
                    "dia_diem": location,
                    "period": artifact.get("period", ""),
                    "location_hint": location_hint,
                    "tags": artifact.get("tags", []),
                    "data_json_id": artifact.get("id", ""),
                    "artifact_index": artifact_id_counter - 1000  # Store index for retrieval
                }
                artifacts.append(artifact_data)
                artifact_id_counter += 1
        
        # Also include artifacts from PHAN_LOAI
        all_artifacts_old = PHAN_LOAI.get("di_vat", [])
        for artifact in all_artifacts_old:
            artifact_copy = artifact.copy()
            name_lower = artifact.get("ten", "").lower()
            if any(kw in name_lower for kw in ["máy bay", "xe tăng", "trực thăng"]):
                artifact_copy["dia_diem"] = "Khu Trưng Bày Ngoài Trời"
            elif "tra tấn" in name_lower or "tù binh" in name_lower:
                artifact_copy["dia_diem"] = "Phòng Trà Tân"
            else:
                artifact_copy["dia_diem"] = "Khu Trưng Bày Trong Nhà"
            
            if artifact_copy["dia_diem"] in locations:
                artifacts.append(artifact_copy)
        
        # Process photos from PHAN_LOAI
        photos = []
        all_photos = PHAN_LOAI.get("anh", [])
        for photo in all_photos:
            photo_copy = photo.copy()
            if "quốc tế" in photo.get("ten", "").lower() or "phóng viên" in photo.get("ten", "").lower():
                photo_copy["dia_diem"] = "Khu Trưng Bày Ảnh Quốc Tế"
            else:
                photo_copy["dia_diem"] = "Khu Trưng Bày Trong Nhà"
            
            if photo_copy["dia_diem"] in locations:
                photos.append(photo_copy)

        print(f"[DEBUG] Filtered photos: {len(photos)}, artifacts: {len(artifacts)}")

        return jsonify({
            "ok": True,
            "photos": photos,
            "artifacts": artifacts
        })
    except Exception as e:
        print(f"Error getting items by location: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": "Lỗi khi lấy dữ liệu"}), 500

@app.route("/api/tours/create", methods=["POST"])
def create_tour():
    """Create a custom tour"""
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    data = request.get_json(silent=True) or {}
    tour_name = (data.get("tour_name") or "").strip()
    description = (data.get("description") or "").strip()
    items = data.get("items", [])  # List of {type: 'photo'|'artifact', id: int}

    if not tour_name:
        return jsonify({"ok": False, "error": "Thiếu tên lộ trình"}), 400

    if not items or len(items) == 0:
        return jsonify({"ok": False, "error": "Lộ trình phải có ít nhất 1 điểm"}), 400

    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Insert tour
            cur.execute("""
                INSERT INTO tours (user_id, tour_name, description, created_at)
                VALUES (%s, %s, %s, NOW())
            """, (user_id, tour_name, description))
            tour_id = cur.lastrowid

            # Insert tour items
            for idx, item in enumerate(items):
                item_type = item.get("type")
                item_id = item.get("id")
                cur.execute("""
                    INSERT INTO tour_items (tour_id, item_type, item_id, order_index)
                    VALUES (%s, %s, %s, %s)
                """, (tour_id, item_type, item_id, idx))

        return jsonify({
            "ok": True,
            "message": "Đã tạo lộ trình thành công!",
            "tour_id": tour_id
        })
    except Exception as e:
        print(f"Error creating tour: {e}")
        return jsonify({"ok": False, "error": "Lỗi khi tạo lộ trình"}), 500

@app.route("/api/tours/my", methods=["GET"])
def get_my_tours():
    """Get user's tours"""
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT id, tour_name, description, created_at
                FROM tours
                WHERE user_id=%s
                ORDER BY created_at DESC
            """, (user_id,))
            tours = cur.fetchall()

            # Get items for each tour
            for tour in tours:
                cur.execute("""
                    SELECT item_type, item_id, order_index
                    FROM tour_items
                    WHERE tour_id=%s
                    ORDER BY order_index
                """, (tour["id"],))
                tour["items"] = cur.fetchall()

                # Format date
                if tour.get("created_at"):
                    tour["created_at"] = tour["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "ok": True,
            "tours": tours
        })
    except Exception as e:
        print(f"Error getting tours: {e}")
        return jsonify({"ok": False, "error": "Lỗi khi lấy lộ trình"}), 500

@app.route("/api/tours/<int:tour_id>", methods=["GET"])
def get_tour_detail(tour_id):
    """Get tour details with full item information from data.json and PHAN_LOAI"""
    # Location mapping helper function (same as in get_items_by_location)
    location_mapping_detail = {
        "trên bầu trời và tại các bãi đáp dã chiến": "Khu Trưng Bày Ngoài Trời",
        "dọc các trục đường chiến lược": "Khu Trưng Bày Ngoài Trời",
        "trảng bàng, tây ninh": "Khu Trưng Bày Ảnh Quốc Tế",
        "khu mô phỏng nhà tù": "Phòng Trà Tân",
        "khu trưng bày nạn nhân": "Khu Trưng Bày Trong Nhà",
        "vùng đồng bằng và rừng thấp": "Khu Trưng Bày Ngoài Trời",
        "bên vai phóng viên trên chiến trường": "Khu Trưng Bày Ảnh Quốc Tế",
        "điểm liên lạc tiền phương": "Khu Trưng Bày Trong Nhà",
        "phòng chỉ huy dã chiến": "Khu Trưng Bày Trong Nhà",
        "ba lô và túi áo ngực": "Khu Trưng Bày Trong Nhà",
        "hòm thư dã chiến": "Khu Trưng Bày Trong Nhà",
        "trên chiến trường và chốt chặn": "Khu Trưng Bày Ngoài Trời",
        "cổng đơn vị/điểm kiểm soát": "Khu Trưng Bày Ngoài Trời",
        "trạm quân y dã chiến": "Khu Trưng Bày Trong Nhà",
        "hành lang bệnh xá dã chiến": "Khu Trưng Bày Trong Nhà",
        "trận địa pháo": "Khu Trưng Bày Ngoài Trời",
        "hàng rào phòng thủ": "Khu Trưng Bày Ngoài Trời",
        "công sự dã chiến": "Khu Trưng Bày Ngoài Trời",
        "tại doanh trại và ngoài chiến trường": "Khu Trưng Bày Ngoài Trời",
        "trên tay áo, túi áo": "Khu Trưng Bày Trong Nhà",
        "kho quân nhu": "Khu Trưng Bày Trong Nhà",
        "trong ba lô, chốt trực": "Khu Trưng Bày Trong Nhà",
        "vùng ô nhiễm bom mìn": "Khu Trưng Bày Ngoài Trời",
        "khu trưng bày ngoài trời": "Khu Trưng Bày Ngoài Trời",
        "phòng khách thời ấy": "Khu Trưng Bày Trong Nhà",
        "khu đô thị": "Khu Trưng Bày Ảnh Quốc Tế",
        "bên hông lính/nhân viên y tế": "Khu Trưng Bày Trong Nhà",
        "đường mòn, bìa rừng": "Khu Trưng Bày Ngoài Trời",
        "thắt lưng người lính": "Khu Trưng Bày Trong Nhà",
        "bàn gỗ cũ": "Khu Trưng Bày Trong Nhà",
        "ví tiền hoặc túi áo": "Khu Trưng Bày Trong Nhà",
    }
    
    def get_location_from_hint_detail(location_hint):
        """Map location_hint to standardized location"""
        location_hint_lower = location_hint.lower()
        for hint, loc in location_mapping_detail.items():
            if hint in location_hint_lower:
                return loc
        return "Khu Trưng Bày Trong Nhà"  # Default
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Get tour info
            cur.execute("""
                SELECT id, user_id, tour_name, description, created_at
                FROM tours
                WHERE id=%s
            """, (tour_id,))
            tour = cur.fetchone()

            if not tour:
                return jsonify({"ok": False, "error": "Không tìm thấy lộ trình"}), 404

            # Get tour items with details
            cur.execute("""
                SELECT item_type, item_id, order_index
                FROM tour_items
                WHERE tour_id=%s
                ORDER BY order_index
            """, (tour_id,))
            items = cur.fetchall()

            # Fetch full details for each item from PHAN_LOAI and EXTENDED_ARTIFACTS
            detailed_items = []
            for item in items:
                item_type = item["item_type"]
                item_id = item["item_id"]
                order_index = item["order_index"]
                
                detail = None
                
                if item_type == "photo":
                    # Find in PHAN_LOAI photos
                    for photo in PHAN_LOAI.get("anh", []):
                        if photo.get("id") == item_id:
                            detail = {
                                "id": photo.get("id"),
                                "name": photo.get("ten", ""),
                                "description": photo.get("mo_ta", ""),
                                "image": photo.get("hinh_anh", ""),
                                "type": "photo",
                                "order": order_index
                            }
                            break
                
                elif item_type == "artifact":
                    # First check EXTENDED_ARTIFACTS (IDs >= 1000)
                    if item_id >= 1000:
                        artifact_idx = item_id - 1000
                        if 0 <= artifact_idx < len(EXTENDED_ARTIFACTS):
                            artifact = EXTENDED_ARTIFACTS[artifact_idx]
                            detail = {
                                "id": item_id,
                                "name": artifact.get("name_vi", ""),
                                "ten": artifact.get("name_vi", ""),  # Also include 'ten' for compatibility
                                "description": artifact.get("paragraphs_vi", [""])[0] if artifact.get("paragraphs_vi") else "",
                                "mo_ta": artifact.get("paragraphs_vi", [""])[0] if artifact.get("paragraphs_vi") else "",
                                "image": None,
                                "period": artifact.get("period", ""),
                                "location_hint": artifact.get("location_hint", ""),
                                "dia_diem": get_location_from_hint_detail(artifact.get("location_hint", "")),  # Map to location
                                "tags": artifact.get("tags", []),
                                "type": "artifact",
                                "order": order_index
                            }
                    else:
                        # Find in PHAN_LOAI artifacts
                        for artifact in PHAN_LOAI.get("di_vat", []):
                            if artifact.get("id") == item_id:
                                detail = {
                                    "id": artifact.get("id"),
                                    "name": artifact.get("ten", ""),
                                    "description": artifact.get("mo_ta", ""),
                                    "image": artifact.get("hinh_anh", ""),
                                    "type": "artifact",
                                    "order": order_index
                                }
                                break
                
                if detail:
                    detailed_items.append(detail)

            # Sort by order
            detailed_items.sort(key=lambda x: x.get("order", 0))
            
            tour["items"] = detailed_items
            if tour.get("created_at"):
                tour["created_at"] = tour["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "ok": True,
            "tour": tour
        })
    except Exception as e:
        print(f"Error getting tour detail: {e}")
        return jsonify({"ok": False, "error": "Lỗi khi lấy chi tiết lộ trình"}), 500

# ======================== FEEDBACK API ========================
@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """Submit user feedback"""
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    data = request.get_json(silent=True) or {}
    rating = data.get("rating")
    comment = (data.get("comment") or "").strip()
    category = (data.get("category") or "general").strip()

    if not rating or rating not in [1, 2, 3, 4, 5]:
        return jsonify({"ok": False, "error": "Rating phải từ 1-5"}), 400

    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO feedback (user_id, rating, comment, category, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (user_id, rating, comment, category))
            feedback_id = cur.lastrowid

        return jsonify({
            "ok": True,
            "message": "Cảm ơn bạn đã gửi feedback!",
            "feedback_id": feedback_id
        })
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return jsonify({"ok": False, "error": "Lỗi khi lưu feedback"}), 500

@app.route("/api/feedback", methods=["GET"])
def get_feedback():
    """Get user's feedback history"""
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT id, rating, comment, category, created_at
                FROM feedback
                WHERE user_id=%s
                ORDER BY created_at DESC
                LIMIT 50
            """, (user_id,))
            feedbacks = cur.fetchall()

        # Format dates
        for fb in feedbacks:
            if fb.get("created_at"):
                fb["created_at"] = fb["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "ok": True,
            "feedbacks": feedbacks
        })
    except Exception as e:
        print(f"Error getting feedback: {e}")
        return jsonify({"ok": False, "error": "Lỗi khi lấy feedback"}), 500

@app.route("/api/ticket/verify", methods=["POST"])
def ticket_verify():
    """Verify ticket code for entry"""
    data = request.get_json(silent=True) or {}
    ticket_code = (data.get("ticket_code") or "").strip()

    if not ticket_code:
        return jsonify({"ok": False, "error": "Thiếu mã vé"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT user_id, ma_ve, ngay_mua_ve, trang_thai
            FROM users WHERE ma_ve=%s
        """, (ticket_code,))
        user = cur.fetchone()

    if not user:
        return jsonify({"ok": False, "error": "Mã vé không hợp lệ"}), 404

    if user["trang_thai"] != 1:
        return jsonify({"ok": False, "error": "Vé đã bị hủy"}), 400

    return jsonify({
        "ok": True,
        "message": "Mã vé hợp lệ",
        "ticket_code": ticket_code,
        "owner": user["user_id"],
        "purchase_date": user["ngay_mua_ve"].strftime("%Y-%m-%d %H:%M:%S") if user["ngay_mua_ve"] else None
    })

@app.route("/api/bank/accounts", methods=["GET"])
def get_bank_accounts():
    """Get list of fake bank accounts for testing"""
    accounts = [
        {"account_number": acc, "name": info["name"], "balance": info["balance"]}
        for acc, info in FAKE_BANK_ACCOUNTS.items()
    ]
    return jsonify({
        "ok": True,
        "accounts": accounts,
        "note": "Mật khẩu cho tất cả tài khoản: 123456",
        "ticket_price": TICKET_PRICE
    })

# Legacy endpoints (keep for backward compatibility)
@app.route("/api/ticket/confirm", methods=["POST"])
def ticket_confirm():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "").strip()
    if not user_id:
        return jsonify({"ok": False, "error": "Thiếu user_id"}), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE users SET trang_thai=1 WHERE user_id=%s", (user_id,))
        cur.execute("SELECT user_id, trang_thai, diem_thuong FROM users WHERE user_id=%s", (user_id,))
        row = cur.fetchone()
    if not row:
        return jsonify({"ok": False, "error": "Không tìm thấy user"}), 404
    return jsonify({"ok": True, "message": "Đã xác nhận mua vé", "user": row, "purchased": bool(row["trang_thai"] == 1)})

@app.route("/api/ticket/cancel", methods=["POST"])
def ticket_cancel():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "").strip()
    if not user_id:
        return jsonify({"ok": False, "error": "Thiếu user_id"}), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE users SET trang_thai=0 WHERE user_id=%s", (user_id,))
        cur.execute("SELECT user_id, trang_thai, diem_thuong FROM users WHERE user_id=%s", (user_id,))
        row = cur.fetchone()
    if not row:
        return jsonify({"ok": False, "error": "Không tìm thấy user"}), 404
    return jsonify({"ok": True, "message": "Đã huỷ xác nhận", "user": row, "purchased": bool(row["trang_thai"] == 1)})

# ======================== CHECKIN (QR) ====================
def ensure_checkin_table():
    """Create checkin table with timestamp and quiz tracking"""
    with get_conn() as conn, conn.cursor() as cur:
        # Main checkin table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS checkin (
              id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
              user VARCHAR(190) NOT NULL,
              dia_diem VARCHAR(255) NOT NULL,
              checkin TINYINT(1) NOT NULL DEFAULT 0,
              checkin_time DATETIME DEFAULT NULL,
              quiz_completed TINYINT(1) DEFAULT 0,
              quiz_score INT DEFAULT 0,
              PRIMARY KEY (id),
              UNIQUE KEY uk_user_dia_diem (user, dia_diem)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Add new columns if they don't exist (for existing tables)
        cur.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = 'checkin'
            AND COLUMN_NAME IN ('checkin_time', 'quiz_completed', 'quiz_score')
        """, (DB_NAME,))
        existing_cols = {row['COLUMN_NAME'] for row in cur.fetchall()}

        if 'checkin_time' not in existing_cols:
            cur.execute("ALTER TABLE checkin ADD COLUMN checkin_time DATETIME DEFAULT NULL")
        if 'quiz_completed' not in existing_cols:
            cur.execute("ALTER TABLE checkin ADD COLUMN quiz_completed TINYINT(1) DEFAULT 0")
        if 'quiz_score' not in existing_cols:
            cur.execute("ALTER TABLE checkin ADD COLUMN quiz_score INT DEFAULT 0")

ensure_checkin_table()

def upsert_checkin(user_id: str, dia_diem: str, checked: int = 1):
    """Update or insert checkin record with timestamp"""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            UPDATE checkin
            SET checkin=%s, checkin_time=NOW()
            WHERE user=%s AND dia_diem=%s
        """, (checked, user_id, dia_diem))

        if cur.rowcount == 0:
            cur.execute("""
                INSERT INTO checkin(user, dia_diem, checkin, checkin_time)
                VALUES (%s,%s,%s,NOW())
            """, (user_id, dia_diem, checked))

        cur.execute("""
            SELECT user, dia_diem, checkin, checkin_time, quiz_completed, quiz_score
            FROM checkin
            WHERE user=%s AND dia_diem=%s
        """, (user_id, dia_diem))
        return cur.fetchone()

def get_checkin(user_id: str, dia_diem: str):
    """Get checkin record for user and location"""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT user, dia_diem, checkin, checkin_time, quiz_completed, quiz_score
            FROM checkin
            WHERE user=%s AND dia_diem=%s
        """, (user_id, dia_diem))
        return cur.fetchone()

@app.route("/api/qr/link", methods=["GET"])
def qr_link():
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401
    dia_diem = (request.args.get("dia_diem") or "").strip()
    if not dia_diem:
        return jsonify({"ok": False, "error": "Thiếu dia_diem"}), 400
    encoded = urllib.parse.quote(dia_diem, safe="")
    host = request.host_url.rstrip("/")
    url = f"{host}/api/checkin/scan?dia_diem={encoded}"
    return jsonify({"ok": True, "url": url})

@app.route("/api/checkin/scan", methods=["GET"])
def checkin_scan():
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập. Hãy đăng nhập rồi quét lại."}), 401
    dia_diem = (request.args.get("dia_diem") or "").strip()
    if not dia_diem:
        return jsonify({"ok": False, "error": "Thiếu dia_diem"}), 400
    row = upsert_checkin(user_id, dia_diem, checked=1)
    return jsonify({"ok": True, "message": f"Đã check-in {dia_diem}", "data": row})

@app.route("/api/checkin/mark", methods=["POST"])
def checkin_mark():
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401
    d = request.get_json(silent=True) or {}
    dia_diem = (d.get("dia_diem") or "").strip()
    if not dia_diem:
        return jsonify({"ok": False, "error": "Thiếu dia_diem"}), 400
    row = upsert_checkin(user_id, dia_diem, checked=1)
    return jsonify({"ok": True, "data": row})

@app.route("/api/checkin/status", methods=["GET"])
def checkin_status():
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401
    dia_diem = (request.args.get("dia_diem") or "").strip()
    if not dia_diem:
        return jsonify({"ok": False, "error": "Thiếu dia_diem"}), 400
    row = get_checkin(user_id, dia_diem)
    return jsonify({"ok": True, "user": user_id, "dia_diem": dia_diem, "checked": bool(row and row.get("checkin") == 1)})

@app.route("/api/checkin/list", methods=["GET"])
def checkin_list():
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT dia_diem, checkin FROM checkin WHERE user=%s AND checkin=1 ORDER BY dia_diem", (user_id,))
        rows = cur.fetchall()
    return jsonify({"ok": True, "data": rows})

@app.route("/api/checkin/visited", methods=["GET"])
def checkin_visited():
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401
    q = (request.args.get("q") or "").strip()
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"ok": False, "error": "limit/offset không hợp lệ"}), 400
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    where = ["user=%s", "checkin=1"]
    args = [user_id]
    if q:
        where.append("dia_diem LIKE %s")
        args.append(f"%{q}%")
    where_sql = " AND ".join(where)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS total FROM checkin WHERE {where_sql}", args)
        total = (cur.fetchone() or {}).get("total", 0)
        cur.execute(
            f"""
            SELECT dia_diem, checkin
            FROM checkin
            WHERE {where_sql}
            ORDER BY id DESC
            LIMIT %s OFFSET %s
            """,
            args + [limit, offset],
        )
        rows = cur.fetchall()
    return jsonify({"ok": True, "user": user_id, "total": total, "limit": limit, "offset": offset, "data": rows})

# ======================== CHECKIN WITH AI & QUIZ ========================
import requests
import json
import qrcode
import io
import base64

# AI API endpoint
AI_API_URL = "http://localhost:8000/api/ask"

def generate_location_info(location_name):
    """Generate AI information about a location"""
    try:
        prompt = f"Hãy cung cấp thông tin chi tiết về '{location_name}' trong Bảo Tàng Chứng Tích Chiến Tranh. Bao gồm: lịch sử, ý nghĩa, và những điểm đặc biệt. Trả lời bằng tiếng Việt, ngắn gọn khoảng 3-4 câu."

        response = requests.post(AI_API_URL, json={"message": prompt}, timeout=10)
        if response.ok:
            data = response.json()
            return data.get("response", "Không có thông tin")
        return "Không thể tải thông tin từ AI"
    except Exception as e:
        print(f"AI generation error: {e}")
        return f"Thông tin về {location_name} đang được cập nhật."

def generate_quiz(location_name, location_info):
    """Generate quiz questions about the location"""
    try:
        prompt = f"""Dựa trên thông tin sau về '{location_name}':
{location_info}

Hãy tạo 3 câu hỏi trắc nghiệm (multiple choice) về địa điểm này. Mỗi câu hỏi có 4 đáp án, chỉ 1 đáp án đúng.

Trả lời theo format JSON chính xác như sau (không thêm markdown, chỉ JSON thuần):
{{
  "questions": [
    {{
      "question": "Câu hỏi 1?",
      "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
      "correct": 0
    }},
    {{
      "question": "Câu hỏi 2?",
      "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
      "correct": 1
    }},
    {{
      "question": "Câu hỏi 3?",
      "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
      "correct": 2
    }}
  ]
}}

Trong đó 'correct' là index (0-3) của đáp án đúng."""

        response = requests.post(AI_API_URL, json={"message": prompt}, timeout=15)
        if response.ok:
            data = response.json()
            ai_response = data.get("response", "")

            # Try to extract JSON from response
            try:
                # Remove markdown code blocks if present
                if "```json" in ai_response:
                    ai_response = ai_response.split("```json")[1].split("```")[0].strip()
                elif "```" in ai_response:
                    ai_response = ai_response.split("```")[1].split("```")[0].strip()

                quiz_data = json.loads(ai_response)
                return quiz_data.get("questions", [])
            except json.JSONDecodeError:
                print(f"Failed to parse quiz JSON: {ai_response}")
                return generate_fallback_quiz(location_name)

        return generate_fallback_quiz(location_name)
    except Exception as e:
        print(f"Quiz generation error: {e}")
        return generate_fallback_quiz(location_name)

def generate_fallback_quiz(location_name):
    """Generate simple fallback quiz if AI fails"""
    return [
        {
            "question": f"Địa điểm '{location_name}' thuộc bảo tàng nào?",
            "options": [
                "Bảo Tàng Chứng Tích Chiến Tranh",
                "Bảo Tàng Lịch Sử",
                "Bảo Tàng Mỹ Thuật",
                "Bảo Tàng Dân Tộc"
            ],
            "correct": 0
        },
        {
            "question": "Bảo tàng này nằm ở thành phố nào?",
            "options": ["Hà Nội", "Đà Nẵng", "TP. Hồ Chí Minh", "Huế"],
            "correct": 2
        },
        {
            "question": f"Mục đích chính của việc trưng bày '{location_name}' là gì?",
            "options": [
                "Giáo dục lịch sử và lan tỏa thông điệp hòa bình",
                "Thu hút khách du lịch",
                "Trang trí bảo tàng",
                "Lưu trữ hiện vật"
            ],
            "correct": 0
        }
    ]

@app.route("/api/checkin/generate-qr", methods=["POST"])
def generate_checkin_qr():
    """Generate QR code data and image for user to check-in at location"""
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    # Check if user has ticket
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT ma_ve FROM users WHERE user_id=%s", (user_id,))
        user_data = cur.fetchone()

    if not user_data or not user_data.get("ma_ve"):
        return jsonify({"ok": False, "error": "Bạn chưa mua vé. Vui lòng mua vé trước khi check-in."}), 400

    data = request.get_json(silent=True) or {}
    dia_diem = (data.get("dia_diem") or "").strip()

    if not dia_diem:
        return jsonify({"ok": False, "error": "Thiếu dia_diem"}), 400

    ma_ve = user_data.get("ma_ve")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # QR data format: ma_ve|dia_diem|timestamp|user_id
    qr_data = f"{ma_ve}|{dia_diem}|{timestamp}|{user_id}"

    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return jsonify({
        "ok": True,
        "qr_data": qr_data,
        "qr_image": f"data:image/png;base64,{img_str}",
        "ma_ve": ma_ve,
        "dia_diem": dia_diem,
        "timestamp": timestamp,
        "message": "Vui lòng đưa mã QR này cho nhân viên để check-in"
    })

@app.route("/api/checkin/scan-qr", methods=["POST"])
def scan_checkin_qr():
    """Scan QR code and check-in user (used by staff/scanner)"""
    data = request.get_json(silent=True) or {}
    qr_data = (data.get("qr_data") or "").strip()

    if not qr_data:
        return jsonify({"ok": False, "error": "Thiếu qr_data"}), 400

    # Parse QR data: ma_ve|dia_diem|timestamp|user_id
    try:
        parts = qr_data.split("|")
        if len(parts) != 4:
            return jsonify({"ok": False, "error": "QR code không hợp lệ"}), 400

        ma_ve, dia_diem, timestamp, user_id = parts

        # Verify ticket exists
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT user_id, ma_ve FROM users WHERE user_id=%s AND ma_ve=%s", (user_id, ma_ve))
            user_data = cur.fetchone()

        if not user_data:
            return jsonify({"ok": False, "error": "Mã vé không hợp lệ"}), 400

        # Check if already checked in
        existing = get_checkin(user_id, dia_diem)
        if existing and existing.get("checkin") == 1:
            return jsonify({
                "ok": True,
                "message": f"Đã check-in {dia_diem} trước đó",
                "already_visited": True,
                "checkin_time": existing.get("checkin_time").strftime("%Y-%m-%d %H:%M:%S") if existing.get("checkin_time") else None,
                "quiz_completed": bool(existing.get("quiz_completed")),
                "quiz_score": existing.get("quiz_score", 0)
            })

        # First time check-in
        checkin_record = upsert_checkin(user_id, dia_diem, checked=1)

        # Award 1000 points for first-time check-in
        CHECKIN_REWARD = 1000
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                UPDATE users
                SET diem_thuong = diem_thuong + %s
                WHERE user_id=%s
            """, (CHECKIN_REWARD, user_id))

            # Get updated points
            cur.execute("SELECT diem_thuong FROM users WHERE user_id=%s", (user_id,))
            user_data = cur.fetchone()
            total_points = user_data.get("diem_thuong", 0) if user_data else 0

        # Generate AI info about location
        location_info = generate_location_info(dia_diem)

        # Generate quiz
        quiz_questions = generate_quiz(dia_diem, location_info)

        return jsonify({
            "ok": True,
            "message": f"Check-in thành công tại {dia_diem}! +{CHECKIN_REWARD} điểm",
            "already_visited": False,
            "user_id": user_id,
            "ma_ve": ma_ve,
            "dia_diem": dia_diem,
            "checkin_time": checkin_record.get("checkin_time").strftime("%Y-%m-%d %H:%M:%S") if checkin_record.get("checkin_time") else None,
            "location_info": location_info,
            "quiz": quiz_questions,
            "quiz_completed": False,
            "points_earned": CHECKIN_REWARD,
            "total_points": total_points
        })

    except Exception as e:
        print(f"Error scanning QR: {e}")
        return jsonify({"ok": False, "error": "Lỗi khi xử lý QR code"}), 500

@app.route("/api/checkin/submit-quiz", methods=["POST"])
def submit_quiz():
    """Submit quiz answers and award points"""
    user_id = verify_session_or_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    data = request.get_json(silent=True) or {}
    dia_diem = (data.get("dia_diem") or "").strip()
    answers = data.get("answers", [])  # List of user's answer indices
    correct_answers = data.get("correct_answers", [])  # List of correct answer indices

    if not dia_diem:
        return jsonify({"ok": False, "error": "Thiếu dia_diem"}), 400

    if not answers or not correct_answers:
        return jsonify({"ok": False, "error": "Thiếu answers hoặc correct_answers"}), 400

    # Calculate score
    total_questions = len(correct_answers)
    correct_count = sum(1 for i, ans in enumerate(answers) if i < len(correct_answers) and ans == correct_answers[i])
    score = int((correct_count / total_questions) * 100)

    # Award points based on score
    points_earned = 0
    if score == 100:
        points_earned = 50  # Perfect score
    elif score >= 66:
        points_earned = 30  # 2/3 correct
    elif score >= 33:
        points_earned = 10  # 1/3 correct

    # Update checkin record
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            UPDATE checkin
            SET quiz_completed=1, quiz_score=%s
            WHERE user=%s AND dia_diem=%s
        """, (score, user_id, dia_diem))

        # Update user points
        cur.execute("""
            UPDATE users
            SET diem_thuong = diem_thuong + %s
            WHERE user_id=%s
        """, (points_earned, user_id))

        # Get updated user points
        cur.execute("SELECT diem_thuong FROM users WHERE user_id=%s", (user_id,))
        user_data = cur.fetchone()
        total_points = user_data.get("diem_thuong", 0) if user_data else 0

    return jsonify({
        "ok": True,
        "message": "Đã hoàn thành quiz!",
        "score": score,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "points_earned": points_earned,
        "total_points": total_points,
        "feedback": get_quiz_feedback(score)
    })

def get_quiz_feedback(score):
    """Get feedback message based on score"""
    if score == 100:
        return "🎉 Xuất sắc! Bạn đã trả lời đúng tất cả!"
    elif score >= 66:
        return "👍 Tốt lắm! Bạn đã hiểu khá rõ về địa điểm này."
    elif score >= 33:
        return "💪 Cố gắng lên! Hãy đọc kỹ thông tin hơn nhé."
    else:
        return "📚 Hãy tìm hiểu thêm về địa điểm này nhé!"

# ======================== AI AGENT ========================
@app.route("/api/ai/agent", methods=["POST"])
def ai_agent():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Message required"}), 400
    
    # Simple echo response - replace with actual AI integration
    response = f"AI Response to: {message}"
    return jsonify({"response": response, "success": True})

@app.route("/api/ask", methods=["POST"])
def ask_ai():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Message required"}), 400
    
    # Simple response - replace with actual AI integration
    response = f"Thông tin về {message}: Đây là thông tin chi tiết từ AI."
    return jsonify({"response": response, "success": True})

# ======================== PROVINCES ========================
@app.route("/api/provinces", methods=["GET"])
def get_provinces():
    provinces = [
        {"id": 1, "name": "Hồ Chí Minh"},
        {"id": 2, "name": "Hà Nội"},
        {"id": 3, "name": "Đà Nẵng"},
        {"id": 4, "name": "Cần Thơ"},
        {"id": 5, "name": "Hải Phòng"}
    ]
    return jsonify({"provinces": provinces})

# ======================== FEEDBACK =======================
@app.route("/api/feedback", methods=["POST"])
def feedback():
    d = request.get_json(silent=True) or {}
    if not d.get("message"):
        return jsonify({"message": "Message required"}), 400
    rating = d.get("rating")
    if rating is not None and not isinstance(rating, (int, float)):
        return jsonify({"message": "Rating must be number"}), 400
    conn = db_conn("feedback"); cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT id, created_at FROM feedbacks WHERE username=%s AND message=%s ORDER BY created_at DESC LIMIT 1",
            (d.get("username"), d["message"])
        )
        prev = cur.fetchone()
        if prev and isinstance(prev.get("created_at"), datetime):
            if datetime.now() - prev["created_at"] < timedelta(seconds=5):
                cur.close(); conn.close()
                return jsonify({"message": "Duplicate ignored"}), 200
        cur.execute(
            "INSERT INTO feedbacks(username,message,rating,created_at) VALUES (%s,%s,%s,%s)",
            (d.get("username"), d["message"], rating, datetime.now())
        )
        conn.commit()
    finally:
        cur.close(); conn.close()
    return jsonify({"message": "Feedback saved"}), 201

@app.route("/api/feedbacks", methods=["GET"])
def feedbacks():
    conn = db_conn("feedback"); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT username,message,rating,DATE_FORMAT(created_at,'%Y-%m-%d %H:%i:%s') AS created_at FROM feedbacks ORDER BY created_at DESC")
    data = cur.fetchall()
    cur.close(); conn.close()
    return jsonify({"success": True, "data": data})

# ======================== SEARCH (museum) =================
@app.route('/api/search', methods=['GET'])
def search_artifacts():
    query = request.args.get('name', '').lower().strip()
    if not query:
        return jsonify({"message": "Thiếu từ khóa tìm kiếm"}), 400
    results = []
    # Search in both di_vat and anh categories
    phan_loai = bao_tang_chung_tich.get("phan_loai", {})
    for category_name, items in phan_loai.items():
        for item in items:
            if (query in item.get("ten", "").lower()
                or query in item.get("mo_ta", "").lower()):
                hinh_anh = item.get("hinh_anh", "")
                # Handle both string and list for hinh_anh
                if isinstance(hinh_anh, list):
                    hinh_anh_str = ", ".join(hinh_anh)
                else:
                    hinh_anh_str = hinh_anh
                results.append({
                    "id": item.get("id"),
                    "category": category_name,
                    "ten": item.get("ten"),
                    "mo_ta": item.get("mo_ta"),
                    "hinh_anh": item.get("hinh_anh")
                })
    if not results:
        abort(404, description="Không tìm thấy hiện vật hoặc hình ảnh nào phù hợp.")
    return jsonify(results)

# ======================== WEATHER ========================
API_KEY = "50fb31ce1941d76978a0369cbf302a89"  # OpenWeather key của bạn

def get_current_weather():
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        "?q=Ho%20Chi%20Minh,VN&units=metric&lang=vi"
        f"&appid={API_KEY}"
    )
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

@app.route("/api/weather/current", methods=["GET"])
def current_weather():
    try:
        data = get_current_weather()
        result = {
            "thanh_pho": data.get("name"),
            "mo_ta": data.get("weather", [{}])[0].get("description"),
            "nhiet_do": data.get("main", {}).get("temp"),
            "cam_nhan": data.get("main", {}).get("feels_like"),
            "do_am": data.get("main", {}).get("humidity"),
            "toc_do_gio": data.get("wind", {}).get("speed"),
            "time_unix": data.get("dt"),
        }
        return jsonify(result)
    except requests.HTTPError as he:
        return jsonify({"error": "OpenWeather HTTPError", "detail": str(he)}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ======================== MUSEUM LISTS ====================
# (Moved to top of file after imports)

@app.route("/api/artifacts", methods=["GET"])
def get_artifacts():
    items = PHAN_LOAI.get("di_vat", [])
    return jsonify(items)  # Return items directly

@app.route("/api/photos", methods=["GET"])
def get_photos():
    items = PHAN_LOAI.get("anh", [])
    return jsonify(items)  # Return items directly

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "Running ✅",
        "museum_name": TEN_BAO_TANG,
        "address": DIA_CHI_BAO_TANG,
        "ticket_price": f"{TICKET_PRICE:,}đ",
        "endpoints_available": {
            "/api/artifacts": "Danh sách Di vật",
            "/api/photos": "Danh sách Ảnh & Mô phỏng",
            "/api/weather/current": "Thời tiết hiện tại TP.HCM",
            "/api/register": "Đăng ký",
            "/api/login": "Đăng nhập",
            "/api/check-session": "Kiểm tra phiên",
            "/api/logout": "Đăng xuất",
            "/api/ticket/purchase": "Mua vé (POST: bank_account, bank_password)",
            "/api/ticket/status": "Kiểm tra trạng thái vé",
            "/api/ticket/verify": "Xác minh mã vé (POST: ticket_code)",
            "/api/bank/accounts": "Danh sách tài khoản ngân hàng giả lập",
            "/api/checkin/scan-with-info": "Check-in + AI info + Quiz (GET/POST: dia_diem)",
            "/api/checkin/submit-quiz": "Submit quiz answers (POST: dia_diem, answers, correct_answers)",
            "/api/checkin/*": "Check-in QR (legacy)",
            "/api/feedback": "Gửi feedback",
            "/api/feedbacks": "List feedback",
            "/api/ai/agent": "AI Agent",
            "/api/ask": "Ask AI",
            "/api/provinces": "Provinces list"
        }
    })

# ======================== RUN ============================
if __name__ == "__main__":
    app.run(debug=True, port=3000, host="0.0.0.0")
