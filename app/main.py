import os
import json
from math import ceil

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.database import engine, SessionLocal
from app.models import Base, Certificate
from app.auth import login_required, authenticate_admin
from app.certificate_service import generate_certificate
from app.schemas import VerifyRequest, VerifyResponse
from app.blockchain import verify_certificate_on_chain


# ================= APP INIT =================

app = FastAPI(
    title="API Verifikasi Sertifikat",
    description="Backend untuk verifikasi sertifikat akademik digital",
    version="1.0.0"
)

app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key-skripsi"
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)


# ============================================================
# ================= ANDROID API (PUBLIC) =====================
# ============================================================

@app.post("/verify", response_model=VerifyResponse)
def verify_certificate(payload: VerifyRequest):

    db = SessionLocal()

    cert = db.query(Certificate).filter(
        Certificate.certificate_hash == payload.certificate_hash
    ).first()

    if not cert:
        db.close()
        return VerifyResponse(
            valid=False,
            message="Sertifikat tidak valid",
            data=None,
            blockchain_registered=False
        )

    blockchain_status = verify_certificate_on_chain(payload.certificate_hash)

    response = VerifyResponse(
        valid=True,
        message="Sertifikat ditemukan",
        data={
            "certificate_id": cert.certificate_id,
            "name": cert.name,
            "nim": cert.nim,
            "program_studi": cert.program_studi,
            "institusi": cert.institusi,
            "issue_date": cert.issue_date,
            "blockchain_verified": blockchain_status,
            "transaction_hash": cert.blockchain_tx,
            "explorer_url": f"https://amoy.polygonscan.com/tx/{cert.blockchain_tx}"
            if cert.blockchain_tx else None
        },
        blockchain_registered=blockchain_status
    )

    db.close()
    return response


# ============================================================
# ================= DOWNLOAD (PUBLIC) ========================
# ============================================================

@app.get("/download-certificate/{certificate_id}")
def download_certificate(certificate_id: str):

    file_path = f"certificates/{certificate_id}.pdf"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File tidak ditemukan")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{certificate_id}.pdf"
    )


# ============================================================
# ================= AUTH ========================
# ============================================================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):

    db = SessionLocal()
    user = authenticate_admin(username, password, db)
    db.close()

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Username atau password salah"}
        )

    request.session["admin_id"] = user.id
    return RedirectResponse("/dashboard", status_code=302)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


# ============================================================
# ================= DASHBOARD (PROTECTED) ====================
# ============================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    auth=Depends(login_required)
):
    if auth:
        return auth

    db = SessionLocal()

    total_certificates = db.query(Certificate).count()

    total_blockchain = (
        db.query(Certificate)
        .filter(Certificate.blockchain_tx.isnot(None))
        .count()
    )

    db.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": "Dashboard",
            "total_certificates": total_certificates,
            "total_blockchain": total_blockchain
        }
    )


# ============================================================
# ================= GENERATE (PROTECTED) =====================
# ============================================================

@app.get("/generate", response_class=HTMLResponse)
def generate_page(
    request: Request,
    auth=Depends(login_required)
):
    if auth:
        return auth

    return templates.TemplateResponse(
        "generate.html",
        {"request": request, "title": "Generate Sertifikat"}
    )


@app.post("/generate", response_class=HTMLResponse)
def generate_submit(
    request: Request,
    name: str = Form(...),
    nim: str = Form(...),
    program_studi: str = Form(...),
    institusi: str = Form(...),
    auth=Depends(login_required)
):
    if auth:
        return auth

    certificate = generate_certificate(name, nim, program_studi, institusi)

    return templates.TemplateResponse(
        "generate.html",
        {
            "request": request,
            "title": "Generate Sertifikat",
            "certificate": certificate
        }
    )


# ============================================================
# ================= LIST CERTIFICATE =========================
# ============================================================

@app.get("/certificates", response_class=HTMLResponse)
def list_certificates(
    request: Request,
    page: int = 1,
    nim: str = "",
    auth=Depends(login_required)
):
    if auth:
        return auth

    db = SessionLocal()

    query = db.query(Certificate)

    if nim:
        query = query.filter(Certificate.nim.ilike(f"%{nim}%"))

    total = query.count()

    per_page = 5
    total_pages = ceil(total / per_page) if total > 0 else 1

    # Validasi page
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    certificates = (
        query
        .order_by(Certificate.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    db.close()

    return templates.TemplateResponse(
        "certificates.html",
        {
            "request": request,
            "title": "Daftar Sertifikat",
            "certificates": certificates,
            "page": page,
            "total_pages": total_pages,
            "search_nim": nim,
            "total_data": total
        }
    )


@app.post("/delete-certificate/{certificate_id}")
def delete_certificate(
    request: Request,
    certificate_id: str,
    auth=Depends(login_required)
):
    if auth:
        return auth

    meta_file = "certificates/certificates.json"

    if not os.path.exists(meta_file):
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")

    with open(meta_file, "r") as f:
        certs = json.load(f)

    cert_to_delete = next(
        (c for c in certs if c["certificate_id"] == certificate_id),
        None
    )

    if not cert_to_delete:
        raise HTTPException(status_code=404, detail="Sertifikat tidak ditemukan")

    pdf_path = f"certificates/{certificate_id}.pdf"
    qr_path = f"certificates/{certificate_id}_qr.png"

    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    if os.path.exists(qr_path):
        os.remove(qr_path)

    certs.remove(cert_to_delete)

    with open(meta_file, "w") as f:
        json.dump(certs, f, indent=4)

    return RedirectResponse("/certificates", status_code=302)