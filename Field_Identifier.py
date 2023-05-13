# Import the required modules
import cartopy
import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature
from colorama import Fore
import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import openpyxl
import os
import pandas as pd
from shapely.geometry.point import Point

# import sys


# Before we proceed, we'll set the CRS that we shall be working with: Universal Transverse Mercator
myCRS = ccrs.epsg(2157)


# This "assign_Area_Length" function assigns area in km2 and length in meters to any geodataframe

def assign_area_length(gdf):
    for ind, row in gdf.iterrows():  # iterate over each row in the GeoDataFrame
        gdf.loc[ind, 'Area_km2'] = row[
                                       'geometry'].area / 1000000  # assign the row's geometry length to a new column
    for ind, row in gdf.iterrows():  # iterate over each row in the GeoDataFrame
        gdf.loc[ind, 'Length_m'] = row['geometry'].length  # assign the row's geometry length to a new column, Length


# This scale_bar function adds a scale bar to the output map:
def scale_bar1():
    points = gpd.GeoSeries([Point(53.5, 6.5), Point(54.5, 6.5)], crs=2157)
    points = points.to_crs(2157)  # Projected to my crs
    distance_meters = points[0].distance(points[1])             #  the distance between the 2 point above
                                                                # which will be used to generate the scale bar
    ax.add_artist(ScaleBar(distance_meters, box_color="none", location="lower right"))


def scale_bar2(ax, location=(0.99, 0.035)):
    x0, x1, y0, y1 = ax.get_extent()
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    ax.plot([sbx - 30000, sbx], [sby, sby], color='k', linewidth=5, transform=ax.projection)
    ax.plot([sbx - 30000, sbx], [sby, sby], color='w', linewidth=5, transform=ax.projection)
    ax.plot([sbx - 25000, sbx], [sby, sby], color='k', linewidth=5, transform=ax.projection)
    ax.plot([sbx - 20000, sbx], [sby, sby], color='w', linewidth=5, transform=ax.projection)
    ax.plot([sbx - 10000, sbx], [sby, sby], color='k', linewidth=5, transform=ax.projection)

    ax.text(sbx - 22000, sby + 3500, "Kilometres", fontsize=8, transform=myCRS)  # add the scale bar labels to the axis
    ax.text(sbx - 1200, sby - 4500, '30', transform=ax.projection, fontsize=6)  # exact positions do not
    ax.text(sbx - 12000, sby - 4500, '20', transform=ax.projection, fontsize=6)  # place well on map
    ax.text(sbx - 22000, sby - 4500, '10', transform=ax.projection, fontsize=6)  # so numbers have been placed
    ax.text(sbx - 26500, sby - 4500, '5', transform=ax.projection, fontsize=6)  # in best display positions
    ax.text(sbx - 32000, sby - 4500, '0', transform=ax.projection, fontsize=6)

# The steps referred to in the script from here on in, correspond to the steps set out in the User Guide
# STEP 1:
# Ask for essential user input:
# First ask for user to input ASSI name to be investigated

Selected_ASSI = input(Fore.LIGHTGREEN_EX + "\n\nEnter the name of ASSI to investigate, "
                                           "or enter \'All\' for a Northern Ireland level overview:")
# TODO: Work with ASSI Name in lower case


# To check a valid value has been input, first add the geodataframe need to perform this check
ASSI = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/EGM722_Project//data_files/ASSI.shp')).to_crs(epsg=2157)
ASSI.to_excel("ASSI.xlsx")
# Check and give user 3 attempts to make valid input
count = 0
while count < 2:
    try:
        if (Selected_ASSI in ASSI.NAME.values) or (Selected_ASSI == 'All'):
            print(Fore.LIGHTWHITE_EX + '\n\nGood Choice! Let\'s investigate ' + Selected_ASSI)
            break
        elif Selected_ASSI not in ASSI.NAME.values:
            print(Fore.RED + '\nThis is an invalid choice. Please try again......')
            Selected_ASSI = input(
                Fore.LIGHTGREEN_EX + "Enter the name of ASSI to investigate, "
                                     "or enter \'All\' for a Northern Ireland level overview:")
            count += 1
    except ValueError:
        print(Fore.LIGHTGREEN_EX + "Only text input allowed")

