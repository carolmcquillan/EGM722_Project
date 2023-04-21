#- - - - - - - - - - - - - - -  Import required modules/packages/dependencies- - - - - - - - - - - - - - - - - - - - - _
%matplotlib inline
import cartopy
import os
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import pandas as pd
import folium
import ipywidgets
from IPython.display import HTML, display

plt.ion()  # make the plotting interactive

#- - - - - - - - - - - - - - -  Add initial data- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -- - - -
# This adds the bike locations we will be working with 
locations = ("https://www.belfastcity.gov.uk/getmedia/f68a4e53-68df-429c-8ac8-a8be9411ab73/belfast-bike-stations-updated-25-june-2021.csv")
bike_station_locations= pd.read_csv(locations)
#TODO: add additional layers
#- - - - - - - - - - - - - - -  Create the map- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#this creates the map and centres the map on the mean x,y of all bike station locations
map = folium.Map(location=[bike_station_locations.Latitude.mean(), bike_station_locations.Longitude.mean()], zoom_start=14, control_scale=True)


#- - - - - - - - - - - - - - -  Add data to the map- - - - - - - - - - - - - -- - - - - - - - - - - - - - - - - - - - -
#this adds the bike station point locations to the map and uses the location field as a popup label
for index, row in bike_station_locations.iterrows():
    lat = row['Latitude']
    long = row['Longitude']
    name = row['Location']
    
    folium.Marker([lat, long], name).add_to(map)

    
# add data layers control
folium.LayerControl().add_to(map)
#TODO: configure widget
#- - - - - - - - - - - - - - -  Carry out spatial analyses- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
oneKmBuffer = bike_station_locations.geometry.buffer(1)
oneKmBuffer.head()

#for index, row in bike_station_locations.iterrows():



#TODO: define and code for further analyses

#- - - - - - - - - - - - - - -  Present results from analysis- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#TODO: present results

#- - - - - - - - - - - - - - - Finishing Touches- - - - - - - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - -
#this adds a title to the map   
mapTitle = 'Belfast Bike Locations'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(mapTitle)   

map.get_root().html.add_child(folium.Element(title_html))    




#- - - - - - - - - - - - - - - Save the map- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#this saves the map as html
map.save("Belfast bikes.html")



#- - - - - - - - - - - - - - - Output the final map- - - - - - - - - - - - - - - 
map

