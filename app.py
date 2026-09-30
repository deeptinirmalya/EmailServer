import os
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
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

MAX_RECIPIENTS = 500


def get_recipient_list(data, field, required=False):
    recipients = data.get(field)
    if field == "receiver_email" and isinstance(recipients, str):
        recipients = [recipients]
    if recipients is None:
        recipients = []
    if not isinstance(recipients, list):
        raise ValueError(f"{field} must be a list of email addresses")
    if required and not recipients:
        raise ValueError(f"Missing field: {field}")

    cleaned_recipients = []
    for recipient in recipients:
        if not isinstance(recipient, str) or not recipient.strip():
            raise ValueError(f"{field} must contain only non-empty email addresses")
        try:
            validate_email(recipient.strip())
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email in {field}: {e}") from e
        cleaned_recipients.append(recipient.strip())
    return cleaned_recipients


def background_send_email(subject, receiver_emails, cc_emails, bcc_emails, body, authority_name, body_type):
    with app.app_context():
        try:
            msg = Message(
                subject=subject,
                sender=(authority_name, app.config['MAIL_USERNAME']),
                recipients=receiver_emails,
                cc=cc_emails,
                bcc=bcc_emails
            )
            if body_type == "html":
                msg.html = body
            else:
                msg.body = body

            mail.send(msg)
            print(f"Success: Email sent to {len(receiver_emails) + len(cc_emails) + len(bcc_emails)} recipients")
        except Exception as e:
            print(f"Error sending email: {str(e)}")


@app.route('/health', methods=['GET'])
def health_check():
    return {
        "status": "running",
        "message": "Email server is active",
        "environment": "production"
    }, 200


@app.route("/send-email", methods=["POST"])
def send_mail_route():

    if request.headers.get("X-API-KEY") != app.config['ROUT_API_KEY']:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON required"}), 400

    required = ["subject", "body", "authority_name"]
    for field in required:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        receiver_emails = get_recipient_list(data, "receiver_email", required=True)
        cc_emails = get_recipient_list(data, "cc")
        bcc_emails = get_recipient_list(data, "bcc")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if len(receiver_emails) + len(cc_emails) + len(bcc_emails) > MAX_RECIPIENTS:
        return jsonify({"error": f"A maximum of {MAX_RECIPIENTS} total recipients is allowed"}), 400

    background_send_email(
        data["subject"].strip(),
        receiver_emails,
        cc_emails,
        bcc_emails,
        data["body"].strip(),
        data["authority_name"].strip(),
        data.get("body_type", "text")
    )

    return jsonify({"status": "Success", "message": "Email sent successfully"}), 200

if __name__ == "__main__":
    app.run()