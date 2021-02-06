"""Machine learning functions"""
import requests
from bs4 import BeautifulSoup as bs
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


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


@router.post("/api/get_data", response_model=CityData)
async def get_data(city: City):
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
    data.update(walkscore)

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
async def get_rental_price(city: City):
    return {"rental_price": 1500}


@router.post("/api/pollution")
async def get_pollution(city: City):
    return {"pollution": "Good"}


@router.post("/api/walkability")
async def get_walkability(city: City):
    try:
        score = (await get_walkscore(**city.dict()))[0]
    except IndexError:
        raise HTTPException(status_code=422, detail="Walkscore not found")

    return {"walkability": score}


async def get_walkscore(city: str, state: str):
    """ Input: City, 2 letter abbreviation for state
    Returns a list containing WalkScore, BusScore, and BikeScore in that order"""

    city, state = city.title(), state.upper()
    r = requests.get(f"https://www.walkscore.com/{state}/{city}")
    images = bs(r.text, features="lxml").select("#hood-badges img")
    return [int(str(x)[10:12]) for x in images]


@router.post("/api/livability")
async def get_livability(city: City):
    return {"livability": 47.0}
