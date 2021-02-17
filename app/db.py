"""Database functions"""

import os
from fastapi import APIRouter, Depends
import sqlalchemy
from dotenv import load_dotenv
import databases
import asyncio
from typing import Union, Iterable
from pypika import Query, Table

load_dotenv()
database_url = os.getenv("DATABASE_URL")
database = databases.Database(database_url)

router = APIRouter()



@router.get("/info")
async def get_url():
    """Verify we can connect to the database,
    and return the database URL in this format:

    dialect://user:password@host/dbname

    The password will be hidden with ***
    """

    url_without_password = repr(database.url)
    return {"database_url": url_without_password}



async def select(columns:Union[Iterable[str], str], city):
    data = Table('data')
    if type(columns) == str:
        q = Query.from_(data).select(columns)
    else:
        cols = [data[x] for x in columns]
        q = Query.from_(data).select(*cols)

    q = (q
            .where(data.City == city.city)
            .where(data.State == city.state)
        )

    value = await database.fetch_one(str(q))
    return value
