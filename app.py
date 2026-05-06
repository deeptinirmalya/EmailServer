import os
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['MAIL_SERVER'] = os.getenv("SMTP_HOST", "smtp.gmail.com")
app.config['MAIL_PORT'] = int(os.getenv("SMTP_PORT", 465))
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USER")
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASSWORD")
app.config['ROUT_API_KEY'] = os.getenv("ROUT_API_KEY")

mail = Mail(app)

def send_email_sync(subject, receiver_email, body, authority_name, body_type):
    """Sends email synchronously within the request context."""
    try:
        msg = Message(
            subject=subject,
            sender=(authority_name, app.config['MAIL_USERNAME']),
            recipients=[receiver_email]
        )
        if body_type == "html":
            msg.html = body
        else:
            msg.body = body
        
        mail.send(msg)
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)

@app.route('/health', methods=['GET'])
def health_check():
    return {
        "status": "running",
        "message": "Email server is active (Synchronous Mode)",
        "environment": "production"
    }, 200

@app.route("/send-email", methods=["POST"])
def send_mail_route():
    # API Key Validation
    if request.headers.get("X-API-KEY") != app.config['ROUT_API_KEY']:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON required"}), 400

    required = ["subject", "body", "receiver_email", "authority_name"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Email Validation
    try:
        validate_email(data["receiver_email"])
    except EmailNotValidError as e:
        return jsonify({"error": str(e)}), 400

    # Execute sending (Synchronous)
    success, message = send_email_sync(
        data["subject"].strip(),
        data["receiver_email"].strip(),
        data["body"].strip(),
        data["authority_name"].strip(),
        data.get("body_type", "text")
    )

    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500

if __name__ == "__main__":
    app.run()