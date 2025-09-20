from __future__ import annotations
import os
from fastapi import HTTPException
from typing import Optional

def require_api_key(x_api_key: Optional[str], env_var_name: str) -> None:
    """Raise 401 if env API key exists and header does not match."""
    expected = os.getenv(env_var_name)
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")