"""Machine learning functions"""
from pickle import load
import requests
import os
import datetime
from bs4 import BeautifulSoup as bs
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.state_abbr import us_state_abbrev as abbr
from dotenv import dotenv_values, load_dotenv
from pathlib import Path
import pandas as pd
import numpy as np
from pypika import Query, Table, CustomFunction
import asyncio
from app.db import database, select, select_all
from typing import List, Optional
import json
from dotenv import dotenv_values, load_dotenv

router = APIRouter()
load_dotenv()

class City(BaseModel):
    city: str = "New York"
    state: str = "NY"


class CityRecommendations(BaseModel):
    recommendations: List[City]


class CityDataBase(BaseModel):
    city: City
    latitude: float
    longitude: float
    rental_price: float
    crime: str
    air_quality_index: str
    population: int
    diversity_index: float


class CityData(CityDataBase):
    walkability: float
    busability: float
    bikeability: float
    livability: float
    recommendations: List[City]


class CityDataFull(CityDataBase):
    good_days: int
    crime_rate_ppt: float
    nearest_string: str


class LivabilityWeights(BaseModel):
    walkability: float = 1.0
    low_rent: float = 1.0
    low_pollution: float = 1.0
    diversity: float = 1.0
    low_crime: float = 1.0


def validate_city(
    city: City,
) -> City:
    """Ensure City name and State name are in the right format.

    Ensures that the city name is in Title Case and the State is converted from
    Full name to All Caps ABBR if needed.

    args:
        city: The City object to be Validated

    returns:
        a City object in a proper format to be used elsewhere.

    raises:
        HTTPException:
            If the state cannot be converted into an ABBR
    """

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
async def get_data(city: City):
    """Retrieve all data for city

    Fetch data from DB, calculate derived stats, scrape Walkscore
    return data

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """

    city = validate_city(city)

    value = await select_all(city)

    full_data = CityDataFull(city=city, **value)
    tasks = await asyncio.gather(
        get_livability_score(city, full_data),
        get_walkability(city),
        get_busability(city),
        get_bikeability(city),
        get_recommendation_cities(city, full_data.nearest_string),
    )
    data = {**full_data.dict()}

    for item in tasks:
        data.update(item)

    return data


@router.post("/api/coordinates")
async def get_coordinates(city: City):
    """Retrieve coordinates for target city

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    value = await select(["lat", "lon"], city)
    return {"latitude": value[0], "longitude": value[1]}


@router.post("/api/crime")
async def get_crime(city: City):
    """Retrieve crime rate for target city

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    data = Table("data")
    value = await select("Crime Rating", city)
    return {"crime": value[0]}


@router.post("/api/rental_price")
async def get_rental_price(city: City):
    """Retrieve rental price for target city

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    value = await select("Rent", city)

    return {"rental_price": value[0]}


@router.post("/api/pollution")
async def get_pollution(city: City):
    """Retrieve pollution rating for target city

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    value = await select("Air Quality Index", city)
    return {"air_quality_index": value[0]}


@router.post("/api/walkability")
async def get_walkability(city: City):
    """Retrieve walkscore for target city

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    try:
        score = (await get_walkscore(**city.dict()))[0]
    except IndexError:
        raise HTTPException(
            status_code=422, detail=f"Walkscore not found for {city.city}, {city.state}"
        )

    return {"walkability": score}


@router.post("/api/busability")
async def get_busability(city: City):
    """Retrieve BusScore for target city

    args:
        city: The target city

    returns:
        Dictionary that contains the Bus Score, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    try:
        score = (await get_walkscore(**city.dict()))[1]
    except IndexError:
        raise HTTPException(
            status_code=422, detail=f"BusScore not found for {city.city}, {city.state}"
        )

    return {"busability": score}

    
