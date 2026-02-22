import os
import json
import uuid
import hashlib
from datetime import datetime

import qrcode
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Frame
from reportlab.pdfgen import canvas


CERT_DIR = "certificates"
META_FILE = os.path.join(CERT_DIR, "certificates.json")

if not os.path.exists(CERT_DIR):
    os.makedirs(CERT_DIR)

def generate_certificate(name, nim, program_studi, institusi):

    certificate_id = str(uuid.uuid4())
    issue_date = datetime.now().strftime("%d %B %Y")

    # 🔐 Hash untuk verifikasi
    raw_data = f"{name}{nim}{program_studi}{institusi}{certificate_id}"
    certificate_hash = hashlib.sha256(raw_data.encode()).hexdigest()

    pdf_path = os.path.join(CERT_DIR, f"{certificate_id}.pdf")

    # =============================
    # Generate QR Code
    # =============================
    qr = qrcode.make(certificate_hash)
    qr_path = os.path.join(CERT_DIR, f"{certificate_id}_qr.png")
    qr.save(qr_path)

    # =============================
    # Generate PDF
    # =============================
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Border
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(4)
    c.rect(30, 30, width - 60, height - 60)

    # Logo
    logo_path = "static/UCA.png"
    if os.path.exists(logo_path):
        c.drawImage(logo_path, width/2 - 50, height - 150, width=100, height=100, preserveAspectRatio=True)

    # Judul
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 180, "SERTIFIKAT AKADEMIK")

    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 210, "Diberikan kepada:")

    # Nama Mahasiswa
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 250, name.upper())

    # Detail mahasiswa
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 280, f"NIM: {nim}")
    c.drawCentredString(width/2, height - 300, f"Program Studi: {program_studi}")
    c.drawCentredString(width/2, height - 320, f"Institusi: {institusi}")

    # Nomor Sertifikat
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, height - 350, f"Nomor Sertifikat: {certificate_id}")

    # Tanggal
    c.drawString(60, 100, f"Tanggal Terbit: {issue_date}")

    # Tanda tangan
    c.line(width - 200, 120, width - 60, 120)
    c.drawString(width - 190, 100, "Kepala Program Studi")

    # QR Code
    c.drawImage(qr_path, width - 150, 200, width=100, height=100)

    c.save()

    # =============================
    # Simpan metadata JSON
    # =============================
    certificate_data = {
        "certificate_id": certificate_id,
        "name": name,
        "nim": nim,
        "program_studi": program_studi,
        "institusi": institusi,
        "issue_date": issue_date,
        "certificate_hash": certificate_hash
    }

    certs = []
    if os.path.exists(META_FILE):
        with open(META_FILE, "r") as f:
            certs = json.load(f)

    certs.append(certificate_data)

    with open(META_FILE, "w") as f:
        json.dump(certs, f, indent=4)

    return certificate_data
