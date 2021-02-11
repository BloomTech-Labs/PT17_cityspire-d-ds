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

* /info
This is the link to the AWS RDS Postgres database.

* /get_data
Here users can query cities and get an overview of the city
```
{
  "city": {
    "city": "San Francisco",
    "state": "CA"
  },
  "latitude": 37.7749,
  "longitude": -122.4194,
  "rental_price": 2000,
  "crime": "High",
  "pollution": "good",
  "walkability": 60,
  "livability": 49
}

```

* /coordinates
Here users can get coordinates for the city, this is used by frontend so users can visualize the city location
```

{
  "latitude": 37.7749,
  "longitude": -122.4194
}

```

* /crime
Here users get a low, medium, high range for crime in specific cities based on the FBI crime database
```

{
  "crime": "High"
}

```

* /rental_price
Here users can see the estimate for rental prices in the city they are interested in 

```

{
  "rental_price": 1500
}

```

* /pollution
This endpoint allows users to gauge the pollution on the aqi index

```

{
  "pollution": "Good"
}

```

* /walkability
This gives users an idea of how walkable their city is.
```
{
  "walkability": 60
}

```

* /livability
This endpoint gives users an estimate of livability based on user preference

```

{
  "livability": 47
}

```

### Code Links

Below are links to resources used to create this project:

    Datasets:
    (https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/tree/main/datasets_to_merge)
    The first link shows all combined csv that is stored in Postgres.

    (https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/tree/main/notebooks)
    This link shows all the different datasets we used to compile our data about the different cities.

    API: https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/tree/main/app This is where the code for creating the different endpoints can be located.

    Packages/Technologies used: https://github.com/Lambda-School-Labs/labspt15-cityspire-g-ds/blob/main/Pipfile


