from pydantic import BaseModel


class OfferRequestCreateResponse(BaseModel):
    user_uuid: str
    request_by: int
    action_taker_id: int


class OfferRequestUpdateResponse(BaseModel):
    user_uuid: str
    request_by: int
    action_taker_id: int


class OfferRequestDelete(BaseModel):
    user_uuid: str


class OfferRequestDetailsResponse(BaseModel):
    request_id: int
    user_uuid: str
    request_by: int
    action_taker_id: int
    status: str
    created_at: str
    updated_at: str


class OfferRequestListResponse(BaseModel):
    user_uuid: str
    action_taker_id: int


class OfferRequestUpdateResponse2(BaseModel):
    user_uuid: str
    action_taker_id: int


class OfferRequestResponse(BaseModel):
    user_uuid: str
    action_taker_id: int
    action_taker_name: str
    status: str
    comments: str
