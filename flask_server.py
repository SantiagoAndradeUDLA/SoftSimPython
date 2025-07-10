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
    content = request.get_json(silent=True) # silent=True to prevent raising an exception on bad JSON
    if content is None:
        # This happens if the request body is not valid JSON or content-type is not application/json
        print("Error: Received invalid JSON or incorrect content-type.")
        return jsonify({"status": "error", "message": "Invalid JSON data or Content-Type header."}), 400
    
    # Basic validation: Check if expected keys are present (optional, but good practice)
    expected_keys = ['voltaje', 'corriente', 'potencia', 'energia']
    if not all(key in content for key in expected_keys):
        print(f"Warning: Received data is missing some expected keys. Data: {content}")
        # Decide if this is an error or just a warning. For now, accept partial data.
        # return jsonify({"status": "error", "message": "Missing some data fields."}), 400

    print(f"Received data: {content}") # Log received data
    latest_data.update(content)
    return jsonify({"status": "ok", "message": "Data updated successfully."}), 200

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(latest_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
