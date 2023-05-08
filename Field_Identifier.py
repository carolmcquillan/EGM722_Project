###################################### Import required modules/packages/dependencies##########################################
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import cartopy
import geopandas as gpd
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import folium
import ipywidgets
# from IPython.display import HTML, display
import numpy as np
#import openpyxl

############################################### Essential User Input ######################################################
# first ask for user input to select an ASSI to investigate
print("Name of ASSI to investigate:")
Selected_ASSI = input()

# then ask user to determine the buffer distance to be used
print("Specify a buffer distance in kilometers. \nInput a whole number:")
Dist_km_str = input()
Dist_km_int = int(Dist_km_str)
Dist_m_int = Dist_km_int * 1000


################################################# New functions ############################################################

# This "assign_Area_Length" function assigns area in km2 and length in meters to any geodataframe
def assign_Area_Length(gdf):
    for ind, row in gdf.iterrows():  # iterate over each row in the GeoDataFrame
        ASSI.loc[ind, 'Area_km2'] = row[
                                        'geometry'].area / 1000000  # assign the row's geometry length to a new column, Area

    for ind, row in gdf.iterrows():  # iterate over each row in the GeoDataFrame
        ASSI.loc[ind, 'Length_m'] = row['geometry'].length  # assign the row's geometry length to a new column, Length

################################################# Initial Data SetUp ############################################################

#%matplotlib notebook

# create the applicable CRS -in this case- Universal Transverse Mercator reference system- to transform the data
myCRS = ccrs.epsg(2157)

# - - - - - - - - - - - - - - - - - - - - Bring in the key spatial datasets- - - - - - - - - - - - - - - - - - - - - - - -
# adding the ASSI data
ASSI = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/EGM722_Project//data_files/ASSI.shp')).to_crs(epsg=2157)

# add Agricultural fields data
AgFields = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/EGM722_Project/data_files/AgFields.shp'))
AgFields.to_crs(epsg=2157, inplace=True)

# - - - - - - - - - - - - - - -   - - - - -  Bring in the key other datasets-- - - - - - - - - - - - - - - - - - - - - - - - -
# where we want to bring in field data
# where we want to bring in landuse data
# where we want to join this data to the ASSI

# - - - - - - - - - - - - - - -   - - - - -  Create Essential layers for analyses- - - - - - - - - - - - - - - -- - - ---------
# create an GDF based upon the User selected ASSI
SelectedASSI = ASSI.loc[ASSI['NAME'] == Selected_ASSI]

# create an ASSI Buffer GDF based upon the User selected Buffer Distance
SelectedASSI_buffer = SelectedASSI.copy()
SelectedASSI_buffer.geometry = SelectedASSI.geometry.buffer(Dist_m_int)

# TOD remove spaces from ASSI Names for future saves
####shpName = Selected_ASSI[REFERENCE]+'_buf3km.shp'
# SelectedASSI_buffer.to_file(shpName)                  # exports the features to a new shapefile for future use (if required)

################################################## Spatial Analysis #########################################################

# - - - - - - - - - - - - - -  -  - - create an gdf to identify fields within the buffer - - - - - - - - - -  - - - - - - - - - - -
FieldsInBuf = gpd.sjoin(AgFields, SelectedASSI_buffer, how='inner', predicate='intersects', )

# Create relevant filename (based on ASSI Reference) and save to shapefile
ASSICode = str(FieldsInBuf.REFERENCE.unique())
ASSICode = ASSICode.replace("[", "")
ASSICode = ASSICode.replace("]", "")
ASSICode = ASSICode.replace("'", "")
FileTitle = (ASSICode + "_" + str(Dist_km_int) + "km" + ".shp")
FieldsInBuf.to_file(FileTitle)

# - - - - - - - - - - - -  Output summary analysis/ profile statistics for fields within the buffer area- - - - - - - - - - - -

# assign_Area_Length(ASSI) #apply user created function to assign lenght and area to gdf
# ASSI = ASSI.drop(['MAP_SCALE', 'CONFIRMDAY', 'CONFIRM_HA', 'DECLAREDAY','DECLARE_HA',
# 'GIS_AREA', 'GIS_LENGTH', 'PARTIES', 'Shape_STAr', 'Shape_STLe'], axis=1)    #Drop unneccessary fields
# neworder = ['geometry','OBJECTID', 'REFERENCE',  'NAME', 'COUNTY', 'SPECIESPT1', 'SPECIESPT2', #Create new order for columns
# 'HABITAT', 'EARTH_SCI', 'Areakm2', 'Length_m','Hyperlink']
# ASSI= ASSI.reindex(columns=neworder)                                                           #Apply new order for columns


######################## Create output map o show ASSI, Buffer extent and Fields within Buffer extent #########################

#%matplotlib notebook
# make the plotting interactive
# plt.ion()

# create the applicable CRS -in this case- Universal Transverse Mercator reference system- to transform the data
myCRS = ccrs.epsg(2157)

# create a figure of size 10x10 (representing the page size in inches)
myFig = plt.figure(figsize=(10, 10))

# create an axes object in the figure (within which the data shall be plotted), using the predefined crs
ax = plt.axes(projection=myCRS)

# first, we set the map extent
xmin, ymin, xmax, ymax = SelectedASSI.total_bounds  # then get this dataset bounds and set them against the axes extent '
mapExtent = ax.set_extent(
    [xmin - Dist_m_int - 5000, xmax + Dist_m_int + 5000, ymin - Dist_m_int - 5000, ymax + Dist_m_int + 5000], crs=myCRS)

