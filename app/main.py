import os
import json

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.database import engine, SessionLocal
from app.models import Base
from app.auth import login_required, authenticate_admin
from app.certificate_service import generate_certificate
from app.schemas import VerifyRequest, VerifyResponse

# ================= APP INIT =================

app = FastAPI(
    title="API Verifikasi Sertifikat",
    description="Backend untuk verifikasi sertifikat akademik digital",
    version="1.0.0"
)

# ================= MIDDLEWARE =================

app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key-skripsi"
)

# ================= STATIC & TEMPLATE =================

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ================= DATABASE =================

Base.metadata.create_all(bind=engine)

# ============================================================
# ================= ANDROID API (PUBLIC) =====================
# ============================================================

@app.post("/verify", response_model=VerifyResponse)
def verify_certificate(payload: VerifyRequest):
    meta_file = "certificates/certificates.json"

    if not os.path.exists(meta_file):
        return VerifyResponse(
            valid=False,
            message="Data sertifikat tidak ditemukan"
        )

    with open(meta_file, "r") as f:
        certs = json.load(f)

    for cert in certs:
        if cert["certificate_hash"] == payload.certificate_hash:
            return VerifyResponse(
                valid=True,
                message="Sertifikat valid dan terdaftar",
                data={
                    "certificate_id": cert["certificate_id"],
                    "name": cert["name"],
                    "nim": cert["nim"],
                    "program_studi": cert["program_studi"],
                    "institusi": cert["institusi"],
                    "issue_date": cert["issue_date"],
                }
            )

    return VerifyResponse(
        valid=False,
        message="Sertifikat tidak valid"
    )

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
    auth = Depends(login_required)
):
    if auth:
        return auth

    meta_file = "certificates/certificates.json"
    certs = []

    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r") as f:
                certs = json.load(f)
        except:
            certs = []

    total_certificates = len(certs)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": "Dashboard",
            "total_certificates": total_certificates
        }
    )


# ============================================================
# ================= GENERATE (PROTECTED) =====================
# ============================================================

@app.get("/generate", response_class=HTMLResponse)
def generate_page(
    request: Request,
    auth = Depends(login_required)
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
    auth = Depends(login_required)
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
# ================= LIST CERTIFICATE (PROTECTED) =============
# ============================================================

from math import ceil

@app.get("/certificates", response_class=HTMLResponse)
def list_certificates(
    request: Request,
    page: int = 1,
    nim: str = "",
    auth = Depends(login_required)
):
    if auth:
        return auth

    meta_file = "certificates/certificates.json"
    certs = []

    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r") as f:
                certs = json.load(f)
                if not isinstance(certs, list):
                    certs = []
        except Exception:
            certs = []

    # 🔎 FILTER BERDASARKAN NIM
    if nim:
        certs = [c for c in certs if nim.lower() in c["nim"].lower()]

    # 📄 PAGINATION
    per_page = 5
    total = len(certs)
    total_pages = ceil(total / per_page) if total > 0 else 1

    start = (page - 1) * per_page
    end = start + per_page
    paginated_certs = certs[start:end]

    return templates.TemplateResponse(
        "certificates.html",
        {
            "request": request,
            "title": "Daftar Sertifikat",
            "certificates": paginated_certs,
            "page": page,
            "total_pages": total_pages,
            "search_nim": nim
        }
    )


@app.post("/delete-certificate/{certificate_id}")
def delete_certificate(
    request: Request,
    certificate_id: str,
    auth = Depends(login_required)
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