if count == 2: print(Fore.RED + '\n\n\n\nProgramme quitting due to invalid user input.............................'
                     '\n\nPlease refer to the user guide to help identify a valid ASSI name for input.'); os._exit(0)

# Step 2: Ask for user to define the buffer distance
Dist_km_str = input(
    Fore.LIGHTGREEN_EX + "\n\nSpecify a buffer distance in kilometers (no decimals or commas permitted):")
# TODO: Verify user input is a keyboard number and give 3 chances for valid input
Dist_km_int = int(Dist_km_str)
Dist_m_int = Dist_km_int * 1000

# Provide user  update
print(Fore.LIGHTWHITE_EX + '\n\nCreating a {} km buffer around {}'.format(Dist_km_str, Selected_ASSI))

# Step 3: Work with tht ASSI data - Now, we're working with the ASSI data which was added above:
assign_area_length(ASSI)  # first, apply this user created function to assign length and area to gdf

ASSI = ASSI.drop(['MAP_SCALE', 'CONFIRMDAY', 'CONFIRM_HA', 'DECLAREDAY', 'DECLARE_HA',  # Dropping fields not needed
                  'GIS_AREA', 'GIS_LENGTH', 'PARTIES', 'Shape_STAr', 'Shape_STLe', 'Hyperlink'], axis=1)

newASSIorder = ['OBJECTID', 'geometry', 'REFERENCE', 'NAME', 'COUNTY', 'SPECIESPT1', 'SPECIESPT2',
                # Creating new column order
                'HABITAT', 'EARTH_SCI', 'Area_km2', 'Length_m']
ASSI = ASSI.reindex(columns=newASSIorder)  # Applying new order to gdf

# To have the valid data in our ASSI gdf,
if Selected_ASSI == 'All':
    ASSI = ASSI  # ASSI gdf contains all rows as requested by user
else:  # or (depending on the user input)
    ASSI = ASSI.loc[ASSI['NAME'] == Selected_ASSI]  # ASSI gdf now only contains row of the selected ASSI


# Step 4: Buffering ASSI(s)
# Here we are Undertaking initial spatial analysis to create a buffer of the selected ASSI(s)
# we'll be buffering by the user defined  distance from above
ASSI_buffer = ASSI.copy()                                   # first, made a copy of the current ASSI gdf
                                                            # (this may be 1 feature or all-depending on user's choice)
ASSI_buffer.geometry = ASSI.geometry.buffer(
    Dist_m_int)  # This is where a buffer of the ASSI(s) is created.  It is based upon the user selected Buffer Distance
ASSI_buffer_dis = ASSI_buffer.dissolve()                    # This dissolves the features in the ASSI_buffer gdf
                                                            # to create new 'ASSI_buffer_dis' gdf
assign_area_length(ASSI_buffer_dis)

print('\nSpatial buffering in progress.....................')
print('\nDissolving polygons...............................')


# Step 5: Work with the Agricultural Field and Livestock data
# Add first Agricultural Fields dataset(this includes Field ID's and geometry)
AgFields = gpd.read_file(
    os.path.abspath('c:/Carol_PG_CERT_GIS/EGM722_Project/data_files/AgFields.shp'))  # add Agricultural fields data
AgFields.to_crs(epsg=2157, inplace=True)  # assigning the crs to the gdf
assign_area_length(AgFields)  # applying user created function to assign length and area to gdf
newAgFieldsorder = ['geometry', 'FieldID', 'Hectares', 'Area_km2', 'Length_m', 'X_COORD',
                    'Y_COORD']  # creating new order for columns
AgFields = AgFields.reindex(columns=newAgFieldsorder)  # applying new column order to the gdf

