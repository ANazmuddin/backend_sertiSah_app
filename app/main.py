from fastapi import FastAPI
from app.schemas import VerifyRequest, VerifyResponse
from app.services import verify_certificate
from app.certificate_service import generate_certificate
from app.schemas import CertificateRequest, CertificateResponse
from fastapi.responses import FileResponse
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app.auth import ADMIN_USERNAME, ADMIN_PASSWORD, require_login

import os

from fastapi.staticfiles import StaticFiles


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

@app.post("/verify", response_model=VerifyResponse)
def verify(data: VerifyRequest):
    result = verify_certificate(data.certificate_hash)
    return result

@app.post("/generate-certificate", response_model=CertificateResponse)
def create_certificate(data: CertificateRequest):
    return generate_certificate(
        data.name,
        data.nim,
        data.program_studi,
        data.institusi
    )

@app.get("/download-certificate/{certificate_id}")
def download_certificate(certificate_id: str):
    file_path = f"certificates/{certificate_id}.pdf"

    if not os.path.exists(file_path):
        return {
            "status": "ERROR",
            "message": "File sertifikat tidak ditemukan"
        }

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{certificate_id}.pdf"
    )

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request}
    )

@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["admin_logged_in"] = True
        return RedirectResponse("/dashboard", status_code=302)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Username atau password salah"}
    )

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    auth = require_login(request)
    if auth:
        return auth

    return templates.TemplateResponse(
        "dashboard.html", {"request": request}
    )

@app.post("/dashboard", response_class=HTMLResponse)
def generate_from_dashboard(
    request: Request,
    name: str = Form(...),
    nim: str = Form(...),
    program_studi: str = Form(...),
    institusi: str = Form(...)
):
    auth = require_login(request)
    if auth:
        return auth

    from app.certificate_service import generate_certificate

    certificate = generate_certificate(
        name, nim, program_studi, institusi
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "certificate": certificate
        }
    )
