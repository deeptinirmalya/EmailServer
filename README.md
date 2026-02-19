# 🚀 Flask Async Email Server

A high-performance Flask API designed to handle asynchronous email delivery. Optimized for **PythonAnywhere**, this service uses multi-threading to ensure your main application remains responsive while emails are sent in the background.

[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

- **Asynchronous Execution:** Uses `threading` for a "Fire & Forget" architecture.
- **Secure Authentication:** Protected via custom `X-API-KEY` header validation.
- **HTML & Plain Text:** Supports both rich HTML templates and standard text.
- **PythonAnywhere Optimized:** Configured for WSGI hosting with static environment variable support.
- **Health Monitoring:** Dedicated `/health` endpoint for uptime checks.

---

## 🛠️ Environment Variables

To run this service, configure the following variables in your `.env` file located in `~/EmailServer/`:

| Key | Description | Example |
| :--- | :--- | :--- |
| `FLASK_SECRET_KEY` | Flask session security | `your_secret_string_here` |
| `ROUT_API_KEY` | Custom key for API Authentication | `my-secret-api-key` |
| `SMTP_HOST` | SMTP server address | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port (Use 587 for PythonAnywhere) | `587` |
| `EMAIL_USER` | Your email address | `example@gmail.com` |
| `EMAIL_PASSWORD` | 16-digit Google App Password | `xxxx xxxx xxxx xxxx` |


> **Note:** PythonAnywhere Free Tier requires Port **587** and TLS for outgoing mail.

---

## 📡 API Endpoints

### 1. Health Check
Check if the service is alive and the WSGI application is correctly loaded.
- **URL:** `https://servicestack.pythonanywhere.com/health`
- **Method:** `GET`
- **Response:** `{"status": "running", "message": "Email server is active"}`

### 2. Send Email
Queue an email for delivery.
- **URL:** `https://servicestack.pythonanywhere.com/accept-email-iv`
- **Method:** `POST`
- **Headers:** - `Content-Type: application/json`
  - `X-API-KEY: <your_rout_api_key>`
- **Body:**
```json
{
    "subject": "Welcome to the Platform!",
    "body": "<h1>Hello!</h1><p>Your account is ready.</p>",
    "receiver_email": "user@example.com",
    "body_type": "html"
}