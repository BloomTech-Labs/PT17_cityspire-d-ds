"""Machine learning functions"""
import requests
from bs4 import BeautifulSoup as bs
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.state_abbr import us_state_abbrev as abbr
from pathlib import Path
import pandas as pd
from pypika import Query, Table
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


def validate_city(city: City, ) -> City:
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
async def get_data(city: City, conn = Depends(get_db)):
    city = validate_city(city)
    data = {
        "city": city,
        "latitude": 37.7749,
        "longitude": -122.4194,
        "rental_price": 2000,
        "pollution": "good",
        "crime": "High",
        "livability": 49.0,
    }

    walkscore = await get_walkability(city)
    rent_price = await get_rental_price(city, conn)
    data.update({
        **walkscore, 
        **rent_price,
        })

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
async def get_rental_price(city: City, conn = Depends(get_db)):
    city = validate_city(city)
    rental_data = Table('rental_data')
    q=(Query
        .from_(rental_data)
        .select(rental_data.Rent)
        .where(rental_data.City == city.city)
        .where(rental_data.State == city.state))

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
    """ Input: City, 2 letter abbreviation for state
    Returns a list containing WalkScore, BusScore, and BikeScore in that order"""

    r = requests.get(f"https://www.walkscore.com/{state}/{city}")
    images = bs(r.text, features="lxml").select(".block-header-badge img")
    print(images)
    return [int(str(x)[10:12]) for x in images]


@router.post("/api/livability")
async def get_livability(city: City):
    return {"livability": 47.0}
