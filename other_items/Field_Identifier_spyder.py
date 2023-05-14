#- - - - - - - - - - - - - - -  Import required modules/packages/dependencies- - - - - - - - - - - - - - - - - - - - - _
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
#import cartopy
import geopandas as gpd
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import folium
import ipywidgets
from IPython.display import HTML, display
import numpy as np
import seaborn as sns

import seaborn as sns



#- - - - - - - - - - - - - - -  Initial Map SetUp- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -- - - -
#%matplotlib notebook
# make the plotting interactive
#plt.ion()
# Set Seaborn style and color palette
sns.set_style("darkgrid")
sns.set_palette("husl")

# create the applicable CRS -in this case- Universal Transverse Mercator reference system- to transform the data
myCRS = ccrs.epsg(2157)

# create a figure of size 10x10 (representing the page size in inches)
myFig = plt.figure(figsize=(10, 10)) 

# create an axes object in the figure (within which the data shall be plotted), using the predefined crs
ax = plt.axes(projection=myCRS)  

# first, we just add the outline of Northern Ireland using cartopy's ShapelyFeature
outline= gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/egm722_Practicals/egm722/week2/data_files/NI_outline.shp')).to_crs(epsg=2157)

outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', facecolor='w') #load in dataset, to be used to set the map extent
xmin, ymin, xmax, ymax = outline.total_bounds #then get this dataset bounds and set them against the axes extent '
ax.add_feature(outline_feature) # add the features we've created to the map.
ax.set_extent([xmin-5000, xmax+5000, ymin-5000, ymax+5000], crs=myCRS) 


#- - - - - - - - - - - - - - -  Add required data- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -- - - -
#towns = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/egm722_Practicals/egm722/week2/data_files/Towns.shp'))
#towns.to_crs(epsg=2157, inplace=True)
AgFields = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/EGM722_Project/data_files/AgFields.shp'))
AgFields.to_crs(epsg=2157, inplace=True)
ASSI = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/EGM722_Project//data_files/ASSI.shp')).to_crs(epsg=2157)
#water = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/egm722_Practicals/egm722/week2/data_files/Water.shp')).to_crs(epsg=2157)

AgFields_feature = ShapelyFeature(AgFields['geometry'], myCRS, edgecolor='w', facecolor='lightgrey', linewidth=0.3)
ASSI_feature = ShapelyFeature(ASSI['geometry'], myCRS, edgecolor='lightgreen', facecolor='lightgreen', linewidth=0.1)
ax.add_feature(AgFields_feature)
ax.add_feature(ASSI_feature)

#- - - - - - - - - - - - - - -  Add required data- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -- - - -
ASSI_buffer = ASSI.copy()
ASSI_buffer.geometry = ASSI.geometry.buffer(3000)
#ASSI_buffer_feature = ShapelyFeature(ASSI_buffer['geometry'], myCRS, edgecolor='red', facecolor='none', linewidth=1)
#ax.add_feature(ASSI_buffer_feature)



ASSI_buffer_dis = ASSI_buffer.dissolve()
ASSI_bufDisfeature = ShapelyFeature(ASSI_buffer_dis['geometry'], myCRS, edgecolor='red', facecolor='none', linewidth=1)
ax.add_feature(ASSI_bufDisfeature)
myFig



