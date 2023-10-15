import asyncio

from sqlalchemy import text
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


class AtmDoesntExist(Exception):
    pass


async def get_atm(id, db: AsyncSession = Depends(get_db)) -> AtmShow:
    atm = await store.atm.get(db, id)
    if not atm:
        raise AtmDoesntExist
    return atm


async def get_multi_atm(skip, limit, db: AsyncSession = Depends(get_db)) -> List[AtmShow]:
    atms = await store.atm.get_multi(skip=skip, limit=limit, db=db)
    if not atms:
        raise AtmDoesntExist
    return atms.all()


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
        atms = await store.atm.get_by_filters(db=db, conditions=conditions, offset=filters.offset,
                                              limit=filters.limit)
    else:
        atms = await store.atm.get_multi(skip=filters.offset, limit=filters.limit, db=db)
        atms = atms.all()
    return atms


async def calculate_distance_and_order(coords, db: AsyncSession):
    sql_query = text(f"""
        SELECT
    *,
    point{tuple(coords)} <@> point(longitude, latitude) AS distance_to_you
FROM
    atms
ORDER BY
    distance_to_you
LIMIT 15;

    """)
    result = await db.execute(sql_query)

    return result.mappings().all()
