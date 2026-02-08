import os
import json

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.database import engine, SessionLocal
from app.models import Base
from app.auth import require_login, authenticate_admin
from app.certificate_service import generate_certificate
from app.schemas import VerifyRequest, VerifyResponse


app = FastAPI(
    title="API Verifikasi Sertifikat",
    description="Backend untuk verifikasi sertifikat akademik digital",
    version="1.0.0"
)

# ================== MIDDLEWARE ==================
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key-skripsi"
)

# ================== STATIC & TEMPLATE ==================
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ================== DATABASE ==================
Base.metadata.create_all(bind=engine)

# ================== API ANDROID ==================
@app.post("/verify", response_model=VerifyResponse)
def verify_certificate(payload: VerifyRequest):
    meta_file = "certificates/certificates.json"

    if not os.path.exists(meta_file):
        return VerifyResponse(
            valid=False,
            message="Data sertifikat tidak ditemukan"
        )

    try:
        with open(meta_file, "r") as f:
            certs = json.load(f)
    except Exception:
        certs = []

    for cert in certs:
        if cert["certificate_hash"] == payload.certificate_hash:
            return VerifyResponse(
                valid=True,
                message="Sertifikat valid dan terdaftar"
            )

    return VerifyResponse(
        valid=False,
        message="Sertifikat tidak valid"
    )

# ================== DOWNLOAD PDF ==================
@app.get("/download-certificate/{certificate_id}")
def download_certificate(certificate_id: str):
    file_path = f"certificates/{certificate_id}.pdf"

    if not os.path.exists(file_path):
        return {"status": "ERROR", "message": "File sertifikat tidak ditemukan"}

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{certificate_id}.pdf"
    )

# ================== AUTH ==================
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

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

# ================== DASHBOARD ==================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    auth = require_login(request)
    if auth:
        return auth

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

# ================== GENERATE SERTIFIKAT ==================
@app.get("/generate", response_class=HTMLResponse)
def generate_page(request: Request):
    auth = require_login(request)
    if auth:
        return auth

    return templates.TemplateResponse(
        "generate.html",
        {"request": request}
    )

@app.post("/generate", response_class=HTMLResponse)
def generate_submit(
    request: Request,
    name: str = Form(...),
    nim: str = Form(...),
    program_studi: str = Form(...),
    institusi: str = Form(...)
):
    auth = require_login(request)
    if auth:
        return auth

    certificate = generate_certificate(
        name, nim, program_studi, institusi
    )

    return templates.TemplateResponse(
        "generate.html",
        {
            "request": request,
            "certificate": certificate
        }
    )

# ================== DAFTAR SERTIFIKAT ==================
@app.get("/certificates", response_class=HTMLResponse)
def list_certificates(request: Request):
    auth = require_login(request)
    if auth:
        return auth

    certs = []
    meta_file = "certificates/certificates.json"

    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r") as f:
                certs = json.load(f)
                if not isinstance(certs, list):
                    certs = []
        except Exception:
            certs = []

    return templates.TemplateResponse(
        "certificates.html",
        {
            "request": request,
            "certificates": certs
        }
    )
