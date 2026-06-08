import jwt
import time
import requests
from pathlib import Path
from fastapi import HTTPException
from ...config.env_loader import get_env_var

INTEGRATION_KEY = get_env_var("INTEGRATION_KEY")
USER_ID = get_env_var("USER_ID")
AUTH_SERVER = get_env_var("AUTH_SERVER")

current_dir = str(Path.cwd())
target_dir = current_dir + "/Backend/API_Layer/utils/private.key"
PRIVATE_KEY_PATH = Path(target_dir)


def generate_docusign_access_token():
    print(PRIVATE_KEY_PATH)
    private_key = PRIVATE_KEY_PATH.read_bytes()

    now = int(time.time())

    payload = {
        "iss": INTEGRATION_KEY,
        "sub": USER_ID,
        "aud": AUTH_SERVER,
        "iat": now,
        "exp": now + 3600,
        "scope": "signature impersonation",
    }

    assertion = jwt.encode(payload, private_key, algorithm="RS256")

    response = requests.post(
        f"https://{AUTH_SERVER}/oauth/token",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        },
        timeout=10,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to obtain DocuSign access token",
        )

    response.raise_for_status()
    return response.json()
