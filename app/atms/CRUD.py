from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.CRUD import ModelAccessor, CreateSchemaType, ModelType
from app.atms.model import ATM
from app.atms.schema import ATMCreateSchema


class AtmAccessor(ModelAccessor[ATM, ATMCreateSchema, ATMCreateSchema]):
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


    async def get_by_filters(self, db: AsyncSession, conditions, offset, limit):
        query = select(ATM).where(and_(*conditions)).offset(offset).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


atm = AtmAccessor(ATM)
