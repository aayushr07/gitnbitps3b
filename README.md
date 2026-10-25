# AICTE APAAR ID Platform - Backend Service

An AI-powered student data management, verification, and multi-level approval platform for AICTE-approved institutions under Smart India Hackathon (SIH26263).

## 🚀 Key Features

- **AI-Based APAAR Verification Engine**: Aadhaar demographic fuzzy matching, mandatory student consent compliance, duplicate/ghost student detection, and AICTE accreditation validation.
- **Multi-Level Verification State Machine**: 4-tier approval pipeline (College Operator ➔ Institution Verifier ➔ Authorized Reviewer ➔ AICTE Central Admin).
- **AI Data Quality Assistant**: Pre-submission database hygiene audit, anomaly detection, typo normalization, and 1-click suggested fixes.
- **Verifiable QR Code Generation**: Generates cryptographically verifiable QR codes for APAAR student cards.
- **MongoDB Integration**: MongoDB Atlas persistence with high-performance in-memory fallback.

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Flask** & **Flask-CORS**
- **PyMongo** (MongoDB Driver)
- **QRCode & Pillow** (Dynamic QR Generation)
- **python-dotenv**

---

## ⚙️ Setup & Installation

1. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Add your `MONGO_URI` in `.env` (or leave it blank to run in local in-memory mode with pre-seeded demo records).

4. **Run the Backend Server**:
   ```bash
   python app.py
   ```
   The API will be available at `http://127.0.0.1:5000`.

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/ai-verify-student` | Multi-factor AI verification for new student APAAR ID |
| `GET` | `/api/ai-verify-student/presets` | 4 ready-to-test SIH evaluator demo cases |
| `POST` | `/api/verify-apaar` | APAAR ID & QR token instant verification |
| `GET` | `/api/workflow/records` | Multi-level approval applications queue |
| `POST` | `/api/workflow/action` | Authority approval, rejection, or flagging |
| `POST` | `/api/data-quality/analyze` | AI pre-submission data quality audit |
| `GET` | `/api/students` | Central student repository query & filters |
| `GET` | `/api/generate-qr/<id>` | Dynamic verifiable QR code image or base64 |
