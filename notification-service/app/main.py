from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MimeText
import os

app = Flask(__name__)

@app.route('/api/notifications/email', methods=['POST'])
def send_email():
    data = request.get_json()
    msg = MimeText(data['body'])
    msg['Subject'] = data['subject']
    msg['From'] = os.getenv('SMTP_FROM', 'noreply@fraudsystem.com')
    msg['To'] = data['to']

    with smtplib.SMTP(os.getenv('SMTP_HOST', 'localhost'), os.getenv('SMTP_PORT', 25)) as server:
        server.send_message(msg)
    return jsonify({'message': 'Email sent'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)