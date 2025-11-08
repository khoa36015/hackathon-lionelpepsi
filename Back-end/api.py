# ======================== IMPORTS ========================
from flask import Flask, jsonify, request, abort
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

# Dữ liệu bảo tàng
from data import  bao_tang_chung_tich  # ✅ bạn đã có file data.py

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

# ---- CORS (mở rộng cho dev) ----
CORS(app, supports_credentials=True)

@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    resp.headers["Vary"] = "Origin"
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

# ======================== AUTH ============================
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "").strip()
    password = data.get("password") or ""
    if not user_id or not password:
        return jsonify({"ok": False, "error": "Thiếu user_id hoặc password"}), 400

    hashed_pw = generate_password_hash(password)
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO users (user_id, mat_khau) VALUES (%s, %s)", (user_id, hashed_pw))
        return jsonify({"ok": True, "message": "Đăng ký thành công"})
    except pymysql.err.IntegrityError:
        return jsonify({"ok": False, "error": "user_id đã tồn tại"}), 409
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "").strip()
    password = data.get("password") or ""
    if not user_id or not password:
        return jsonify({"ok": False, "error": "Thiếu user_id hoặc password"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        user = cur.fetchone()
    if not user:
        return jsonify({"ok": False, "error": "Không tìm thấy user"}), 404
    if not check_password_hash(user["mat_khau"], password):
        return jsonify({"ok": False, "error": "Sai mật khẩu"}), 401

    token = create_token(user_id)
    return jsonify({"ok": True, "message": "Đăng nhập thành công", "user_id": user_id, "token": token})

@app.route("/api/check-session", methods=["GET"])
def check_session():
    user_id = verify_token(request)
    if not user_id:
        return jsonify({"logged_in": False, "user": None})
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT user_id, trang_thai, diem_thuong FROM users WHERE user_id=%s", (user_id,))
        user = cur.fetchone()
    if not user:
        return jsonify({"logged_in": False, "user": None})
    return jsonify({"logged_in": True, "user": user})

@app.route("/api/logout", methods=["POST"])
def logout():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1].strip()
        session_cache.pop(token, None)
    return jsonify({"ok": True, "message": "Đã đăng xuất"})

# ======================== TICKET ==========================
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

@app.route("/api/ticket/status", methods=["GET"])
def ticket_status():
    user_id = (request.args.get("user_id") or "").strip()
    if not user_id:
        return jsonify({"ok": False, "error": "Thiếu user_id"}), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT user_id, trang_thai, diem_thuong FROM users WHERE user_id=%s", (user_id,))
        row = cur.fetchone()
    if not row:
        return jsonify({"ok": False, "error": "Không tìm thấy user"}), 404
    return jsonify({"ok": True, "user": row, "purchased": bool(row["trang_thai"] == 1)})

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
    sql = """
    CREATE TABLE IF NOT EXISTS checkin (
      id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      user VARCHAR(190) NOT NULL,
      dia_diem VARCHAR(255) NOT NULL,
      checkin TINYINT(1) NOT NULL DEFAULT 0,
      PRIMARY KEY (id),
      UNIQUE KEY uk_user_dia_diem (user, dia_diem)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
ensure_checkin_table()

def upsert_checkin(user_id: str, dia_diem: str, checked: int = 1):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE checkin SET checkin=%s WHERE user=%s AND dia_diem=%s", (checked, user_id, dia_diem))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO checkin(user, dia_diem, checkin) VALUES (%s,%s,%s)", (user_id, dia_diem, checked))
        cur.execute("SELECT user, dia_diem, checkin FROM checkin WHERE user=%s AND dia_diem=%s", (user_id, dia_diem))
        return cur.fetchone()

def get_checkin(user_id: str, dia_diem: str):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT user, dia_diem, checkin FROM checkin WHERE user=%s AND dia_diem=%s", (user_id, dia_diem))
        return cur.fetchone()

@app.route("/api/qr/link", methods=["GET"])
def qr_link():
    user_id = verify_token(request)
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
    user_id = verify_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập. Hãy đăng nhập rồi quét lại."}), 401
    dia_diem = (request.args.get("dia_diem") or "").strip()
    if not dia_diem:
        return jsonify({"ok": False, "error": "Thiếu dia_diem"}), 400
    row = upsert_checkin(user_id, dia_diem, checked=1)
    return jsonify({"ok": True, "message": f"Đã check-in {dia_diem}", "data": row})

@app.route("/api/checkin/mark", methods=["POST"])
def checkin_mark():
    user_id = verify_token(request)
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
    user_id = verify_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401
    dia_diem = (request.args.get("dia_diem") or "").strip()
    if not dia_diem:
        return jsonify({"ok": False, "error": "Thiếu dia_diem"}), 400
    row = get_checkin(user_id, dia_diem)
    return jsonify({"ok": True, "user": user_id, "dia_diem": dia_diem, "checked": bool(row and row.get("checkin") == 1)})

@app.route("/api/checkin/list", methods=["GET"])
def checkin_list():
    user_id = verify_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT dia_diem, checkin FROM checkin WHERE user=%s AND checkin=1 ORDER BY dia_diem", (user_id,))
        rows = cur.fetchall()
    return jsonify({"ok": True, "data": rows})

@app.route("/api/checkin/visited", methods=["GET"])
def checkin_visited():
    user_id = verify_token(request)
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
    for key, info in dulieu.items():
        hien_vat_list = info.get("hien_vat", [])
        for hv in hien_vat_list:
            if (query in hv.get("ten", "").lower()
                or query in hv.get("mo_ta", "").lower()
                or query in hv.get("hinh_anh", "").lower()):
                results.append({
                    "id": key,
                    "ten_khu_vuc": info.get("ten", "Không rõ"),
                    "ten_hien_vat": hv.get("ten"),
                    "mo_ta": hv.get("mo_ta"),
                    "hinh_anh": hv.get("hinh_anh")
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
PHAN_LOAI = bao_tang_chung_tich.get("phan_loai", {})
TEN_BAO_TANG = bao_tang_chung_tich.get("ten", "Bảo tàng Chứng tích Chiến tranh")
DIA_CHI_BAO_TANG = bao_tang_chung_tich.get("dia_chi", "Không rõ địa chỉ")

@app.route("/api/artifacts", methods=["GET"])
def get_artifacts():
    items = PHAN_LOAI.get("di_vat", [])
    return jsonify({"museum_name": TEN_BAO_TANG, "category": "Di vật / Artifacts", "total": len(items), "items": items})

@app.route("/api/photos", methods=["GET"])
def get_photos():
    items = PHAN_LOAI.get("anh", [])
    return jsonify({"museum_name": TEN_BAO_TANG, "category": "Ảnh & Mô phỏng / Photos & Exhibits", "total": len(items), "items": items})

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "Running ✅",
        "museum_name": TEN_BAO_TANG,
        "address": DIA_CHI_BAO_TANG,
        "endpoints_available": {
            "/api/artifacts": "Danh sách Di vật",
            "/api/photos": "Danh sách Ảnh & Mô phỏng",
            "/api/weather/current": "Thời tiết hiện tại TP.HCM",
            "/api/register": "Đăng ký",
            "/api/login": "Đăng nhập",
            "/api/check-session": "Kiểm tra phiên",
            "/api/logout": "Đăng xuất",
            "/api/ticket/*": "Vé",
            "/api/checkin/*": "Check-in QR",
            "/api/feedback": "Gửi feedback",
            "/api/feedbacks": "List feedback"
        }
    })

# ======================== RUN ============================
if __name__ == "__main__":
    app.run(debug=True, port=3000, host="0.0.0.0")
