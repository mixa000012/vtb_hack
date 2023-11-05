import uuid

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID


from app.core.db.base_class import Base


class IssuedJWTToken(Base):
    __tablename__ = "issued_jwt_token"
    jti = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    device_id = Column(String(36))
    revoked = Column(Boolean, default=False)

    def __str__(self) -> str:
        return f'{self.subject}: {self.jti}'
