from time import time
from urllib import response
import httpx
from fastapi import HTTPException
from ...config.env_loader import get_env_var


ADMIN_USERS_API = get_env_var("ADMIN_USERS_API")

_admin_cache = {"data": None, "expires": 0}
_admin_client: httpx.AsyncClient | None = None


async def get_admin_http_client():
    global _admin_client
    if _admin_client is None:
        _admin_client = httpx.AsyncClient(timeout=30.0)
    return _admin_client


import time
import httpx


def _full_name(first_name: str | None, middle_name: str | None, last_name: str | None) -> str:
    parts = [first_name, middle_name, last_name]
    return " ".join(p.strip() for p in parts if p and p.strip())


async def fetch_admin_users_reformed(token: str) -> list[dict]:
    if _admin_cache["data"] and time.time() < _admin_cache["expires"]:
        return _admin_cache["data"]

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            ADMIN_USERS_API,
            headers={"Authorization": token},
            params={"page": 1, "limit": 500}
        )

    data = response.json()
    users = data.get("users", [])

    result = [
        {
            "user_id": u["user_id"],
            "mail": u["mail"],
            "first_name": u.get("first_name"),
            "middle_name": u.get("middle_name"),
            "last_name": u.get("last_name"),
            "name": _full_name(
                u.get("first_name"),
                u.get("middle_name"),
                u.get("last_name")
            )
        }
        for u in users if u.get("is_active")
    ]

    _admin_cache["data"] = result
    _admin_cache["expires"] = time.time() + 300  # 5 min

    return result
