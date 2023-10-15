import uuid

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID

from app.core.db.base_class import Base


class Offices(Base):
    __tablename__ = "offices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    salePointName = Column(String)
    address = Column(String)
    status = Column(String)
    openHours = Column(JSON)
    rko = Column(String)
    openHoursIndividual = Column(JSON)
    officeType = Column(String)
    salePointFormat = Column(String)
    suoAvailability = Column(String)
    hasRamp = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    metroStation = Column(String)
    distance = Column(Integer)
    kep = Column(Boolean)
    myBranch = Column(Boolean)
    network = Column(String)
    credit_card = Column(Boolean)
    debit_card = Column(Boolean)
    consultation = Column(Boolean)
    issuing = Column(Boolean)
