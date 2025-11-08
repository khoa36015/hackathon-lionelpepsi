from flask import Flask, jsonify, request, session, abort
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_cors import CORS
from datetime import datetime, timedelta
import mysql.connector
from data1 import dulieu

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


# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(debug=True, port=3000, use_reloader=False,host='0.0.0.0')