# Adding second Agricultural dataset (Livestock numbes- this is non-spatial, it includes Field IDs
# which will be used as a join field and also includes animal counts
FieldInfo = pd.read_excel(
    os.path.abspath('C:/Carol_PG_CERT_GIS/EGM722_Project/data_files/FieldInfo.xlsx'))  # Add in Excel table

# Now joining FieldInfo (pandas dataframe) onto the AgFields(geopandas dataframe)
AgFields = AgFields.merge(FieldInfo, on='FieldID', how='left')
AgFields = AgFields.drop(['X_COORD', 'Y_COORD'], axis=1)  # drop unneeded columns
print('\nJoining data.....................')


# Step 6: Performing spatial join on Fields and ASSI(s)
# by overlaying agricultural fields with the dissolved buffer to spatially join the records
# AgFields.crs == ASSI_buffer_dis.crs                    #checking the crs of gdfs being processed  are the same
FieldsInBuf = gpd.sjoin(AgFields, ASSI_buffer_dis, how='inner',
                        predicate='intersects')  # uses intersect method, though can be changed to 'within' if needed
print(
    '\nSpatial join in progress..........................')  # if changing to within, will also need to update the title

# Step 7: Creating output map for spatial visualisation of results
# Now, we're creating an output map to show ASSI(s), Buffer area and Agricultural Fields:
myFig = plt.figure(figsize=(10, 10))  # creating figure of size 10x10 (representing the page size in inches)
ax = plt.axes(
    projection=myCRS)  # creating axes object in the figure (within which data shall be plotted), using predefined crs

# first, we set the map extent:
xmin, ymin, xmax, ymax = ASSI.total_bounds  # Bounding co-ords of the ASSI dataset are set against the axes extent
if Selected_ASSI != 'All':  # The axes extent will vary, depending upon whether the user chose to investigate
    mapExtent = ax.set_extent(  # a single ASSI or all.
        [xmin - Dist_m_int - 2500, xmax + Dist_m_int + 2500, ymin - Dist_m_int - 2500, ymax + Dist_m_int + 2500],
        crs=myCRS)  # If we're investigating a single ASSI, this will zoom the map just outside of the buffer zone
else:
    mapExtent = ax.set_extent(
        [xmin - 2500, xmax + 2500, ymin - 2500, ymax + 2500],
        # Or if we're investigating ALL ASSI's, this will focus map
        crs=myCRS)  # at a Northern Ireland level( just outside the ASSI extent)

# Add background and labels to enhance the map:
if Selected_ASSI == 'All':  # add background features to NI scale map for aesthetic/context setting purposes only
    ax.add_feature(cartopy.feature.OCEAN)  # adding oceans for background
    ax.add_feature(cartopy.feature.LAND)  # adding land for background
    towns = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/egm722_Practicals/egm722/week2/data_files/Towns.shp'))
    towns.to_crs(epsg=2157, inplace=True)  # adding towns data to give additional context- (crs specified)
    city_handle = ax.plot(towns.loc[towns['TOWN_NAME'] == 'Belfast'].geometry.x,
                          # adding legend handles for City and Towns
                          towns.loc[towns['TOWN_NAME'] == 'Belfast'].geometry.y, 'o', color='r', ms=6, transform=myCRS)
    town_handle = ax.plot(towns.loc[towns['TOWN_NAME'] != 'Belfast'].geometry.x,
                          towns.loc[towns['TOWN_NAME'] != 'Belfast'].geometry.y, 's', color='0.5', ms=6,
                          transform=myCRS)
    # next we're adding the text labels for the towns and cities (all are stored within the towns gdf)
    for ind, row in towns.iterrows():  # towns.iterrows() returns the index and row
        x, y = row.geometry.x, row.geometry.y  # get the x,y location for each town
        ax.text(x, y, row['TOWN_NAME'].title(), fontsize=8, transform=myCRS)  # use plt.text to place a label at x,y


