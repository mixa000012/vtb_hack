from sqlalchemy import Column, ForeignKey, func
from sqlalchemy import DateTime
import uuid
from sqlalchemy import String, Boolean, Integer, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.db.base_class import Base


class ATM(Base):
    __tablename__ = 'atms'

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