from fastapi import FastAPI
from app.schemas import VerifyRequest, VerifyResponse
from app.services import verify_certificate
from app.certificate_service import generate_certificate
from app.schemas import CertificateRequest, CertificateResponse


app = FastAPI(
    title="API Verifikasi Sertifikat",
    description="Backend untuk verifikasi sertifikat akademik digital",
    version="1.0.0"
)

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
