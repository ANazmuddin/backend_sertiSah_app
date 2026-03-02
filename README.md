---

# 📜 SertiSah Backend

Blockchain-Based Academic Certificate Verification System

---

## 📌 Overview

SertiSah Backend is a FastAPI-based system for issuing and verifying academic certificates digitally.
Each certificate:

* Is generated as an official PDF
* Contains a unique SHA-256 hash
* Embeds a QR Code for verification
* Is stored immutably on Polygon (Amoy Testnet) blockchain
* Can be verified through REST API or Android application

The system includes:

* 🔐 Role-Based Admin Authentication (RBAC)
* 📄 Certificate Generation
* 🔗 Blockchain Integration (Web3.py)
* 📊 Admin Dashboard
* 🧾 Audit Logging System
* 📱 Public API for Android Verification

---

## 🏗️ Tech Stack

* **FastAPI** – Backend framework
* **SQLite** – Database
* **SQLAlchemy** – ORM
* **Web3.py** – Blockchain interaction
* **Polygon Amoy Testnet** – Smart contract deployment
* **ReportLab** – PDF generation
* **QR Code** – Hash verification
* **SessionMiddleware** – Authentication handling

---

## 📁 Project Structure

```
backend_verifikasi/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── auth.py
│   ├── certificate_service.py
│   ├── blockchain.py
│   └── schemas.py
│
├── templates/
├── static/
├── certificates/
├── .env
├── requirements.txt
└── README.md
```

---

# 🚀 Installation Guide (Local Setup)

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/sertisah-backend.git
cd sertisah-backend
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

If requirements.txt does not exist:

```bash
pip install fastapi uvicorn sqlalchemy passlib web3 python-dotenv qrcode reportlab
```

---

## 4️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```
PRIVATE_KEY=your_polygon_private_key
WALLET_ADDRESS=your_wallet_address
CONTRACT_ADDRESS=your_deployed_contract_address
RPC_URL=https://rpc-amoy.polygon.technology
```

⚠️ Never share your private key publicly.

---

## 5️⃣ Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0
```

Backend will be available at:

```
http://127.0.0.1:8000
```

---

# 🔐 Default Admin Setup

After first run, create a superadmin manually using Python shell:

```bash
python
```

Then:

```python
from app.database import SessionLocal
from app.models import AdminUser
from app.auth import hash_password

db = SessionLocal()

admin = AdminUser(
    username="superadmin",
    password_hash=hash_password("admin123"),
    role="SUPERADMIN"
)

db.add(admin)
db.commit()
db.close()
```

Login at:

```
http://127.0.0.1:8000/login
```

---

# 📜 Smart Contract

The system uses a simple Solidity contract:

```solidity
contract CertificateStorage {

    mapping(string => bool) private certificates;

    event CertificateStored(string hash);

    function storeCertificate(string memory _hash) public {
        require(!certificates[_hash], "Certificate already exists");
        certificates[_hash] = true;
        emit CertificateStored(_hash);
    }

    function verifyCertificate(string memory _hash) public view returns (bool) {
        return certificates[_hash];
    }
}
```

Deployed on:

Polygon Amoy Testnet

---

# 🔎 Public API Endpoints

## Verify Certificate

**POST** `/verify`

Request:

```json
{
  "certificate_hash": "your_hash_here"
}
```

Response:

```json
{
  "valid": true,
  "message": "Certificate found",
  "data": {
    "certificate_id": "...",
    "name": "...",
    "nim": "...",
    "program_studi": "...",
    "institusi": "...",
    "issue_date": "...",
    "blockchain_verified": true,
    "transaction_hash": "...",
    "explorer_url": "..."
  },
  "blockchain_registered": true
}
```

---

# 🛡️ Security Features

* SHA-256 certificate hashing
* Blockchain immutability
* Session-based admin authentication
* Role-Based Access Control (RBAC)
* Audit log system (admin & public API tracking)
* Separation of public and protected endpoints

---

# 📊 Admin Features

* Generate certificate
* Delete certificate
* Search by NIM
* Pagination
* Blockchain transaction tracking
* Audit log viewer (SUPERADMIN only)

---

# 📱 Android Integration

The Android app communicates with:

```
POST /verify
```

Used for real-time QR Code scanning and blockchain validation.

---

# 🧾 Audit Logging

All sensitive actions are logged:

* Login
* Certificate generation
* Deletion
* Public verification API calls

Logs include:

* Admin ID (nullable for public requests)
* Action type
* Description
* IP Address
* Timestamp

---

# ⚙️ Development Notes

If database schema changes:

Delete database (development only):

```bash
rm sertisah.db
```

Then restart the server.

---

# 🧠 System Architecture

```
Admin → FastAPI → SQLite
                ↓
              Web3.py
                ↓
          Polygon Blockchain
                ↓
            Android App
```

---

# 📌 License

This project is developed for academic research purposes.

---

# 👨‍💻 Author

SertiSah – Academic Digital Certificate Verification System
Built with FastAPI, Blockchain, and Android Integration.

Ahnan Dev

---
