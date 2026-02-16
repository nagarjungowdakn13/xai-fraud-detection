from flask import Flask, send_from_directory
import os

# Resolve the built frontend directory (../frontend/dist) relative to this file
STATIC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'dist')
)

app = Flask(__name__, static_folder=STATIC_DIR)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)