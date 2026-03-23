from pydantic import BaseModel
from typing import Optional

class HRVerificationRequest(BaseModel):
    user_uuid: str
    status: str   # VERIFIED or REJECTED

class VerifyDocumentRequest(BaseModel):
    user_uuid: Optional[str] = None
    document_uuid: Optional[str] = None
    doc_type: str   # personal / address / education / identity / experience / bank / pf
    status: str     # verified / rejected
    remarks: Optional[str] = None

    