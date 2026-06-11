from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from Backend.Business_Layer.utils.redis_cache import (
    get_cache,
    create_cache,
    delete_cache,
    cache_exists,
)

router = APIRouter(prefix="/cache", tags=["Form Cache"])


@router.post("/{form_name}/{user_uuid}")
def upsert_form_cache(form_name: str, user_uuid: str, payload: Dict[str, Any]):
    """
    Create cache for a form.
    If cache already exists, delete and recreate.
    """
    try:
        if cache_exists(form_name, user_uuid):
            delete_cache(form_name, user_uuid)

        success = create_cache(form_name, user_uuid, payload)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create cache")

        return {
            "status": "success",
            "message": "Cache stored successfully",
            "form": form_name,
            "user_uuid": user_uuid,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{form_name}/{user_uuid}")
def get_form_cache(form_name: str, user_uuid: str):
    """
    Get cached form data for a user.
    """
    data = get_cache(form_name, user_uuid)
    if not data:
        raise HTTPException(status_code=404, detail="Cache not found")

    return {
        "status": "success",
        "form": form_name,
        "user_uuid": user_uuid,
        "data": data,
    }
