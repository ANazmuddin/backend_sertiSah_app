from fastapi import Request
from fastapi.responses import RedirectResponse

# Dummy akun admin (cukup untuk skripsi)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def is_authenticated(request: Request):
    return request.session.get("admin_logged_in", False)

def require_login(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
