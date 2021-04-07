import urllib.request, json
import pandas as pd
import requests

"""This is a script used to scrape data off of the TomTom Traffic Index"""

# final.csv to dataframe for use of city column 
df = pd.read_csv('notebooks/datasets/datasets_to_merge/updated/final.csv')
# sorting df by total population
df = df.sort_values(by = 'TotalPop', ascending=False, inplace=True)

# list of cities to search through 
cities_by_population = df[['City', 'TotalPop']]

# keylist for generated dataframe column names


for c in cities_by_population['City']:
    # add a hyphen to city names that are two words
        c = '-'.join(c.split())
        c = "".join(c).lower()

        # keylist for generated dataframe column names
        keylist = ['city', 'world_rank',  
            'avg_congestion',
            'am_peak',  
            'pm_peak',
            'worst_day']

        city_data = {}

        for i in keylist:
            city_data[i] = None 

        base_url = f"https://www.tomtom.com/en_gb/traffic-index/page-data/{c}-traffic/page-data.json"

        with urllib.request.urlopen(base_url) as scrape:
            try:
                data = json.loads(scrape.read().decode())
                # if the json is uncodable that means we have been redirected to the home page
            except ValueError:
                continue
            else:
                
                
                # base path to 2019 data
                stats2019 = data['result']['data']['citiesJson']['stats2019']
                
                # city name
                city_data['city'] = c
                # world rank 2017
                city_data['world_rank'] = stats2019['rank']
                # average congestion of 2017
                city_data['avg_congestion'] = stats2019['congestion']
                # The AM and PM peak congestion for work days
                city_data['am_peak'] = str(round(int(stats2019['results']['workingDays']['amPeak']['congestion']), 2))
                city_data['pm_peak'] = str(round(int(stats2019['results']['workingDays']['pmPeak']['congestion']), 2))
                # Worst day of the year 
                city_data['worst_day'] = f"{stats2019['results']['worstDay']['month']}/{stats2019['results']['worstDay']['day']}/19"
                
                #  does the dataframe exist?
                try:
                    var = city_df
                except NameError:
                    var_exists = False
                else:
                    var_exists = True

                # if the dataframe doesnt exist, initialize a dataframe
                if var_exists == False:
                    city_df = pd.DataFrame(data = city_data, index = [0])
                    print(city_df)
                    continue

                else:
                    # append to dataframe
                    city_df = city_df.append(city_data, ignore_index = True) 
                    print(city_df)
                    continue
# Dataframe to csv for saving
city_df = city_df.drop_duplicates()
city_df.to_csv(r'notebooks/datasets/data/city_traffic/city_traffic.csv')

