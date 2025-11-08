from flask import Flask, jsonify, request, session, abort
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_cors import CORS
from datetime import datetime, timedelta
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import secrets
from datetime import datetime, timedelta
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Secret key và session config
app.secret_key = "super-secret-dev-key"
app.config.update(
    SESSION_TYPE='filesystem',
    PERMANENT_SESSION_LIFETIME=timedelta(days=1),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False  # dev mode
)
Session(app)

# ✅ CORS cấu hình cho dev (cho phép credentials)
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5500"])

# ---------- DB ----------
def db_conn(db_name):
    return mysql.connector.connect(
        host="34.136.163.31",
        user="admin",
        password="Kv135791!",
        database=db_name
    )



# ---------- FEEDBACK ----------
@app.route("/api/feedback", methods=["POST"])
def feedback():
    d = request.get_json() or {}
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

@app.route("/api/feedbacks")
def feedbacks():
    conn = db_conn("feedback"); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT username,message,rating,DATE_FORMAT(created_at,'%Y-%m-%d %H:%i:%s') AS created_at FROM feedbacks ORDER BY created_at DESC")
    data = cur.fetchall()
    cur.close(); conn.close()
    return jsonify({"success": True, "data": data})


# ✅ Tìm kiếm hiện vật hoặc hình ảnh trưng bày
@app.route('/api/search', methods=['GET'])
def search_artifacts():
    query = request.args.get('name', '').lower().strip()
    if not query:
        return jsonify({"message": "Thiếu từ khóa tìm kiếm"}), 400

    results = []

    # Duyệt qua từng khu vực/tỉnh trong dữ liệu
    for key, info in dulieu.items():
        hien_vat_list = info.get("hien_vat", [])

        for hv in hien_vat_list:
            if (
                query in hv.get("ten", "").lower() or
                query in hv.get("mo_ta", "").lower() or
                query in hv.get("hinh_anh", "").lower()
            ):
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

API_KEY = "50fb31ce1941d76978a0369cbf302a89"

# Hàm lấy thời tiết hiện tại ở TP.HCM
def get_current_weather():
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q=Ho%20Chi%20Minh,VN&appid={API_KEY}&units=metric&lang=vi"
    )
    res = requests.get(url)
    return res.json()

@app.route("/api/weather/current", methods=["GET"])
def current_weather():
    try:
        data = get_current_weather()
        # Lọc bớt dữ liệu, chỉ trả thông tin chính
        result = {
            "thanh_pho": data.get("name"),
            "mo_ta": data["weather"][0]["description"],
            "nhiet_do": data["main"]["temp"],
            "cam_nhan": data["main"]["feels_like"],
            "do_am": data["main"]["humidity"],
            "toc_do_gio": data["wind"]["speed"],
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ---------- MAIN ----------
DB_HOST = "34.136.163.31"
DB_PORT = 3306
DB_USER = "admin"
DB_PASS = "Kv135791!"
DB_NAME = "authen"  # tên database trong file authen.sql

SECRET_KEY = "change_this_secret_123"  # đổi khi dùng thật

# ==================== KHỞI TẠO APP ====================
app = Flask(__name__)
app.config.update(
    SECRET_KEY=SECRET_KEY,
    JSON_AS_ASCII=False,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
)
CORS(app, supports_credentials=True)


session_cache = {}

app = Flask(__name__)
CORS(app, supports_credentials=True)

# ================= DB CONNECT =================
def get_conn():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS,
        database=DB_NAME, charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

# ================= HÀM TIỆN ÍCH =================
def create_token(user_id):
    token = secrets.token_hex(16)
    session_cache[token] = {
        "user_id": user_id,
        "expires": datetime.utcnow() + timedelta(hours=12)
    }
    return token

def verify_token(req):
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1].strip()
    data = session_cache.get(token)
    if not data:
        return None
    if data["expires"] < datetime.utcnow():
        del session_cache[token]
        return None
    return data["user_id"]

# ================= API =================
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
    return jsonify({
        "ok": True,
        "message": "Đăng nhập thành công",
        "user_id": user_id,
        "token": token
    })


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

from flask import request, jsonify

