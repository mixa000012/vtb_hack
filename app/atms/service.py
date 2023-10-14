import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.deps import get_db
from app.core import store
from app.user.model import User
import json
from uuid import uuid4

from typing import AsyncGenerator, List
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.atms.schema import ATMCreateSchema, AtmShow, Filters
from app.core.deps import get_db
import asyncio
from app.atms.model import ATM

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


async def load_data_from_json_file(json_file_path, db: AsyncSession = Depends(get_db)):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file).get('atms')
        for json_data in data:
            obi_in = ATMCreateSchema(
                address=json_data.get('address', ''),
                latitude=json_data.get('latitude', 0.0),
                longitude=json_data.get('longitude', 0.0),
                allDay=json_data.get('allDay', False),
                wheelchair=json_data['services'].get('wheelchair', {}).get('serviceActivity', 'UNKNOWN') == 'AVAILABLE',
                blind=json_data['services'].get('blind', {}).get('serviceActivity', 'UNKNOWN') == 'AVAILABLE',
                nfcForBankCards=json_data['services'].get('nfcForBankCards', {}).get('serviceActivity',
                                                                                     'UNAVAILABLE') == 'AVAILABLE',
                qrRead=json_data['services'].get('qrRead', {}).get('serviceActivity', 'UNAVAILABLE') == 'AVAILABLE',
                supportsUsd=json_data['services'].get('supportsUsd', {}).get('serviceActivity',
                                                                             'UNAVAILABLE') == 'AVAILABLE',
                supportsChargeRub=json_data['services'].get('supportsChargeRub', {}).get('serviceActivity',
                                                                                         'UNAVAILABLE') == 'AVAILABLE',
                supportsEur=json_data['services'].get('supportsEur', {}).get('serviceActivity',
                                                                             'UNAVAILABLE') == 'AVAILABLE',
                supportsRub=json_data['services'].get('supportsRub', {}).get('serviceActivity',
                                                                             'UNAVAILABLE') == 'AVAILABLE'
            )
            async with async_session_maker() as session:
                obi_in = obi_in.dict()
                db_obj = ATM(**obi_in)  # type: ignore
                session.add(db_obj)
                await session.commit()
                await session.refresh(db_obj)


if __name__ == "__main__":
    # Run the asyncio event loop to execute the main function
    asyncio.run(load_data_from_json_file('atms.txt'))


async def get_atm(id, db: AsyncSession = Depends(get_db)) -> AtmShow:
    return await store.atm.get(db, id)


async def get_multi_atm(skip, limit, db: AsyncSession = Depends(get_db)) -> List[AtmShow]:
    res = await store.atm.get_multi(skip=skip, limit=limit, db=db)
    return res.all()


async def get_by_filters(filters: Filters, db: AsyncSession = Depends(get_db)) -> list[AtmShow]:
    conditions = []
    if filters.allDay:
        conditions.append(ATM.allDay == True)
    if filters.wheelchair:
        conditions.append(ATM.wheelchair == True)
    if filters.blind:
        conditions.append(ATM.blind == True)
    if filters.nfcForBankCards:
        conditions.append(ATM.nfcForBankCards == True)
    if filters.qrRead:
        conditions.append(ATM.qrRead == True)
    if filters.supportsUsd:
        conditions.append(ATM.supportsUsd == True)
    if filters.supportsChargeRub:
        conditions.append(ATM.supportsChargeRub == True)
    if filters.supportsEur:
        conditions.append(ATM.supportsEur == True)
    if filters.supportsUsd:
        conditions.append(ATM.supportsUsd == True)
    if conditions:
        offices = await store.atm.get_by_filters(db=db, conditions=conditions, offset=filters.offset,
                                                 limit=filters.limit)
    else:
        offices = await store.atm.get_multi(skip=filters.offset, limit=filters.limit)
        offices = offices.all()
    return offices
