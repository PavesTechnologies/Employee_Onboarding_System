from pydantic import BaseModel


class OtpResponseStatus(BaseModel):
    status: str
    message: str


class OtpRequestBody(BaseModel):
    email: str
    otp: str
