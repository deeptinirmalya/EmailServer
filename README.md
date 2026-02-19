# 🚀 Flask Async Email Server

A high-performance, production-ready Flask API designed to handle asynchronous email delivery. Built with security and scalability in mind, this service uses multi-threading to ensure your main application remains responsive while emails are sent in the background.

[![Deployed on Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://www.koyeb.com/)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

- **Asynchronous Execution:** Uses `threading` for a "Fire & Forget" architecture.
- **Secure Authentication:** Protected via custom `X-API-KEY` header validation.
- **HTML & Plain Text:** Supports both rich HTML templates and standard text.
- **Cloud Native:** Optimized for **Koyeb** with Gunicorn and dynamic port binding.
- **Health Monitoring:** Dedicated `/health` endpoint for uptime checks.

---

## 🛠️ Environment Variables

To run this service, configure the following variables in your **Koyeb Dashboard** or local `.env` file:

| Key | Description | Example |
| :--- | :--- | :--- |
| `FLASK_SECRET_KEY` | Flask session security | `your_secret_string_here` |
| `ROUT_API_KEY` | Custom key for API Authentication | `my-secret-api-key` |
| `SMTP_HOST` | SMTP server address | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `465` |
| `EMAIL_USER` | Your email address | `example@gmail.com` |
| `EMAIL_PASSWORD` | 16-digit Google App Password | `xxxx xxxx xxxx xxxx` |
| `DISPLAY_NAME` | Name shown to email recipients | `Support Team` |

---

## 📡 API Endpoints

### 1. Health Check
Check if the service is alive.
- **URL:** `/health`
- **Method:** `GET`
- **Response:** `{"success": "✅ Service running"}`

### 2. Send Email
Queue an email for delivery.
- **URL:** `/accept-email-iv`
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
