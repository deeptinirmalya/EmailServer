import os
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_executor import Executor
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError

load_dotenv()

app = Flask(__name__)


app.config['MAIL_SERVER'] = os.getenv("SMTP_HOST", "smtp.gmail.com")
app.config['MAIL_PORT'] = int(os.getenv("SMTP_PORT", 465))
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USER")
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASSWORD")
app.config['ROUT_API_KEY'] = os.getenv("ROUT_API_KEY")

mail = Mail(app)
executor = Executor(app)


def background_send_email(subject, receiver_email, body, authority_name, body_type):
    with app.app_context():
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
            print(f"Success: Email sent to {receiver_email}")
        except Exception as e:
            print(f"Error sending email: {str(e)}")

@app.route("/send-email", methods=["POST"])
def send_mail_route():

    if request.headers.get("X-API-KEY") != app.config['ROUT_API_KEY']:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON required"}), 400

    required = ["subject", "body", "receiver_email", "authority_name"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        validate_email(data["receiver_email"])
    except EmailNotValidError as e:
        return jsonify({"error": str(e)}), 400


    executor.submit(
        background_send_email,
        data["subject"].strip(),
        data["receiver_email"].strip(),
        data["body"].strip(),
        data["authority_name"].strip(),
        data.get("body_type", "text")
    )

    return jsonify({"status": "Email queued", "message": "Sending in background"}), 202

if __name__ == "__main__":
    app.run()