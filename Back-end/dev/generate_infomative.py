from flask import Flask, jsonify
from flask_cors import CORS
from data import bao_tang_chung_tich  # File data.py chứa biến này

app = Flask(__name__)
CORS(app)  # Cho phép tất cả domain, nếu cần credential thì thêm supports_credentials=True

@app.route("/api/museum-data", methods=["GET"])
def get_museum_data():
    """
    Trả về toàn bộ thông tin của Bảo tàng Chứng tích Chiến tranh:
    - Tên bảo tàng
    - Địa chỉ
    - Tổng số hiện vật
    - Phân loại hiện vật (ảnh, di vật)
    """

    phan_loai = bao_tang_chung_tich.get("phan_loai", {})
    # Tính tổng số hiện vật an toàn
    total_items = sum(len(phan_loai.get(k, [])) for k in ["anh", "di_vat"])

    response_data = {
        "ten_bao_tang": bao_tang_chung_tich.get("ten", ""),
        "dia_chi": bao_tang_chung_tich.get("dia_chi", ""),
        "total_items": total_items,
        "phan_loai_hien_vat": phan_loai
    }

    return jsonify(response_data)


if __name__ == "__main__":
    # Chạy local, debug=True chỉ dùng cho dev
    app.run(debug=True, port=5000)
