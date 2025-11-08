from flask import Flask, jsonify
from flask_cors import CORS
from data import bao_tang_chung_tich  # Đảm bảo file data.py có biến này

app = Flask(__name__)
CORS(app, supports_credentials=True)

# --- Chuẩn bị dữ liệu gốc ---
PHAN_LOAI = bao_tang_chung_tich.get("phan_loai", {})
TEN_BAO_TANG = bao_tang_chung_tich.get("ten", "Bảo tàng Chứng tích Chiến tranh")
DIA_CHI_BAO_TANG = bao_tang_chung_tich.get("dia_chi", "Không rõ địa chỉ")

# --- Route: Lấy danh sách Di vật ---
@app.route("/api/artifacts", methods=["GET"])
def get_artifacts():
    artifacts_list = PHAN_LOAI.get("di_vat", [])
    return jsonify({
        "museum_name": TEN_BAO_TANG,
        "category": "Di vật / Artifacts",
        "total": len(artifacts_list),
        "items": artifacts_list
    }), 200


# --- Route: Lấy danh sách Ảnh & Mô phỏng ---
@app.route("/api/photos", methods=["GET"])
def get_photos():
    photos_list = PHAN_LOAI.get("anh", [])
    return jsonify({
        "museum_name": TEN_BAO_TANG,
        "category": "Ảnh & Mô phỏng / Photos & Exhibits",
        "total": len(photos_list),
        "items": photos_list
    }), 200


# --- Route mặc định (trang giới thiệu API) ---
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "Running ✅",
        "museum_name": TEN_BAO_TANG,
        "address": DIA_CHI_BAO_TANG,
        "endpoints_available": {
            "/api/artifacts": "Danh sách các Di vật (xe tăng, máy bay, súng, bom...)",
            "/api/photos": "Danh sách các Bức ảnh & khu trưng bày mô phỏng (Da cam, Napalm, Chuồng cọp...)"
        }
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
