from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    # TODO: Implement prediction logic
    prediction = 0.5  # placeholder
    return jsonify({'score': prediction})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)