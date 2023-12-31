import asyncio
from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import store
from app.core.deps import get_db
from app.salepoint.model import Offices
from app.salepoint.schema import Filters
from app.salepoint.schema import SalepointShow


class OfficeDoesntExist(Exception):
    pass


from sqlalchemy import text


async def calculate_distance_and_order(coords, db: AsyncSession):
    sql_query = text(
        f"""
        SELECT
    *,
    point{tuple(coords)} <@> point(longitude, latitude) AS distance_to_you
FROM
    offices
ORDER BY
    distance_to_you
LIMIT 15;

    """
    )

    result = await db.execute(sql_query)
    return result.mappings().all()


# Usage example


if __name__ == "__main__":
    # Run the asyncio event loop to execute the main function
    asyncio.run(calculate_distance_and_order((37.537434, 55.749634)))


async def get_sale_point(id, db: AsyncSession = Depends(get_db)) -> SalepointShow:
    sale_point = await store.sale_point.get(db, id)
    if not sale_point:
        raise OfficeDoesntExist
    return sale_point


async def get_multi_sale_point(
    skip, limit, db: AsyncSession = Depends(get_db)
) -> List[SalepointShow]:
    res = await store.sale_point.get_multi(skip=skip, limit=limit, db=db)
    if not res:
        raise OfficeDoesntExist
    return res.all()


async def get_by_filters(
    filters: Filters, db: AsyncSession = Depends(get_db)
) -> list[SalepointShow]:
    conditions = []
    if filters.credit_card:
        conditions.append(Offices.credit_card == True)
    if filters.debit_card:
        conditions.append(Offices.debit_card == True)
    if filters.consultation:
        conditions.append(Offices.consultation == True)
    if filters.issuing:
        conditions.append(Offices.issuing == True)
    if conditions:
        offices = await store.sale_point.get_by_filters(
            db=db, conditions=conditions, offset=filters.offset, limit=filters.limit
        )
    else:
        offices = await store.sale_point.get_multi(
            skip=filters.offset, limit=filters.limit, db=db
        )
        offices = offices.all()
    if not offices:
        raise OfficeDoesntExist
    return offices
