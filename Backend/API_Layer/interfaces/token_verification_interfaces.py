from pydantic import BaseModel


class TokenVerificationRequest(BaseModel):
    raw_token: str


class TokenVerificationResponse(BaseModel):
    is_valid: bool
    message: str
