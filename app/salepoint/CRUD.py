from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.CRUD import CreateSchemaType
from app.core.db.CRUD import ModelAccessor
from app.core.db.CRUD import ModelType
from app.salepoint.model import Offices
from app.salepoint.schema import SalePointCreate


class SalePointAccessor(ModelAccessor[Offices, SalePointCreate, SalePointCreate]):
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_filters(self, db: AsyncSession, conditions, offset, limit):
        query = select(Offices).where(and_(*conditions)).offset(offset).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


sale_point = SalePointAccessor(Offices)
