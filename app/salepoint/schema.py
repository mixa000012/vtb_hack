from datetime import datetime
import uuid
from typing import List

from pydantic.main import BaseModel


class OpenHours(BaseModel):
    days: str | None
    hours: str | None


class SalePointCreate(BaseModel):
    salePointName: str
    address: str
    status: str
    openHours: List[OpenHours]
    rko: str | None
    openHoursIndividual: List[OpenHours]
    officeType: str
    salePointFormat: str
    suoAvailability: str | None
    hasRamp: str | None
    latitude: float
    longitude: float
    metroStation: str | None
    distance: int
    kep: bool | None
    myBranch: bool
    credit_card: bool
    debit_card: bool
    consultation: bool
    issuing: bool



class SalepointShow(SalePointCreate):
    class Config:
        orm_mode = True


class Filters(BaseModel):
    offset: int
    limit: int
    credit_card: bool | None
    debit_card: bool | None
    consultation: bool
    issuing: bool
