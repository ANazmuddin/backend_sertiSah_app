from pydantic import BaseModel

class VerifyRequest(BaseModel):
    certificate_hash: str

class VerifyResponse(BaseModel):
    valid: bool
    message: str