else:  # we'll not add a background to a larger scale map, because it's not accurate enough
    # However here we'll label the ASSI
    ASSI["x"] = ASSI.centroid.map(
        lambda p: p.x)  # so first we need to get x,y co-ords and assign these positions to be used by labels
    ASSI["y"] = ASSI.centroid.map(lambda p: p.y)
    for ind, row in ASSI.loc[ASSI['NAME'] == Selected_ASSI].iterrows():  # 'ASSI.iterrows()' returns the index and row
        x, y = row.x, row.y  # get the x,y location for each ASSI (created using lambda above)
        ax.text(x, y, row['NAME'].title(), fontsize=8, color='red',
                transform=myCRS)  # use plt.text to place a label at x,y

# Next, we're creating Shapely features for Fields, ASSI's, the dissolved buffer feature and Fields that
# fall within the buffer so that we can add the data in the geodataframes to the map:
AgFields_feature = ShapelyFeature(AgFields['geometry'], myCRS, edgecolor='w', facecolor='lightgrey', linewidth=0.3)
ASSI_feature = ShapelyFeature(ASSI['geometry'], myCRS, edgecolor='none', facecolor='lightgreen', linewidth=1)
FieldsInBuf_feature = ShapelyFeature(FieldsInBuf['geometry'], myCRS, edgecolor='yellow', facecolor='none', linewidth=1)
ASSI_buffer_feature = ShapelyFeature(ASSI_buffer_dis['geometry'], myCRS, edgecolor='red', facecolor='none', hatch='xxx',
                                     alpha=0.2, linewidth=1)

# Now we're adding the Shapely features created above, to the map:
ax.add_feature(AgFields_feature)  # add the Field data to map
ax.add_feature(ASSI_feature)  # add the ASSI data to map
ax.add_feature(FieldsInBuf_feature)  # add the Selected Field data to map
ax.add_feature(ASSI_buffer_feature)  # add selected ASSI 3km Buffer to map:

# AAdd gridlines to the map:
gridlines = ax.gridlines(draw_labels=True,  # draw  labels for the grid lines
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],  # add longitude lines at 0.5 deg intervals
                         ylocs=[54, 54.5, 55, 55.5],  # add latitude lines at 0.5 deg intervals
                         linestyle='--')  # define the linestyle
gridlines.right_labels = False  # turn off the left-side labels
gridlines.top_labels = False  # turn off the bottom labels
gridlines.left_labels = True  # turn on the left-side labels
gridlines.bottom_labels = True  # turn on the bottom labels

# Add a north arrow to the map:
x, y, arrow_length = 0.07, 0.1, 0.075  # Here we're specifying the x,y position and
ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),                   # height of arrow and here we're specifying
            arrowprops=dict(facecolor="black", width=3.5, headwidth=15),    # what and how the text should appear
            ha='center', va='center', fontsize=15,
            xycoords=ax.transAxes)

# Add a title and scalebar:                                                  #We have a standard scalebar for a selected
if Selected_ASSI != 'All':  # ASSI and a special scalebar for All ASSI's!
    ax.set_title("Fields Within/Partially Within " + str(Dist_km_int) + "km of " + Selected_ASSI + " ASSI")
    scale_bar1()
else:
    ax.set_title(
        "Fields Within/Partially Within " + str(Dist_km_int) + "km of an Area of Special Scientific Interest(ASSI)")
    scale_bar2(ax)

# Now we'll generate handles for the legend:
ASSI_handles = [
    mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgreen', edgecolor='lightgreen')]  # generate handles for legend
ASSI_buffer_handles = [
    mpatches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='red', hatch='xxx', alpha=0.2, linewidth=1)]
AgField_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgrey', edgecolor='w')]
FieldsInBuf_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgrey', edgecolor='yellow')]

# Now create the legend for the map:
if Selected_ASSI != 'All':  # We won't include the Town and City symbols on a Selected ASSI map
    handles = ASSI_handles + ASSI_buffer_handles + AgField_handles + FieldsInBuf_handles
    labels = ['ASSI', (str(Dist_km_int)) + 'km Buffer', 'Field', 'Field Inside']

