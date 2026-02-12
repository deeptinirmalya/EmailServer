from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
import threading
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

app.secret_key = os.getenv("FLASK_SECRET_KEY")


# -------------------- HEALTH CHECK --------------------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"success": "✅ Service running"}), 200


# -------------------- EMAIL WORKER --------------------
def send_email_async(subject, body, receiver_email, body_type):
    try:
        print("🔥 THREAD STARTED")
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "465"))
        sender_email = os.getenv("EMAIL_USER")
        sender_pass = os.getenv("EMAIL_PASSWORD")
        display_name = os.getenv("DISPLAY_NAME", "My App Name")

        print(smtp_host, smtp_port, sender_email)

        if not all([smtp_host, smtp_port, sender_email, sender_pass]):
            print("❌ SMTP credentials missing")
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        
        msg["From"] = formataddr((display_name, sender_email))
        
        msg["To"] = receiver_email

        mime_type = "html" if body_type == "html" else "plain"
        msg.attach(MIMEText(body, mime_type, "utf-8"))

        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
            server.login(sender_email, sender_pass)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        print(f"✅ Email sent Successfully")

    except Exception as e:
        print("❌ SMTP ERROR:", e)


# -------------------- SEND EMAIL API --------------------
@app.route("/accept-email-iv", methods=["POST"])
def send_mail():

    # API KEY CHECK
    client_key = request.headers.get("X-API-KEY")
    if client_key != os.getenv("ROUT_API_KEY"):
        return jsonify({"error": "Unauthorized"}), 401

    # JSON CHECK
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    data = request.get_json()

    # REQUIRED FIELDS
    required_fields = ["subject", "body", "receiver_email", "body_type"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({"error": "Missing fields", "fields": missing}), 400

    subject = data["subject"].strip()
    body = data["body"].strip()
    receiver_email = data["receiver_email"].strip()
    body_type = data["body_type"].strip().lower()

    if body_type not in ("html", "text"):
        return jsonify({"error": "Invalid body_type"}), 400

    # 🚀 FIRE & FORGET
    thread = threading.Thread(
        target=send_email_async,
        args=(subject, body, receiver_email, body_type)
    )
    thread.start()

    # ⚡ IMMEDIATE RESPONSE
    return jsonify({
        "status": "accepted",
        "message": "Email queued"
    }), 202


# -------------------- RUN APP --------------------
if __name__ == "__main__":
    print("🚀 Starting email service")
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False,
        threaded=True
    )