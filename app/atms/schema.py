from datetime import datetime
import uuid
from typing import List
from typing import Optional
from pydantic.main import BaseModel


class ATMCreateSchema(BaseModel):
    id: uuid.UUID

    address: str
    latitude: float
    longitude: float
    allDay: bool
    wheelchair: Optional[bool] = False
    blind: Optional[bool] = False
    nfcForBankCards: Optional[bool] = False
    qrRead: Optional[bool] = False
    supportsUsd: Optional[bool] = False
    supportsChargeRub: Optional[bool] = False
    supportsEur: Optional[bool] = False
    supportsRub: Optional[bool] = False


class AtmShow(ATMCreateSchema):
    class Config:
        orm_mode = True


class AtmShowWithDistance(AtmShow):
    distance_to_you: int
    pass


class Filters(BaseModel):
    offset: int
    limit: int
    allDay: bool | None
    wheelchair: bool | None
    blind: bool | None
    nfcForBankCards: bool | None
    qrRead: bool | None
    supportsUsd: bool | None
    supportsChargeRub: bool | None
    supportsEur: bool | None
    supportsRub: bool | None
