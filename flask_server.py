from flask import Flask, request, jsonify

app = Flask(__name__)

latest_data = {
    'voltaje': 0.0,
    'corriente': 0.0,
    'potencia': 0.0,
    'energia': 0.0
}

@app.route('/update', methods=['POST'])
def update():
    global latest_data
    content = request.get_json()
    latest_data.update(content)
    return jsonify({"status": "ok"}), 200

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(latest_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
