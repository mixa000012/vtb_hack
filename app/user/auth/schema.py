from pydantic import BaseModel, Field
from app.user.auth.examples import refresh_token


class TokensOut(BaseModel):
    access_token: str = Field(examples=[refresh_token])
    refresh_token: str = Field(examples=[refresh_token])


class UpdateTokensIn(BaseModel):
    refresh_token: str = Field(examples=[refresh_token])
