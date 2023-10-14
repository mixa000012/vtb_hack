import asyncio
import random
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.deps import get_db
from app.core import store
from app.user.model import User
import json
from app.salepoint.schema import SalepointShow, Filters
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db
import asyncio
from app.salepoint.model import Offices

engine_test = create_async_engine(
    settings.PG_DATABASE_URI,
    pool_size=settings.PG_POOL_MAX_SIZE,
    pool_recycle=settings.PG_POOL_RECYCLE,
    max_overflow=settings.PG_MAX_OVERFLOW,
    pool_pre_ping=True,
)
async_session_maker = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test, class_=AsyncSession, expire_on_commit=False,
)


async def load_data_from_json_file(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for entry in data:
            entry['debit_card'] = bool(random.getrandbits(1))
            entry['credit_card'] = bool(random.getrandbits(1))
            entry['consultation'] = bool(random.getrandbits(1))
            entry['issuing'] = bool(random.getrandbits(1))
            async with async_session_maker() as session:
                db_obj = Offices(**entry)  # type: ignore
                session.add(db_obj)
                await session.commit()
                await session.refresh(db_obj)


if __name__ == "__main__":
    # Run the asyncio event loop to execute the main function
    asyncio.run(load_data_from_json_file('offices.txt'))


async def get_sale_point(id, db: AsyncSession = Depends(get_db)) -> SalepointShow:
    return await store.sale_point.get(db, id)


async def get_multi_sale_point(skip, limit, db: AsyncSession = Depends(get_db)) -> List[SalepointShow]:
    res = await store.sale_point.get_multi(skip=skip, limit=limit, db=db)
    return res.all()


async def get_by_filters(filters: Filters, db: AsyncSession = Depends(get_db)) -> list[SalepointShow]:
    conditions = []
    if filters.credit_card:
        conditions.append(Offices.credit_card == True)
    if filters.debit_card:
        conditions.append(Offices.debit_card == True)
    if conditions:
        offices = await store.sale_point.get_by_filters(db=db, conditions=conditions, offset=filters.offset,
                                                        limit=filters.limit)
    else:
        offices = await store.sale_point.get_multi(skip=filters.offset, limit=filters.limit)
        offices = offices.all()
    return offices
