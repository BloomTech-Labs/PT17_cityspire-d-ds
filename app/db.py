"""Database functions"""

import os
from fastapi import APIRouter, Depends
import sqlalchemy
from dotenv import load_dotenv
import databases
import asyncio

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
