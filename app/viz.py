"""Data visualization functions"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

router = APIRouter()

class City(BaseModel):
    city: str = "New York"
    state: str = "NY"

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

@router.post("/api/demographics_graph")
async def demographics_plot(city):
    """
    Visualize demographic information for city

    ### Query Parameters
    - city

    ### Response
    JSON string to render with react-plotly.js
    """
    dataframe = pd.read_csv('https://media.githubusercontent.com/media/CityScape-Datasets/Workspace_Datasets/main/Models/nn_model/nn_model.csv')
    subset = dataframe[dataframe['City'] == city]
    demographics = ['Hispanic', 'White', 'Black', 'Native', 'Asian', 'Pacific']
    city_demographics = subset[demographics]
    city_demographics['Not Specified'] = 100 - city_demographics.sum(axis=1)
    melt = pd.melt(city_demographics)
    melt.columns = ['demographic', 'percentage']
    fig = px.pie(melt, values ='percentage', names ='demographic')
    fig.update_layout(
        title={
            'text': f'Demographics in {city}',
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    fig.show()
    return fig.to_json()

@router.post("/api/employment_graph")
async def employment_plot(city):
    """
    Visualize employment information for city
    - see industry breakdown and employment type

    ### Query Parameters
    - city

    ### Response
    JSON string to render with react-plotly.js
    """
    dataframe = pd.read_csv('https://media.githubusercontent.com/media/CityScape-Datasets/Workspace_Datasets/main/Models/nn_model/nn_model.csv')
    subset = dataframe[dataframe['City'] == city]

    # Industry
    industry = ['PrivateWork', 'PublicWork', 'SelfEmployed', 'FamilyWork']
    industry_type = subset[industry]
    industry_melt = pd.melt(industry_type)
    industry_melt.columns = ['industry', 'percentage']

    # Employment Type
    employment= ['Professional', 'Service', 'Office', 'Construction',	'Production']
    employment_type = subset[employment]
    type_melt = pd.melt(employment_type)
    type_melt.columns = ['employment type', 'percentage']

    #Create subplots
    fig = make_subplots(rows=1, cols=2, subplot_titles = (f'Industry in {city}', f'Employment Types in {city}'))
    fig.add_trace(go.Bar(x = industry_melt['industry'], y = industry_melt['percentage'],
                         marker = dict(color = industry_melt['percentage'], coloraxis = "coloraxis")),
                  row = 1, col = 1)
    fig.add_trace(go.Bar(x =type_melt['employment type'], y =type_melt['percentage'],
                         marker = dict(color = type_melt['percentage'], coloraxis = "coloraxis")),
                         row = 1, col = 2)
    fig.update_layout(coloraxis=dict(colorscale = 'Bluered_r'), showlegend = False)
    fig.show()
    return fig.to_json()

@router.post("/api/crime_graph")
async def crime_plot(city):
    """
    Visualize crime information for city
    - see overall crime breakdown
    - visualize breakdown of violent crime and property crime

    ### Query Parameters
    - city

    ### Response
    JSON string to render with react-plotly.js
    """
    dataframe = pd.read_csv('https://media.githubusercontent.com/media/CityScape-Datasets/Workspace_Datasets/main/Models/nn_model/nn_model.csv')
    subset = dataframe[dataframe['City'] == city]

    # Crime Categories
    crime = ['Violent crime', 'Property crime', 'Arson']
    crime_type = subset[crime]
    crime_melt = pd.melt(crime_type)
    crime_melt.columns = ['categories', 'total']

    # Violent Crime
    violent_crime= ['Murder and nonnegligent manslaughter','Rape', 'Robbery', 'Aggravated assault']
    violent_crime_type = subset[violent_crime]
    violent_crime_type_melt = pd.melt(violent_crime_type)
    violent_crime_type_melt.columns = ['violent crime type', 'total']

    # Property Crime
    property_crime= ['Burglary','Larceny- theft', 'Motor vehicle theft',]
    property_crime_type = subset[property_crime]
    property_crime_melt = pd.melt(property_crime_type)
    property_crime_melt.columns = ['property crime type', 'total']

    #Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles = (f"Crime Breakdown in {city}", f"Violent Crime Breakdown in {city}", f"Property Crime Breakdown in {city}"),
        specs = [[{"type":"xy", 'rowspan':2}, {"type": "pie"}],
                 [None, {"type": "pie"}]],

    )

    fig.add_trace(go.Bar(name = 'Crime Types', x = crime_melt['categories'], y = crime_melt['total']),
                  row = 1, col = 1)
    fig.add_trace(go.Pie(values = violent_crime_type_melt['total'],
                         labels = violent_crime_type_melt['violent crime type']),
                         row = 1, col = 2)
    fig.add_trace(go.Pie(values = property_crime_melt['total'],
                         labels = property_crime_melt['property crime type']),
                         row = 2, col = 2)
    fig.update_layout(height=600, width=1000)
    fig.show()
    return fig.to_json()

@router.post("/api/aqi_graph")
async def air_quality_plot(city):
    """
    Visualize air quality information for city

    ### Query Parameters
    - city

    ### Response
    JSON string to render with react-plotly.js
    """
    dataframe = pd.read_csv('https://media.githubusercontent.com/media/CityScape-Datasets/Workspace_Datasets/main/Models/nn_model/nn_model.csv')
    subset = dataframe[dataframe['City'] == city]
    air_quality_index = ['Days with AQI', 'Good Days', 'Moderate Days','Unhealthy for Sensitive Groups Days', 'Unhealthy Days','Very Unhealthy Days', 'Hazardous Days', 'Max AQI',
       '90th Percentile AQI', 'Median AQI', 'Days CO', 'Days NO2', 'Days Ozone', 'Days SO2', 'Days PM2.5', 'Days PM10']
    air_quality_details = subset[air_quality_index]
    air_quality_melt = pd.melt(air_quality_details)
    air_quality_melt.columns = ['air quality indicators', 'days']
    fig = px.bar(air_quality_melt, x =air_quality_melt['days'], y =air_quality_melt['air quality indicators'], orientation='h')
    fig.update_layout(
        xaxis_range = [0, 360],
        height=600, width=1000,
        title={
            'text': f'Air Quality in {city}',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    fig.show()
    return fig.to_json()