else:  # We will include the Town and City symbols on a NI scale map
    handles = town_handle + city_handle + ASSI_handles + ASSI_buffer_handles + AgField_handles + FieldsInBuf_handles
    labels = ['Town', 'City', 'ASSI', (str(Dist_km_int)) + 'km Buffer', 'Field', 'Field Inside']

leg = ax.legend(handles, labels, title='Legend', title_fontsize=12,  # Now add the legend to the map
                fontsize=10, loc='upper left', frameon=True, framealpha=1)

# Let's create a name that we can use and re-use for our various outputs (including map, excel and shapefile outputs)
# First to create a relevant filename (based on ASSI Reference number) we need to remove some characters
ASSICode = str(FieldsInBuf.REFERENCE.unique())
ASSICode = ASSICode.replace("[", "")  # replacing [ with no character
ASSICode = ASSICode.replace("]", "")  # replacing ] with no character
ASSICode = ASSICode.replace("'", "")  # replacing ' with no character

if Selected_ASSI != 'All':  # then use either
    OutputName = ASSICode + "_" + str(
        Dist_km_int) + "km_" + Selected_ASSI  # ASSICode, to create the prefix name 'selected ASSI' outputs
else:  # or
    OutputName = "ALL_ASSI" + str(Dist_km_int) + "km"  # "ALL_ASSI" to create the prefix name for 'All ASSI' outputs

# Now we're applying the naming convention from above to save the map:
myFig.savefig(OutputName + '_map.png', dpi=300, bbox_inches='tight')
print('\nExporting output map to ............' + str(OutputName) + '_map.png')

# Step 8: Exporting Field records to excel
# Dropping fields that are not required before, exporting to Excel
xlsx_FieldOutput = FieldsInBuf.drop(['geometry', 'index_right', 'OBJECTID', 'REFERENCE', 'NAME', 'COUNTY', 'SPECIESPT1',
                                     'SPECIESPT2', 'HABITAT', 'EARTH_SCI', 'Area_km2_right', 'Length_m_right'], axis=1)
xlsx_FieldOutput = xlsx_FieldOutput.rename(columns={'Area_km2_left': 'Area_km2', 'Length_m_left': 'Length_m'})
xlsx_FieldOutput.to_excel(
    OutputName + "_Fields.xlsx")  # exports the features to an Excel file for future use (if required)
print('\nExporting Field records to..........' + str(OutputName) + "_Fields.xlsx")    # this informs the user on-screen
                                                                              # that we're saving field records to Excel

# Step 9: Creating Descriptive statistics to export to text file
# first we create the variable required

# Field Info
total_Area = AgFields.area.sum() / 1000000                                                # Calculating stats for Fields
total_Area_inside = FieldsInBuf.area.sum() / 1000000
total_Area_outside = total_Area - total_Area_inside

percentAllFields = total_Area / total_Area * 100
percentFieldsInside = total_Area_inside / total_Area * 100
percentFieldsOutside = 100 - percentFieldsInside

# Animal Info                                                                            # Calculating stats for Animals
NIPigCount = FieldInfo['Pig_Count'].sum()
NICattleCount = FieldInfo['Cattle_Count'].sum()
NIPoultryHouseCount = FieldInfo['PoultryHouses'].sum()

totalPigCount = FieldsInBuf['Pig_Count'].sum()
total_CattleCount = FieldsInBuf['Cattle_Count'].sum()
totalPoultryHouses = FieldsInBuf['PoultryHouses'].sum()

percentPigCount = totalPigCount / NIPigCount * 100
percentCattleCount = total_CattleCount / NICattleCount * 100
percentPoultryHouses = totalPoultryHouses / NIPoultryHouseCount * 100

AvPigCount = FieldsInBuf['Pig_Count'].mean()
AvCattleCount = FieldsInBuf['Cattle_Count'].mean()
AvPoultryHouses = FieldsInBuf['PoultryHouses'].mean()