###- - - - - - - - - - - - - - -  Add background features to map (for aesthetic/contest setting purposes only) - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -- - - -

ax.add_feature(cartopy.feature.OCEAN)

###- - - - - - - - - - - - - - -  Add required data to the map- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -- - - -

# Create Shapely features to add to the map:
SelectedASSI_feature = ShapelyFeature(SelectedASSI['geometry'], myCRS, edgecolor='none', facecolor='lightgreen',
                                      linewidth=1)
SelectedASSI_buffer_feature = ShapelyFeature(SelectedASSI_buffer['geometry'], myCRS, edgecolor='red', facecolor='none',
                                             linewidth=1)
FieldsInBuf_feature = ShapelyFeature(FieldsInBuf['geometry'], myCRS, edgecolor='yellow', facecolor='none', linewidth=1)
AgFields_feature = ShapelyFeature(AgFields['geometry'], myCRS, edgecolor='w', facecolor='lightgrey', linewidth=0.3)

# Add Shapely features to the map:
ax.add_feature(AgFields_feature)  # add the Field data to map
ax.add_feature(SelectedASSI_feature)  # add the ASSI data to map
ax.add_feature(FieldsInBuf_feature)  # add the Selected Field data to map
ax.add_feature(SelectedASSI_buffer_feature)  # add selected ASSI 3km Buffer to map:

###- - - - - - - - - - - - - - - ------ add lables to the map- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - --
# add ASSI label to map- this first requires x,yco-ords to be assigned to the feature(s)
ASSI["x"] = ASSI.centroid.map(lambda p: p.x)
ASSI["y"] = ASSI.centroid.map(lambda p: p.y)
for ind, row in ASSI.loc[ASSI['NAME'] == Selected_ASSI].iterrows():  # ASSI.iterrows() returns the index and row
    x, y = row.x, row.y  # get the x,y location for each town
    ax.text(x, y, row['NAME'].title(), fontsize=8, color='red', transform=myCRS)  # use plt.text to place a label at x,y

###- - - - - - - - - - - - - - - - - - --add legend  to the map- - - - - - - - - - - - - - -- - - - - - - -- - - - - - - -

# create handles for the legend:
ASSI_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgreen', edgecolor='lightgreen')]
ASSI_buffer_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='r')]
AgField_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgrey', edgecolor='w')]

handles = AgField_handles + ASSI_handles + ASSI_buffer_handles  # generate a list of handles for the legend
labels = ['Field', 'ASSI', (str(Dist_km_int) + 'km Buffer')]  # generate a list of lables for the legend

leg = ax.legend(handles, labels, title='Legend', title_fontsize=12,
                fontsize=10, loc='upper left', frameon=True,
                framealpha=1)  # assign legend paramenters to variable 'leg'

# -----------------------------------------add gridlines:-----------------------------------------------------------------------

gridlines = ax.gridlines(draw_labels=True,  # draw  labels for the grid lines
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],  # add longitude lines at 0.5 deg intervals
                         ylocs=[54, 54.5, 55, 55.5])  # add latitude lines at 0.5 deg intervals
gridlines.right_labels = False  # turn off the left-side labels
gridlines.top_labels = False  # turn off the bottom labels
gridlines.left_labels = True  # turn on the left-side labels
gridlines.bottom_labels = True  # turn on the bottom labels


# -----------------------------------------add a scale bar:-----------------------------------------------------------------------

# TODO - FIx Scale bar This "scale_bar" function creates a scale bar 10km wide, broken down by 1km and 5km
def scale_bar(ax, location=(0.1, 0.05)):
    x0, x1, y0, y1 = ax.get_extent()
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]
    # sbx = x0 + (x1 - x0) * location[0]
    # sby = y0 + (y1 - y0) * location[1]

    ax.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=7, transform=ax.projection)
    ax.plot([sbx, sbx - 5000], [sby, sby], color='k', linewidth=6, transform=ax.projection)
    ax.plot([sbx - 5000, sbx - 10000], [sby, sby], color='w', linewidth=6, transform=ax.projection)
    ax.plot([sbx - 9000, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=ax.projection)

    ax.text(sbx, sby - 4500, '10 km', transform=ax.projection, fontsize=6)
    ax.text(sbx - 4250, sby - 4500, '5', transform=ax.projection, fontsize=6)  # should be 6250 but doesn't place well
    ax.text(sbx - 9750, sby - 4500, '1', transform=ax.projection, fontsize=6)  # should be 11250 but doesn't place well
    ax.text(sbx - 12500, sby - 4500, '0', transform=ax.projection, fontsize=6)  # add the scale bar to the axis


scale_bar(ax)

# -----------------------------add a north arrow:----------------------------------------------------------------------------------

x, y, arrow_length = 0.93, 0.1, 0.075
ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
            arrowprops=dict(facecolor="black", width=3.5, headwidth=15),
            ha='center', va='center', fontsize=15,
            xycoords=ax.transAxes)

# -----------------------------add a title:--------------------------------------------------------------------------------    --

ax.set_title("Fields within " + str(Dist_km_int) + "km Buffer of " + Selected_ASSI + " ASSI");

# ------------------------------save the figure: ---------------------------------------------------------------------------------

mapNAme = Selected_ASSI + '_map.png'
myFig.savefig(mapNAme, dpi=300, bbox_inches='tight')
# FieldsInBuf.to_excel("output.xlsx")