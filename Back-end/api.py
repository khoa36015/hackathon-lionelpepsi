from flask import Flask, jsonify, request, session, abort
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_cors import CORS
from datetime import datetime, timedelta
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import pymysql


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


def get_conn():
    """Kết nối MySQL"""
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


@app.after_request
def add_cors_headers(resp):
    """Thêm CORS header"""
    resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


# ==================== REGISTER ====================
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    user_id = (data.get("user_id") or "").strip()
    password = data.get("password") or ""

    if not user_id or not password:
        return jsonify({"ok": False, "error": "Thiếu user_id hoặc password"}), 400

    hashed_pw = generate_password_hash(password)

    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (user_id, mat_khau) VALUES (%s, %s)",
                (user_id, hashed_pw),
            )
        return jsonify({"ok": True, "message": "Đăng ký thành công"})
    except pymysql.err.IntegrityError:
        return jsonify({"ok": False, "error": "user_id đã tồn tại"}), 409
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ==================== LOGIN ====================
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    user_id = (data.get("user_id") or "").strip()
    password = data.get("password") or ""

    if not user_id or not password:
        return jsonify({"ok": False, "error": "Thiếu user_id hoặc password"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()

    if not user:
        return jsonify({"ok": False, "error": "Không tìm thấy user"}), 404

    if not check_password_hash(user["mat_khau"], password):
        return jsonify({"ok": False, "error": "Sai mật khẩu"}), 401

    session.permanent = True
    session["user_id"] = user_id
    return jsonify({"ok": True, "message": "Đăng nhập thành công", "user_id": user_id})


# ==================== LOGOUT ====================
@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"ok": True, "message": "Đã đăng xuất"})


# ==================== CHECK SESSION ====================
@app.route("/api/check-session", methods=["GET"])
def check_session():
    # Chỉ cho phép các origin dev mà bạn đang dùng (thêm/bớt tại đây nếu cần)
    allowed = {
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    }
    origin = request.headers.get("Origin")

    uid = session.get("user_id")
    if not uid:
        resp = jsonify({"logged_in": False, "user": None})
        if origin in allowed:
            resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Vary"] = "Origin"
        return resp

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT user_id, trang_thai, diem_thuong FROM users WHERE user_id = %s",
            (uid,),
        )
        user = cur.fetchone()

    if not user:
        resp = jsonify({"logged_in": False, "user": None})
    else:
        resp = jsonify({"logged_in": True, "user": user})

    # 🔒 Echo đúng Origin (không dùng '*') và bật credentials cho route này
    if origin in allowed:
        resp.headers["Access-Control-Allow-Origin"] = origin
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers["Vary"] = "Origin"
    return resp

if __name__ == "__main__":
    app.run(debug=True, port=3000, use_reloader=False,host='0.0.0.0')