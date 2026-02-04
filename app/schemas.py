from pydantic import BaseModel

class VerifyRequest(BaseModel):
    certificate_hash: str

class VerifyResponse(BaseModel):
    status: str
    message: str
