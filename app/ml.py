"""Machine learning functions"""

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class City(BaseModel):
    city: str
    state: str


class CityData(BaseModel):
    city: City
    latitude: str
    longitude: str
    rental_price: float
    crime: str
    pollution: str
    walkability: float
    livability: float


@router.post("/api/get_data", response_model=CityData)
async def get_data(city: City):
    data = {
        "city": {"city": "San Francisco", "state": "CA"},
        "latitude": "37.7749° N",
        "longitude": "122.4194° W",
        "rental_price": 2000,
        "pollution": "medium",
        "walkability": 60.0,
        "crime": "High",
        "livability": 49.0,
    }

    return data


@router.post("/api/coordinates")
async def get_coordinates(city: City):
    return {"latitude": "37.7749° N", "longitude": "122.4194° W"}


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
    return {"pollution": "Medium"}


@router.post("/api/walkability")
async def get_walkability(city: City):
    return {"walkability": 60.0}


@router.post("/api/livability")
async def get_livability(city: City):
    return {"livability": 47.0}
