"""Machine learning functions"""
import requests
from bs4 import BeautifulSoup as bs
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.state_abbr import us_state_abbrev as abbr
from pathlib import Path
import pandas as pd
from pypika import Query, Table
import asyncio
from app.db import get_db

conn = get_db()


router = APIRouter()


class City(BaseModel):
    city: str
    state: str


class CityData(BaseModel):
    city: City
    latitude: float
    longitude: float
    rental_price: float
    crime: str
    pollution: str
    walkability: float
    livability: float


def validate_city(
    city: City,
) -> City:
    city.city = city.city.title()

    try:
        if len(city.state) > 2:
            city.state = city.state.title()
            city.state = abbr[city.state]
        else:
            city.state = city.state.upper()
    except KeyError:
        raise HTTPException(status_code=422, detail=f"Unknown state: '{city.state}'")

    return city


@router.post("/api/get_data", response_model=CityData)
async def get_data(city: City, conn=Depends(get_db)):
    city = validate_city(city)

    tasks = await asyncio.gather(
        get_coordinates(city),
        get_crime(city),
        get_walkability(city),
        get_pollution(city),
        get_rental_price(city, await get_db()),
        get_livability(city),
    )

    data = {"city": city}

    for t in tasks:
        data.update(t)

    return data


@router.post("/api/coordinates")
async def get_coordinates(city: City):
    return {"latitude": 37.7749, "longitude": -122.4194}


async def get_crime(city: City):
    return {"crime": "High"}


@router.post("/api/crime")
async def get_crime(city: City):
    return {"crime": "High"}


@router.post("/api/rental_price")
async def get_rental_price(city: City, conn=Depends(get_db)):
    city = validate_city(city)
    rental_data = Table("rental_data")
    q = (
        Query.from_(rental_data)
        .select(rental_data.Rent)
        .where(rental_data.City == city.city)
        .where(rental_data.State == city.state)
    )
    with conn as c:
        rent = conn.execute(str(q)).fetchone()[0]
    print(rent)

    return {"rental_price": rent}


@router.post("/api/pollution")
async def get_pollution(city: City):
    return {"pollution": "Good"}


@router.post("/api/walkability")
async def get_walkability(city: City):
    city = validate_city(city)
    try:
        score = (await get_walkscore(**city.dict()))[0]
    except IndexError:
        raise HTTPException(
            status_code=422, detail=f"Walkscore not found for {city.city}, {city.state}"
        )

    return {"walkability": score}


async def get_walkscore(city: str, state: str):
    """Input: City, 2 letter abbreviation for state
    Returns a list containing WalkScore, BusScore, and BikeScore in that order"""

    r = requests.get(f"https://www.walkscore.com/{state}/{city}")
    images = bs(r.text, features="lxml").select(".block-header-badge img")
    print(images)
    return [int(str(x)[10:12]) for x in images]


@router.post("/api/livability")
async def get_livability(city: City):
    return {"livability": 47.0}
