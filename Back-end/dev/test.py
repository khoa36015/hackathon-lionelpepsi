from Flask import Flask, jsonify, request
app = Flask(__name__)
@app.route('/test', methods=['GET'])
def test_endpoint():
    response = {
        'status': 'success',
        'message': 'Test endpoint is working!'
    }
    return jsonify(response), 200