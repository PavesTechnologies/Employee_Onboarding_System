from typing import Optional, Dict, Any
from .redis_client import get_redis_client
import json
import logging

logger = logging.getLogger(__name__)

ACCESS_POINT_CACHE_PREFIX = "employee_details"


def make_cache_key(form_name: str, user_uuid: str) -> str:
    """Generate Redis key for form data"""
    return f"{ACCESS_POINT_CACHE_PREFIX}:{form_name}:{user_uuid}"


def get_cache(form_name: str, user_uuid: str) -> Optional[Dict[str, Any]]:
    """Get cached data if exists, else return None."""
    try:
        client = get_redis_client()
        key = make_cache_key(form_name, user_uuid)
        value = client.get(key)
        return json.loads(value) if value else None
    except Exception as e:
        logger.error(f"Cache get error for {form_name}:{user_uuid} - {e}")
        return None


def cache_exists(form_name: str, user_uuid: str) -> bool:
    """Check if cache key exists without fetching data"""
    try:
        client = get_redis_client()
        key = make_cache_key(form_name, user_uuid)
        return client.exists(key) > 0
    except Exception as e:
        logger.error(f"Cache exists check error - {e}")
        return False


def create_cache(form_name: str, user_uuid: str, data: dict, ttl: int = 3600) -> bool:
    """Create or update cache. Returns True if successful."""
    try:
        client = get_redis_client()
        key = make_cache_key(form_name, user_uuid)
        client.set(key, json.dumps(data), ex=ttl)
        return True
    except Exception as e:
        logger.error(f"Cache set error for {form_name}:{user_uuid} - {e}")
        return False


def delete_cache(form_name: str, user_uuid: str) -> bool:
    """Delete cached data. Returns True if deleted."""
    try:
        client = get_redis_client()
        key = make_cache_key(form_name, user_uuid)
        return client.delete(key) > 0
    except Exception as e:
        logger.error(f"Cache delete error - {e}")
        return False


def get_user_all_forms(user_uuid: str) -> Dict[str, Any]:
    """Get all cached forms for a specific user"""
    try:
        client = get_redis_client()
        pattern = f"{ACCESS_POINT_CACHE_PREFIX}:*:{user_uuid}"
        keys = client.keys(pattern)

        result = {}
        for key in keys:
            # Extract form_name from key
            form_name = key.decode("utf-8").split(":")[1]
            value = client.get(key)
            if value:
                result[form_name] = json.loads(value)
        return result
    except Exception as e:
        logger.error(f"Get all forms error for {user_uuid} - {e}")
        return {}


def clear_all_employee_cache():
    """Clear all employee detail caches"""
    try:
        r = get_redis_client()
        if r is None:
            return
        keys = r.keys(f"{ACCESS_POINT_CACHE_PREFIX}:*")
        if keys:
            r.delete(*keys)
            logger.info(f"🗑️ Cleared {len(keys)} cache entries")
    except Exception as e:
        logger.error(f"Clear all cache error - {e}")
