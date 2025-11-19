from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Service endpoints
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://user-service:5001')
TRANSACTION_SERVICE_URL = os.getenv('TRANSACTION_SERVICE_URL', 'http://transaction-service:5002')
ML_SERVICE_URL = os.getenv('ML_SERVICE_URL', 'http://ml-service:5003')
GRAPH_SERVICE_URL = os.getenv('GRAPH_SERVICE_URL', 'http://graph-service:5004')

@app.route('/api/users/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_service_proxy(path):
    response = requests.request(
        method=request.method,
        url=f'{USER_SERVICE_URL}/api/users/{path}',
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)
    return (response.content, response.status_code, response.headers.items())

@app.route('/api/transactions/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def transaction_service_proxy(path):
    response = requests.request(
        method=request.method,
        url=f'{TRANSACTION_SERVICE_URL}/api/transactions/{path}',
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)
    return (response.content, response.status_code, response.headers.items())

# Similar routes for other services...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)