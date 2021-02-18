"""Database functions"""

import os
from fastapi import APIRouter, Depends
import sqlalchemy
from dotenv import load_dotenv
import databases
import asyncio
from typing import Union, Iterable
from pypika import Query, Table
from pypika.terms import Field

Field_ = Union[Field, str]

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



async def select(columns:Union[Iterable[Field_], Field_], city):
    data = Table('data')
    if type(columns) == str or type(columns)==Field:
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

async def select_all(city):
    data = Table('data')
    columns = (
        # 'lat', 'lon'
        data['lat'].as_('latitude'),
        data['lon'].as_('longitude'),
        data['Crime Rating'].as_('crime'),
        data['Rent'].as_('rental_price'),
        data['Air Quality Index'].as_('air_quality_index'),
        data['Population'].as_('population'),
        data['Nearest'].as_('nearest_string'),
        data['Good Days'].as_('good_days'),
        data["Crime Rate per 1000"].as_('crime_rate_ppt')
    )
    q = (Query.from_(data).select(*columns)
            .where(data.City == city.city)
            .where(data.State == city.state)
        )

    value = await database.fetch_one(str(q))
    return value