@router.post("/api/bikeability")
async def get_bikeability(city: City):
    """Retrieve bikeScore for target city

    args:
        city: The target city

    returns:
        Dictionary that contains the BikeScore, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    try:
        score = (await get_walkscore(**city.dict()))[2]
    except IndexError:
        raise HTTPException(
            status_code=422, detail=f"BikeScore not found for {city.city}, {city.state}"
        )

    return {"bikeability": score}

async def get_walkscore(city: str, state: str):
    """Scrape Walkscore, BusScore, and BikeScore.

    args:
        city: The target city
        state: Target state as an all-caps 2-letter abbr

    returns:
        List containing WalkScore, BusScore, and BikeScore in that order
    """

    r_ = requests.get(f"https://www.walkscore.com/{state}/{city}")
    images = bs(r_.text, features="lxml").select(".block-header-badge img")
    return [int(str(x)[10:12]) for x in images]


@router.post("/api/livability")
async def get_livability(city: City, weights: LivabilityWeights = None):
    """Calculate livability score

    Fetch data from DB, calculate derived stats, scrape Walkscore
    return data

    args:
        city: The target city
        LivabilityWeights: Weights for the to use for calculation

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    values = await select(["Rent", "Good Days", "Crime Rate per 1000"], city)
    with open("app/livability_scaler.pkl", "rb") as f:
        s = load(f)
    v = [[values[0] * -1, values[1], values[2] * -1]]
    scaled = s.transform(v)[0]
    walkscore = await get_walkscore(city.city, city.state)
    diversity_index = await select("Diversity Index", city)

    rescaled = [walkscore[0]]
    rescaled.append(round(diversity_index[0]) * 100)
    for score in scaled:
        rescaled.append(score * 100)
    # breakpoint()
    if weights is None:
        return {"livability": round(sum(rescaled) / 5)}
    else:
        weighted = [
            rescaled[0] * weights.walkability,
            rescaled[1] * weights.diversity,
            rescaled[2] * weights.low_rent,
            rescaled[3] * weights.low_pollution,
            rescaled[4] * weights.low_crime,
        ]

        sum_ = sum(weighted)
        divisor = sum(weights.dict().values())

        return {"livability": round(sum_ / divisor)}


async def get_livability_score(city: City, city_data: CityDataFull):
    """Calculate livability score

    Fetch data from DB, calculate derived stats, scrape Walkscore
    return data

    args:
        city: The target city


    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """

    with open("app/livability_scaler.pkl", "rb") as f:
        s = load(f)
    v = [
        [
            city_data.rental_price * -1,
            city_data.good_days,
            city_data.crime_rate_ppt * -1,
        ]
    ]
    scaled = s.transform(v)[0]
    walkscore = await get_walkscore(city.city, city.state)

    rescaled = [walkscore[0], city_data.diversity_index]
    for score in scaled:
        rescaled.append(score * 100)

    return {"livability": round(sum(rescaled) / 5)}


@router.post("/api/population")
async def get_population(city: City):
    """Retrieve population rating for target city

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """

    city = validate_city(city)
    value = await select("Population", city)
    return {"population": value[0]}


@router.post("/api/nearest", response_model=CityRecommendations)
async def get_recommendations(city: City):
    """Retrieve recommended cities for target city

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """

    city = validate_city(city)
    value = await select("Nearest", city)

    recommendations = await get_recommendation_cities(city, value.get("Nearest"))

    return recommendations


@router.post("/api/traffic_data")
async def get_traffic(city: City):
    """Retrieve recommended cities for target city

    Fetch data from dataframe

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """

    
    # reading traffic dataframe into function 
    df = pd.read_csv("app\city_traffic.csv")
    
    # locate the exact row by city and state
    value = df.loc[((df["city"] == city.city) & (df["state"] == city.state))]
    # transform data row to numpy array 
    value = value.to_numpy()
    # if the values are out of index then they dont exist
    try: 
        response = {"city" : value[0][0], "state" : value[0][1], "world_rank" : value[0][2], "avg_congestion" : value[0][3], 
                    "am_peak": value[0][4], "pm_peak": value[0][5],   "worst_day" : value[0][6]}
    # if it doesnt exist, raise exception
    except IndexError:
        raise HTTPException(
            status_code=422, detail=f"Traffic data not found for {city.city}, {city.state}"
            )
    # otherwise return response
    return response
    

async def get_recommendation_cities(city: City, nearest_string: str):
    """Use the string and transform to City

    Fetch data from DB

    args:
        nearest_string: String consisting of the index numbers of the recommended cities.

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """

    test_list = nearest_string.split(",")

    data = Table("data")
    q2 = (
        Query.from_(data)
        .select(data["City"])
        .select(data["State"])
        .where(data.index)
        .isin(test_list)
    )

    recommendations = await database.fetch_all(str(q2))
    recs = CityRecommendations(
        recommendations=[
            City(city=item["City"], state=item["State"]) for item in recommendations
        ]
    )

    return recs


# weather API routes

load_dotenv()
API_KEY = os.getenv('PROJECT_API_KEY')