@app.route("/api/ticket/confirm", methods=["POST"])
def ticket_confirm():
    """
    Body JSON: { "user_id": "khoa" }
    -> Đánh dấu đã mua vé: trang_thai = 1
    """
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "").strip()
    if not user_id:
        return jsonify({"ok": False, "error": "Thiếu user_id"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        # cập nhật trạng_thai = 1 (đã mua vé)
        cur.execute("UPDATE users SET trang_thai = 1 WHERE user_id = %s", (user_id,))
        # lấy lại thông tin sau cập nhật
        cur.execute("SELECT user_id, trang_thai, diem_thuong FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()

    if not row:
        return jsonify({"ok": False, "error": "Không tìm thấy user"}), 404

    purchased = bool(row["trang_thai"] == 1)
    return jsonify({"ok": True, "message": "Đã xác nhận mua vé", "user": row, "purchased": purchased})


@app.route("/api/ticket/status", methods=["GET"])
def ticket_status():
    """
    Query: /api/ticket/status?user_id=khoa
    -> Trả về trạng thái đã mua hay chưa (purchased: true/false)
    """
    user_id = (request.args.get("user_id") or "").strip()
    if not user_id:
        return jsonify({"ok": False, "error": "Thiếu user_id"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT user_id, trang_thai, diem_thuong FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()

    if not row:
        return jsonify({"ok": False, "error": "Không tìm thấy user"}), 404

    purchased = bool(row["trang_thai"] == 1)
    return jsonify({"ok": True, "user": row, "purchased": purchased})


# (tuỳ chọn) bỏ xác nhận mua vé -> trang_thai = 0
@app.route("/api/ticket/cancel", methods=["POST"])
def ticket_cancel():
    """
    Body JSON: { "user_id": "khoa" }
    -> Đặt về chưa mua: trang_thai = 0
    """
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "").strip()
    if not user_id:
        return jsonify({"ok": False, "error": "Thiếu user_id"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE users SET trang_thai = 0 WHERE user_id = %s", (user_id,))
        cur.execute("SELECT user_id, trang_thai, diem_thuong FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()

    if not row:
        return jsonify({"ok": False, "error": "Không tìm thấy user"}), 404

    purchased = bool(row["trang_thai"] == 1)
    return jsonify({"ok": True, "message": "Đã huỷ xác nhận", "user": row, "purchased": purchased})



# =============== CHECKIN Qr ===============

import urllib.parse

def ensure_checkin_table():
    """Đảm bảo bảng checkin tồn tại (không tạo database mới)."""
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
ensure_checkin_table()  # gọi khi app khởi động  (bảng theo checkin.sql)

def upsert_checkin(user_id: str, dia_diem: str, checked: int = 1):
    """Tạo mới hoặc cập nhật checkin cho (user, dia_diem)."""
    with get_conn() as conn, conn.cursor() as cur:
        # cố gắng cập nhật trước
        cur.execute(
            "UPDATE checkin SET checkin=%s WHERE user=%s AND dia_diem=%s",
            (checked, user_id, dia_diem)
        )
        if cur.rowcount == 0:
            # chưa có bản ghi -> chèn mới
            cur.execute(
                "INSERT INTO checkin(user, dia_diem, checkin) VALUES (%s,%s,%s)",
                (user_id, dia_diem, checked)
            )
        # trả về trạng thái sau cùng
        cur.execute(
            "SELECT user, dia_diem, checkin FROM checkin WHERE user=%s AND dia_diem=%s",
            (user_id, dia_diem)
        )
        return cur.fetchone()

def get_checkin(user_id: str, dia_diem: str):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT user, dia_diem, checkin FROM checkin WHERE user=%s AND dia_diem=%s",
            (user_id, dia_diem)
        )
        return cur.fetchone()

@app.route("/api/qr/link", methods=["GET"])
def qr_link():
    """
    Tạo link để nhúng vào QR cho một địa điểm.
    Yêu cầu: đã đăng nhập (Bearer token).
    Query: ?dia_diem=...
    Trả: { url }  -> ví dụ: http://<host>:3000/api/checkin/scan?dia_diem=Ch%E1%BB%A3%20B%E1%BA%BFn%20Th%C3%A0nh
    """
    user_id = verify_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    dia_diem = (request.args.get("dia_diem") or "").strip()
    if not dia_diem:
        return jsonify({"ok": False, "error": "Thiếu dia_diem"}), 400

    # Tạo URL duy nhất cho địa điểm (token không nhúng vào link để tránh lộ; client phải gửi Authorization khi quét)
    encoded = urllib.parse.quote(dia_diem, safe="")
    host = request.host_url.rstrip("/")  # ví dụ http://localhost:3000
    url = f"{host}/api/checkin/scan?dia_diem={encoded}"
    return jsonify({"ok": True, "url": url})

@app.route("/api/checkin/scan", methods=["GET"])
def checkin_scan():
    """
    Endpoint đích của QR. Khi quét QR mở link này:
      - Trình gọi cần gửi kèm Authorization: Bearer <token> (ví dụ app/web đã lưu token).
      - Query: ?dia_diem=...
    Thành công -> đánh dấu checkin=1 cho user hiện tại tại địa điểm đó.
    """
    user_id = verify_token(request)
    if not user_id:
        # Không tự chuyển hướng login vì đây là API; trả lời rõ để frontend/app xử lý
        return jsonify({"ok": False, "error": "Chưa đăng nhập. Hãy đăng nhập rồi quét lại."}), 401

    dia_diem = (request.args.get("dia_diem") or "").strip()
    if not dia_diem:
        return jsonify({"ok": False, "error": "Thiếu dia_diem"}), 400

    row = upsert_checkin(user_id, dia_diem, checked=1)
    return jsonify({
        "ok": True,
        "message": f"Đã check-in {dia_diem}",
        "data": row,
    })

@app.route("/api/checkin/mark", methods=["POST"])
def checkin_mark():
    """
    Đánh dấu checkin bằng JSON (không cần dùng QR).
    Body: { "dia_diem": "..." }
    Yêu cầu: Bearer token.
    """
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
    """
    Trả trạng thái check-in của user hiện tại tại 1 địa điểm.
    Query: ?dia_diem=...
    Yêu cầu: Bearer token.
    """
    user_id = verify_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    dia_diem = (request.args.get("dia_diem") or "").strip()
    if not dia_diem:
        return jsonify({"ok": False, "error": "Thiếu dia_diem"}), 400

    row = get_checkin(user_id, dia_diem)
    return jsonify({
        "ok": True,
        "user": user_id,
        "dia_diem": dia_diem,
        "checked": bool(row and row.get("checkin") == 1)
    })

@app.route("/api/checkin/list", methods=["GET"])
def checkin_list():
    """
    Liệt kê các địa điểm user hiện tại đã check-in.
    Yêu cầu: Bearer token.
    """
    user_id = verify_token(request)
    if not user_id:
        return jsonify({"ok": False, "error": "Chưa đăng nhập"}), 401

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT dia_diem, checkin FROM checkin WHERE user=%s AND checkin=1 ORDER BY dia_diem",
            (user_id,)
        )
        rows = cur.fetchall()
    return jsonify({"ok": True, "data": rows})
# =============== CHECKIN: danh sách địa điểm đã đi ===============

@app.route("/api/checkin/visited", methods=["GET"])
def checkin_visited():
    """
    Trả danh sách địa điểm user hiện tại đã check-in (checkin=1).
    Yêu cầu: Authorization: Bearer <token>

    Query params (tùy chọn):
      - q: từ khóa tìm kiếm theo tên địa điểm (LIKE)
      - limit: số bản ghi mỗi trang (mặc định 50, tối đa 200)
      - offset: vị trí bắt đầu (mặc định 0)

    Response:
    {
      "ok": true,
      "user": "khoa",
      "total": 3,
      "limit": 50,
      "offset": 0,
      "data": [
        {"dia_diem": "Chợ Bến Thành", "checkin": 1},
        {"dia_diem": "Dinh Độc Lập", "checkin": 1},
        ...
      ]
    }
    """
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
        # đếm tổng
        cur.execute(f"SELECT COUNT(*) AS total FROM checkin WHERE {where_sql}", args)
        total = (cur.fetchone() or {}).get("total", 0)

        # lấy dữ liệu (sắp xếp id giảm dần ~ gần đúng theo thời điểm tạo)
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

    return jsonify({
        "ok": True,
        "user": user_id,
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": rows,
    })

if __name__ == "__main__":
    app.run(debug=True, port=3000, use_reloader=False,host='0.0.0.0')