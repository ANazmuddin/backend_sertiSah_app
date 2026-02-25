import os
import json
import uuid
import hashlib
from datetime import datetime

import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from app.blockchain import store_certificate_on_chain


# ===============================
# CONFIG
# ===============================

CERT_DIR = "certificates"
META_FILE = os.path.join(CERT_DIR, "certificates.json")

if not os.path.exists(CERT_DIR):
    os.makedirs(CERT_DIR)


# ===============================
# MAIN FUNCTION
# ===============================

def generate_certificate(name, nim, program_studi, institusi):

    certificate_id = str(uuid.uuid4())
    issue_date = datetime.now().strftime("%d %B %Y")

    # ===============================
    # 🔐 HASH UNTUK VERIFIKASI
    # ===============================
    raw_data = f"{name}{nim}{program_studi}{institusi}{certificate_id}"
    certificate_hash = hashlib.sha256(raw_data.encode()).hexdigest()

    print("HASH YANG DIGENERATE:", certificate_hash)

    # ===============================
    # 🔗 SIMPAN KE BLOCKCHAIN
    # ===============================
    tx_hash = None
    try:
        tx_hash = store_certificate_on_chain(certificate_hash)
        print("BLOCKCHAIN TX HASH:", tx_hash)
    except Exception as e:
        print("ERROR BLOCKCHAIN:", e)

    # ===============================
    # 📁 FILE PATH
    # ===============================
    pdf_path = os.path.join(CERT_DIR, f"{certificate_id}.pdf")
    qr_path = os.path.join(CERT_DIR, f"{certificate_id}_qr.png")

    # ===============================
    # 📷 GENERATE QR
    # ===============================
    qr = qrcode.make(certificate_hash)
    qr.save(qr_path)

    # ===============================
    # 📄 GENERATE PDF
    # ===============================
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Border
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(4)
    c.rect(30, 30, width - 60, height - 60)

    # Logo (optional)
    logo_path = "static/UCA.png"
    if os.path.exists(logo_path):
        c.drawImage(
            logo_path,
            width/2 - 50,
            height - 150,
            width=100,
            height=100,
            preserveAspectRatio=True
        )

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 180, "SERTIFIKAT AKADEMIK")

    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 210, "Diberikan kepada:")

    # Name
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 250, name.upper())

    # Details
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 280, f"NIM: {nim}")
    c.drawCentredString(width/2, height - 300, f"Program Studi: {program_studi}")
    c.drawCentredString(width/2, height - 320, f"Institusi: {institusi}")

    # Certificate ID
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, height - 350, f"Nomor Sertifikat: {certificate_id}")

    # Issue Date
    c.drawString(60, 100, f"Tanggal Terbit: {issue_date}")

    # Signature line
    c.line(width - 200, 120, width - 60, 120)
    c.drawString(width - 190, 100, "Kepala Program Studi")

    # QR Code
    c.drawImage(qr_path, width - 150, 200, width=100, height=100)

    c.save()

    # ===============================
    # 💾 SIMPAN METADATA JSON
    # ===============================
    certificate_data = {
        "certificate_id": certificate_id,
        "name": name,
        "nim": nim,
        "program_studi": program_studi,
        "institusi": institusi,
        "issue_date": issue_date,
        "certificate_hash": certificate_hash,
        "blockchain_tx": tx_hash
    }

    certs = []

    if os.path.exists(META_FILE):
        try:
            with open(META_FILE, "r") as f:
                certs = json.load(f)
                if not isinstance(certs, list):
                    certs = []
        except Exception:
            certs = []

    certs.append(certificate_data)

    with open(META_FILE, "w") as f:
        json.dump(certs, f, indent=4)

    return certificate_data