@router.get('/api/get_current_temp')
async def get_current_temp(city: City):

    temp_weather = json.loads(get_coordinates(city))
    
    url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=imperial" % (temp_weather['lat'], temp_weather['lon'], API_KEY)
    response = requests.get(url)
    data = json.loads(response.text)

    return data["main"]["temp"]
    pass

@router.get('/api/get_feels_like')
async def get_feels_like_temp(lat,lon):

    temp_weather = json.loads(get_coordinates(city))
    url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=imperial" % (temp_weather['lat'], temp_weather['lon'], API_KEY)
    response = requests.get(url)
    data = json.loads(response.text)

   
    return data["main"]["feels_like"]
    pass

@router.get('/api/get_temp_min')
async def get_min_temp(lat,lon):

    temp_weather = json.loads(get_coordinates(city))
    url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=imperial" % (temp_weather['lat'], temp_weather['lon'], API_KEY)
    response = requests.get(url)
    data = json.loads(response.text)


    return data["main"]["temp_min"]
    pass

@router.get('/api/get_temp_max')
async def get_max_temp(lat,lon):

    temp_weather = json.loads(get_coordinates(city))
    url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=imperial" % (temp_weather['lat'], temp_weather['lon'], API_KEY)
    response = requests.get(url)
    data = json.loads(response.text)

    return data["main"]["temp_max"]
    pass

@router.get('/api/get_humidity')
async def get_humidity(lat,lon):

    temp_weather = json.loads(get_coordinates(city))
    url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=imperial" % (temp_weather['lat'], temp_weather['lon'], API_KEY)
    response = requests.get(url)
    data = json.loads(response.text)

    return data["main"]["humidity"]
    pass

@router.get('/api/get_weather_all')
async def get_weather_all(lat,lon):

    temp_weather = json.loads(get_coordinates(city))
    url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=imperial" % (temp_weather['lat'], temp_weather['lon'], API_KEY)
    response = requests.get(url)
    data = json.loads(response.text)

    return data
    pass
=======
# This approach was origianllly developed by https://github.com/israel-dryer/Indeed-Job-Scraper/blob/master/indeed-tutorial.ipynb
# Also credit https://github.com/jiobu1 for help finding approaches to turning this into an API end point
# https://www.youtube.com/watch?v=eN_3d4JrL_w
# https://medium.com/@hannah15198/convert-csv-to-json-with-python-b8899c722f6d
@router.post('/api/job_opportunities')
async def job_opportunities(position, city:City):
    """Returns jobs opportunities from indeed.com

    Fetch first 10 job opportunities
    - Job title,
    - Company,
    - Job location
    - Post Date,
    - Extraction Date,
    - Job Description,
    - Salary,
    - Job Url
    
    args:
        - position: desired job
        - city: target city
    returns:
        Dictionary of requested data in a JSON object
    """


    records = []  

    city_name = validate_city(city)
    location = city_name.city + ' ' + city_name.state
    url = get_url(position, location) 

    response = requests.get(url)
    soup = bs(response.text, 'html.parser')
    cards = soup.find_all('div', 'jobsearch-SerpJobCard')

    for card in cards:
        record = get_record(card)
        records.append(record)

    #return total number of jobs by queary and city, state
    try:
        total_jobs = soup.find('div', id='searchCountPages').text.strip()
        total = total_jobs.split()[-2:]
        jobs = ' '.join(total)
    except AttributeError:
        total_jobs = ''
        jobs = ''

    return {"Search Results":jobs, "Top 10 Listings": records}

def get_record(card):
    # credit to https://github.com/jiobu1 
    """Extract job data from a single record"""
    atag = card.h2.a
    job_title = atag.get('title')
    company = card.find('span', 'company').text.strip()
    job_location = card.find('div', 'recJobLoc').get('data-rc-loc')
    job_summary = card.find('div', 'summary').text.strip()
    post_date = card.find('span', 'date').text.strip()

    try:
        salary = card.find('span', 'salarytext').text.strip()
    except AttributeError:
        salary = ''

    extract_date = datetime.datetime.today().strftime('%Y-%m-%d')
    job_url = 'https://www.indeed.com' + atag.get('href')

    record = {'Job Title': job_title,
              'Company': company,
              'Location': job_location,
              'Date Posted': post_date,
              'Extract Date': extract_date,
              'Description': job_summary,
              'Salary': salary,
              'Job Url': job_url}

    return record

def get_url(position, location):
    "Generate a url based on position and location"

    template = "https://www.indeed.com/jobs?q={}&l={}"
    url = template.format(position, location)
    return url
