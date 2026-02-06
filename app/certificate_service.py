import hashlib
import os
from datetime import datetime
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

CERT_DIR = "certificates"

def generate_certificate(
    name: str,
    nim: str,
    program_studi: str,
    institusi: str
):
    # Pastikan folder ada
    os.makedirs(CERT_DIR, exist_ok=True)

    certificate_id = f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    filename = f"{certificate_id}.pdf"
    filepath = os.path.join(CERT_DIR, filename)

    # Data sertifikat (untuk hashing)
    certificate_data = f"{certificate_id}{name}{nim}{program_studi}{institusi}"

    # Hash SHA-256
    certificate_hash = hashlib.sha256(
        certificate_data.encode()
    ).hexdigest()

    # Generate QR Code dari hash
    qr_path = os.path.join(CERT_DIR, f"{certificate_id}.png")
    qr = qrcode.make(certificate_hash)
    qr.save(qr_path)

    # Generate PDF
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 80, "SERTIFIKAT AKADEMIK DIGITAL")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 150, f"Nama           : {name}")
    c.drawString(100, height - 180, f"NIM            : {nim}")
    c.drawString(100, height - 210, f"Program Studi  : {program_studi}")
    c.drawString(100, height - 240, f"Institusi      : {institusi}")
    c.drawString(100, height - 270, f"ID Sertifikat  : {certificate_id}")

    # QR Code di PDF
    c.drawImage(qr_path, width - 200, 100, width=120, height=120)

    c.showPage()
    c.save()

    return {
        "certificate_id": certificate_id,
        "certificate_hash": certificate_hash,
        "file_path": filepath
    }
