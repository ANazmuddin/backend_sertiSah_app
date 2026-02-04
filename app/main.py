from fastapi import FastAPI
from app.schemas import VerifyRequest, VerifyResponse
from app.services import verify_certificate

app = FastAPI(
    title="API Verifikasi Sertifikat",
    description="Backend untuk verifikasi sertifikat akademik digital",
    version="1.0.0"
)

@app.post("/verify", response_model=VerifyResponse)
def verify(data: VerifyRequest):
    result = verify_certificate(data.certificate_hash)
    return result
