# Labs DS

[Docs](https://docs.labs.lambdaschool.com/data-science/)

## CitySprire APP:
An app that analyzes data from cities such as populations, cost of living,\n
rental rates, crime rates, park (walk score), and many other social \n
and economic factors that are important in deciding where someone would like to live.\n
This app will present such important data in an intuitive and easy to understand interface.\n
Use data to find a place right for you to live.

### DS ENDPOINTS
http://cityscape-203.eba-ijacxhm2.us-east-1.elasticbeanstalk.com/

#### Database
* /api/info
This is the link to the AWS RDS Postgres database.

#### Machine Learning
* /api/get_data
Here users can query cities and get an overview of the city with recommendations for similar cities
```
{
  "city": {
    "city": "San Francisco",
    "state": "CA"
  },
  "latitude": 37.775,
  "longitude": -122.4183,
  "rental_price": 3700,
  "crime": "High",
  "air_quality_index": "Good",
  "population": 886007,
  "diversity_index": 69,
  "walkability": 87,
  "livability": 50,
  "recommendations": [
    {
      "city": "Oakland",
      "state": "CA"
    },
    {
      "city": "Portland",
      "state": "OR"
    },
    {
      "city": "San Diego",
      "state": "CA"
    },
    {
      "city": "San Jose",
      "state": "CA"
    },
    {
      "city": "Seattle",
      "state": "WA"
    }
  ]
}

```

* /api/coordinates
Here users can get coordinates for the city, this is used by frontend so users can visualize the city location
```

{
  "latitude": 37.775,
  "longitude": -122.4183
}

```

* /api/crime
Here users get a low, medium, high range for crime in specific cities based on the FBI crime database
```

{
  "crime": "High"
}

```

* /api/rental_price
Here users can see the estimate for rental prices in the city they are interested in 

```

{
  "rental_price": 1500
}

```

* /api/pollution
This endpoint allows users to gauge the pollution based on the aqi index

```

{
  "air_quality_index": "Good"
}

```

* /api/walkability
This gives users an idea of how walkable their city is.
```

{
   "walkability": 87
}

```

* /api/livability
This endpoint gives users an estimate of livability based on user preference
```

{
  "city": {
    "city": "San Francisco",
    "state": "CA"
  },
  "weights": {
    "walkability": 1,
    "low_rent": 1,
    "low_pollution": 1,
    "diversity": 1,
    "low_crime": 1
  }
}

```

```

{
  "livability": 56
}

```

* /api/population
This endpoint gives users the population information for their city
```

{
  "population": 886007
}

```

* /api/nearest
This endpoint allows users to find similar cities to the one they are interested in moving to
```

{
  "recommendations": [
    {
      "city": "Oakland",
      "state": "CA"
    },
    {
      "city": "Portland",
      "state": "OR"
    },
    {
      "city": "San Diego",
      "state": "CA"
    },
    {
      "city": "San Jose",
      "state": "CA"
    },
    {
      "city": "Seattle",
      "state": "WA"
    }
  ]
}

```

#### Visualization
Below are the visualization endpoints that allows users to visualize and get a better sense of the cities datapoints
* /api/demographics_graph
![Demographics](https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/blob/1883b842a436fd44bd8a8da697846aadfc9c3dbb/notebooks/visuals/demographics.png)


* /api/employment_graph
![Employment](https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/blob/1883b842a436fd44bd8a8da697846aadfc9c3dbb/notebooks/visuals/employment.png)


* /api/crime_graph
![Crime Statistics](https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/blob/1883b842a436fd44bd8a8da697846aadfc9c3dbb/notebooks/visuals/crime.png)


* /api/aqi_graph
![Air Quality](https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/blob/1883b842a436fd44bd8a8da697846aadfc9c3dbb/notebooks/visuals/air_quality.png)



### Code Links

Below are links to resources used to create this project:

### Models:
- Calculating Livability Index:
  https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/tree/main/notebooks/model/livability
  This is how we created the livability index for users (livability.pkl)
  
- Nearest Neigbhors Model:
  https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/tree/main/notebooks/model/nearest_neighbor
  This is how we created the recommendations for cities using the nearest neighbors model
      
### Feature Engineering

#### Diversity Index
The diversity indext was calculated using Simpson's Diversity Index
D = 1 - ((Σ n(n-1)/ (N(N-1))
* n = numbers of individuals of each ethnicity
* N = total number of individuals of all ethnicities
* The value of D ranges between 0 and 1


#### Air Quality
To determine overall air quality for each city, we used the median value and then created an algorithm that separated it based on https://www.airnow.gov/aqi/aqi-basics/ index. \
![Air Quality Index](https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/blob/main/notebooks/datasets/data/pollution/aqi_index.png)

#### Crime Rate Per 1000
Crime Rate per 1,000 inhabitants: This represents the number of Index offenses per 1,000 inhabitants.For example: What is the crime rate for a municipality with 513 Index offenses (murder, rape, robbery,aggravated assault, burglary, larceny-theft and motor vehicle theft), with a population of 8,280? 
513 (Index offenses) ÷ 8,280 (population) = .061957 x 1,000 = 62.0 (crime per 1,000 inhabitants)\
https://www.njsp.org/info/ucr2000/pdf/calc_ucr2000.pdf

  
### Datasets:
(https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/tree/main/notebooks/datasets/datasets_to_merge) \
The first link shows all combined csv that is stored in Postgres.

(https://github.com/Lambda-School-Labs/labspt15-cityspire-g-dsli/tree/main/notebooks/datasets/data) \
This link shows all the different datasets we used to compile our data about the different cities.

### API: 
https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/tree/main/app \
This is where the code for creating the different endpoints can be located.

### Packages/Technologies used: 
https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/blob/main/Pipfile

## Contributors

|                                                          [Jisha Obukwelu](https://github.com/jiobu1)                                                          |                                                       [Erik Seguinte](https://github.com/ErikSeguinte)                                                        |                                                      [dataabyss](https://github.com/dataabyss)                                                       |                                                      [Keino Baird](https://github.com/kbee181756)                                                       |
| :---------------------------------------------------------------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------: |
| [<img src="https://avatars.githubusercontent.com/u/32742307?s=460&u=5b16768fa895028ee408b983bf8c71b1c29bda00&v=4" width = "200" />](https://github.com/jiobu1) | [<img src="![image](https://user-images.githubusercontent.com/57121314/109588498-d7f9e280-7ad6-11eb-9cf9-4e99ef5dfd78.png)" width = "200" />](https://github.com/ErikSeguinte) | [<img src="https://www.dalesjewelers.com/wp-content/uploads/2018/10/placeholder-silhouette-male.png" width = "200" />](https://github.com/dataabyss) | [<img src="https://www.dalesjewelers.com/wp-content/uploads/2018/10/placeholder-silhouette-male.png" width = "200" />](https://github.com/kbee181756) | [<img src="https://www.dalesjewelers.com/wp-content/uploads/2018/10/placeholder-silhouette-male.png" width = "200" />](https://github.com/) |
|                                      [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/jiobu1)                                       |                            [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/ErikSeguinte)                             |                          [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/dataabyss)                           |                         [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/kbee181756)                          | [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/wvandolah) |
|                  [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/jishaobukwelu/)                  |                 [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/erik-seguinte/)                 |                [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/)                |                [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/keino-baird-7a54921b/)                | [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/) |

<br>
<br>

