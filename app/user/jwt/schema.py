import uuid
from datetime import timedelta
from typing import Any

from pydantic.main import BaseModel


class JwtCreate(BaseModel):
    subject: str
    jti: str
    device_id: str
    # expired_time: timedelta
