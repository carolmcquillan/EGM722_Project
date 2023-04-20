import pandas as pd
import geopandas as gpd
import folium
 # This adds the bike locations we will be working with 
locations = ("https://www.belfastcity.gov.uk/getmedia/f68a4e53-68df-429c-8ac8-a8be9411ab73/belfast-bike-stations-updated-25-june-2021.csv")
bike_station_locations= pd.read_csv(locations)

#this creates the map and centres the map on the mean x,y of all bike station locations
map = folium.Map(location=[bike_station_locations.Latitude.mean(), bike_station_locations.Longitude.mean()], zoom_start=14, control_scale=True)

#this adds the point locations to the map and uses the location field as a popup label
for index, row in bike_station_locations.iterrows():
    lat = row['Latitude']
    long = row['Longitude']
    name = row['Location']
    
    folium.Marker([lat, long], name).add_to(map)

#this adds a title to the map   
mapTitle = 'Belfast Bike Locations'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(mapTitle)   



map.get_root().html.add_child(folium.Element(title_html))    

#this saves the map
map.save("Belfastbikes.html")
map