#then we rename the Selected_ASSI variable, so that all out priont statements make sense
if Selected_ASSI == "All":
    Selected_ASSI = " an ASSI"
else:
    pass

# Next, we let the user know that we are going to export Field and Animal stats to a results text file
print('\nExporting Descriptive Statistical data to..........' + str(OutputName) + "_Results.txt")

# and now export the results to the text file
with open(OutputName + "_Results.txt", "a") as f:
    print(OutputName + " Results \n\n", file=f)
    print("Field Info:", file=f)
    print("Total area of all fields in NI is {:.0f} km2".format(total_Area), file=f)
    print("Total area of all fields falling within / partially within " + str(
        Dist_km_int) + "km of" + Selected_ASSI + ":       {:.0f} km2 ({:.2f}%)".format(total_Area_inside,
                                                                                       percentFieldsInside), file=f)
    print("Total area of all fields falling entirely outside of " + str(
        Dist_km_int) + "km from " + Selected_ASSI + ":         {:.0f} km2 ({:.2f}%)\n".format(total_Area_outside,
                                                                                              percentFieldsOutside),
          file=f)
    print("Animal Info: ", file=f)
    print("Total count of pigs within/ partially within the " + str(
        Dist_km_int) + "km buffer:                 {:.0f} pigs ({:.2f}%)".format(totalPigCount, percentPigCount),
          file=f)
    print("Total count of cattle within/ partially within the " + str(
        Dist_km_int) + "km buffer:             {:.0f} cattle ({:.2f}%)".format(total_CattleCount, percentCattleCount),
          file=f)
    print("Total count of poultry houses within/ partially within the " + str(
        Dist_km_int) + "km buffer:        {:.0f} poultry houses ({:.2f}%)\n\n".format(totalPoultryHouses,
                                                                                      percentPoultryHouses), file=f)
    print("Mean number of pigs in fields within/ partially within " + str(
        Dist_km_int) + "km of " + Selected_ASSI + ":                     {:.0f} pigs".format(AvPigCount), file=f)
    print("Mean number of cattle in fields within/ partially within " + str(
        Dist_km_int) + "km of " + Selected_ASSI + ":                  {:.0f} cattle".format(AvCattleCount), file=f)
    print("Mean number of poultry houses in fields within/ partially within " + str(
        Dist_km_int) + "km of " + Selected_ASSI + ":           {:.0f} poultry houses\n\n\n\n".format(AvPoultryHouses),
          file=f)
    print("Descriptive Statistics for fields within " + str(Dist_km_int) + "km\n", file=f)

    print(FieldsInBuf.describe(), file=f)
# TODO: Add Summary ASSI data eg area to the above output

#Step 10: Exporting geodataframes to shapefiles
#Next, we let the user know that we are going to export various datasets to shapefile
ASSI_buffer.to_file(OutputName + "_Buffer.shp")
print('\nExporting shapefile to..........' + str(OutputName) + "_Buffer.shp")

FieldsInBuf.to_file(OutputName + "_Fields.shp")
print('\nExporting shapefile to..........' + str(OutputName) + "_Fields.shp")

if Selected_ASSI == ' an ASSI':                      # this section ensures we don't create a shp containing all ASSI's
    pass
else:
    ASSI.to_file(ASSICode + '_' + Selected_ASSI + "_ASSI.shp")
    print("\nExporting shapefile to.........." + ASSICode + '_' + Selected_ASSI + "_ASSI.shp")


# Here the users receives a final summary message on screen
print(Fore.LIGHTBLUE_EX + '\n\n\nThe script has run successfully and created the following:')
print(Fore.LIGHTYELLOW_EX + '\n1 x Map Output File (png format)')
print('\n1 x Text File (txt format)')
print('\n1 x Data Table (xlsx format)')

if Selected_ASSI != " an ASSI":
    print('\n3 x Spatial File Outputs (shp format)')
else:
    print('\n2 x Spatial File Outputs (shp format\n\n\n\n)')
print("\n\n\n ")

# End of script

