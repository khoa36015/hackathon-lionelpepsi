import json
from flask import Flask, request, jsonify
import database_connector 

app = Flask(__name__)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_db_password',
    'database': 'authen'
}

def get_user_status(user_id):
    """Truy vấn CSDL để lấy trạng thái mua vé (trang_thai)."""
    conn = None
    cursor = None
    try:
        conn = database_connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "SELECT trang_thai FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result: 
            return result[0]
        else:
            return -1 
    except Exception as e:
        print(f"Lỗi CSDL: {e}")
        return -2
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@app.route('/api/v1/check-ticket', methods=['POST'])
def check_ticket():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({
            "success": False, 
            "message": "Thiếu user_id"
        }), 400
    status = get_user_status(user_id)
    if status == -2:
        return jsonify({
            "success": False, 
            "message": "Lỗi kết nối hoặc truy vấn cơ sở dữ liệu"
        }), 500
    if status == -1:
        return jsonify({
            "success": False, 
            "message": "User_id không tồn tại"
        }), 404 
    is_ticket_purchased = (status == 1) 
    return jsonify({
        "success": True,
        "user_id": user_id,
        "has_ticket": is_ticket_purchased,
        "status_code": status 
    })

if __name__ == '__main__':
    app.run(debug=True)