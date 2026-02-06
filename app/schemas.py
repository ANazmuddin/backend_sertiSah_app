from pydantic import BaseModel

class VerifyRequest(BaseModel):
    certificate_hash: str

class VerifyResponse(BaseModel):
    status: str
    message: str

class CertificateRequest(BaseModel):
    name: str
    nim: str
    program_studi: str
    institusi: str

class CertificateResponse(BaseModel):
    certificate_id: str
    certificate_hash: str
    file_path: str
