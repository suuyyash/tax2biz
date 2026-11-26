# Tax2Biz Enterprise Backend Architecture & Security Guide

Welcome to the **Tax2Biz** production-grade backend built with **Python 3**, **FastAPI**, **SQLAlchemy 2.0 (Async)**, and **Pydantic v2**.

---

## 🚀 Quick Start on macOS

The virtual environment and all dependencies are already configured in `venv/`.

### 1. Start the Server
From your project directory (`/Users/sidsmac/Documents/tax2biz`):

```bash
./venv/bin/python run_backend.py
```
*(Or activate the virtualenv first: `source venv/bin/activate && python run_backend.py`)*

### 2. Live Endpoints & Interfaces
- **Interactive Swagger API Docs**: [http://localhost:8085/api/docs](http://localhost:8085/api/docs)
- **Interactive ReDoc Documentation**: [http://localhost:8085/api/redoc](http://localhost:8085/api/redoc)
- **Company Registration Landing Page**: [http://localhost:8085/private-limited-company-registration.html](http://localhost:8085/private-limited-company-registration.html)
- **Homepage**: [http://localhost:8085/index.html](http://localhost:8085/index.html)

---

## 🛡️ Security Architecture & Hardening Measures

This backend is engineered specifically to prevent common fintech/legaltech security vulnerabilities:

1. **Strict Input Validation & Sanitization**:
   - Pydantic v2 schemas enforce regex on all phone numbers (`^[6-9]\d{9}$`), validate RFC email formats, and sanitize founder names to prevent injection attacks.
2. **Sliding-Window OTP Rate Limiting**:
   - Limits OTP requests to **maximum 3 requests per 10 minutes per phone number** to prevent SMS pumping and denial-of-service.
3. **Cryptographic OTP Salting**:
   - Plaintext OTPs are **never stored** in the database. Each OTP is hashed with a per-session random cryptographic salt (`SHA-256(salt + otp)`).
   - Enforces a 10-minute expiry and a maximum of 5 verification attempts.
4. **Server-Side Price Integrity**:
   - The client never dictates the payment amount. Pricing is calculated and verified server-side based on the selected package (`Standard: ₹2,499`, etc.).
5. **PII Masking & Privacy**:
   - Phone numbers and emails are automatically masked in server logs (e.g. `+91 98*** **210`, `su***@gmail.com`).
6. **Security Headers Middleware**:
   - Protects against clickjacking (`X-Frame-Options: SAMEORIGIN`), MIME-sniffing (`X-Content-Type-Options: nosniff`), and suppresses the `Server` banner.
7. **Exception Shielding**:
   - Global exception handlers log detailed stack traces internally while returning clean, non-leaking JSON error payloads to users.

---

## 🔄 Demo Mode vs. Live Production Switching

The backend is configured with pluggable provider adapters:

| Capability | Demo Mode (Active Now) | Live Production Mode |
| :--- | :--- | :--- |
| **Payments** | `PAYMENT_MODE=DEMO`<br>Generates demo order IDs, simulates checkout, and creates audited receipts without real charges. | Set `PAYMENT_MODE=LIVE`<br>Add `RAZORPAY_KEY_ID` & `RAZORPAY_KEY_SECRET` in `.env`. |
| **OTP & SMS** | `NOTIFICATION_MODE=DEMO`<br>Prints OTP visibly in the server terminal and response for instant testing without SMS fees. | Set `NOTIFICATION_MODE=LIVE`<br>Add `SMS_API_KEY` (Gupshup / MSG91) in `.env`. |
| **Database** | `sqlite+aiosqlite:///./tax2biz.db`<br>Zero-configuration local database created automatically. | Set `DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/tax2biz` in `.env`. |

---

## 🧪 Automated Test Suite

Run the automated tests anytime using:

```bash
PYTHONPATH=. ./venv/bin/pytest backend/tests/ -v
```
All 4 test suites verify lead creation, input validation, rate limiting, security headers, and the trademark engine.
