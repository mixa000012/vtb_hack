import uuid

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID

from app.core.db.base_class import Base


class ATM(Base):
    __tablename__ = "atms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    allDay = Column(Boolean)
    wheelchair = Column(Boolean)
    blind = Column(Boolean)
    nfcForBankCards = Column(Boolean)
    qrRead = Column(Boolean)
    supportsUsd = Column(Boolean)
    supportsChargeRub = Column(Boolean)
    supportsEur = Column(Boolean)
    supportsRub = Column(Boolean)
