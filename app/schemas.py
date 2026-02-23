from pydantic import BaseModel
from typing import Optional, Dict, Any

class VerifyRequest(BaseModel):
    certificate_hash: str


class CertificateData(BaseModel):
    certificate_id: str
    name: str
    nim: str
    program_studi: str
    institusi: str
    issue_date: str


class VerifyResponse(BaseModel):
    valid: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    blockchain_registered: bool = False
