import asyncio
import json
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.atms.model import ATM
from app.atms.schema import ATMCreateSchema
from app.core import store
from app.core.config import settings
from app.salepoint.model import Offices

engine_test = create_async_engine(
    settings.PG_DATABASE_URI,
    pool_size=settings.PG_POOL_MAX_SIZE,
    pool_recycle=settings.PG_POOL_RECYCLE,
    max_overflow=settings.PG_MAX_OVERFLOW,
    pool_pre_ping=True,
)
async_session_maker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def load_data_from_json_file(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file).get("atms")
        async with async_session_maker() as session:
            results = await store.atm.get_multi(db=session, skip=0, limit=10)
        if results.all():
            return
        for json_data in data:
            obi_in = ATMCreateSchema(
                address=json_data.get("address", ""),
                latitude=json_data.get("latitude", 0.0),
                longitude=json_data.get("longitude", 0.0),
                allDay=json_data.get("allDay", False),
                wheelchair=json_data["services"]
                .get("wheelchair", {})
                .get("serviceActivity", "UNKNOWN")
                == "AVAILABLE",
                blind=json_data["services"]
                .get("blind", {})
                .get("serviceActivity", "UNKNOWN")
                == "AVAILABLE",
                nfcForBankCards=json_data["services"]
                .get("nfcForBankCards", {})
                .get("serviceActivity", "UNAVAILABLE")
                == "AVAILABLE",
                qrRead=json_data["services"]
                .get("qrRead", {})
                .get("serviceActivity", "UNAVAILABLE")
                == "AVAILABLE",
                supportsUsd=json_data["services"]
                .get("supportsUsd", {})
                .get("serviceActivity", "UNAVAILABLE")
                == "AVAILABLE",
                supportsChargeRub=json_data["services"]
                .get("supportsChargeRub", {})
                .get("serviceActivity", "UNAVAILABLE")
                == "AVAILABLE",
                supportsEur=json_data["services"]
                .get("supportsEur", {})
                .get("serviceActivity", "UNAVAILABLE")
                == "AVAILABLE",
                supportsRub=json_data["services"]
                .get("supportsRub", {})
                .get("serviceActivity", "UNAVAILABLE")
                == "AVAILABLE",
            )
            async with async_session_maker() as session:
                obi_in = obi_in.dict()
                db_obj = ATM(**obi_in)  # type: ignore
                session.add(db_obj)
                await session.commit()
                await session.refresh(db_obj)


async def load_data_from_json_file_offices(json_file_path):
    async with async_session_maker() as session:
        results = await store.sale_point.get_multi(db=session, skip=0, limit=10)
    if results.all():
        return
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        for entry in data:
            entry["debit_card"] = bool(random.getrandbits(1))
            entry["credit_card"] = bool(random.getrandbits(1))
            entry["consultation"] = bool(random.getrandbits(1))
            entry["issuing"] = bool(random.getrandbits(1))
            async with async_session_maker() as session:
                db_obj = Offices(**entry)  # type: ignore
                session.add(db_obj)
                await session.commit()
                await session.refresh(db_obj)


if __name__ == "__main__":

    async def run_load_data():
        # Run both functions concurrently
        await asyncio.gather(
            load_data_from_json_file_offices("offices.txt"),
            load_data_from_json_file("atms.txt"),
        )

    # Run the asyncio event loop to execute the main function
    asyncio.run(run_load_data())
