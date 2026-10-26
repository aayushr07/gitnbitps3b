# AICTE APAAR ID Platform - Backend API Service

Integrated student data management, automated intake validation, and tamper-proof verification REST API for AICTE-approved institutions under the Automated Permanent Academic Account Registry (APAAR) initiative (*One Nation, One Student ID*).

## 🚀 Key Features

- **Automated APAAR & Intake Validation Engine (`POST /api/institution/validate`)**:
  - Duplicate student record detection within and across institutions.
  - 12-digit numeric APAAR validation & checksum integrity.
  - **Admissions Exceeding Approved Intake**: Detects institutions admitting students beyond AICTE sanctioned regular intake or violating supernumerary caps (10–15%).
  - Inconsistency detection: checks mandatory student IDs, consent status, and invalid quota claims.
- **Institution Post-Admission Data Ingestion (`POST /api/institution/upload-students`)**:
  - Secure batch ingestion of student records with Approved Intake, Supernumerary (TFW, EWS, Sports), NRI, OCI, and Foreign National (FN) categories.
- **AICTE Central Repository (`/api/students`)**:
  - Master student registry with APAAR ID as unique academic identifier.
  - Comprehensive filtering by institution, branch, category, and compliance status.
- **Authorized Stakeholder Verification Gateway (`POST /api/verify-apaar`)**:
  - Cryptographic verification for AICTE, institutions, employers (TCS, Infosys), and regulatory bodies.
  - Generates tamper-proof **SHA-256 cryptographic proof seals**.
  - Dynamic QR code generation (`/api/generate-qr/<apaar_id>`).
- **Real-Time Admission Monitoring & Policy Reports (`/api/analytics`, `/api/reports/admissions`)**:
  - Real-time intake vs enrolment monitoring and excess intake anomaly sentinel.
  - CSV report exports for AICTE Council, NAAC, and NIRF accreditation.
- **Institutional ERP / SIS REST Integration (`/api/v1/...`)**:
  - Headless API for university ERPs (SAP, PeopleSoft, Custom SIS) with `X-AICTE-API-KEY` authentication.

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Flask** & **Flask-CORS**
- **PyMongo** (MongoDB Driver with automatic in-memory fallback)
- **QRCode & Pillow** (Dynamic QR Generation)
- **python-dotenv**

---

## ⚙️ Setup & Installation

1. **Activate virtual environment**:
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

3. **Run the Backend Server**:
   ```bash
   python app.py
   ```
   *Runs by default on `http://127.0.0.1:5000`.*
