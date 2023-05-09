#Import the required modules
import sys

from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import cartopy
import geopandas as gpd
import pandas as pd
import openpyxl
import os
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


#Add new functions

# This "assign_Area_Length" function assigns area in km2 and length in meters to any geodataframe
def assign_Area_Length(gdf):
    for ind, row in gdf.iterrows(): # iterate over each row in the GeoDataFrame
        gdf.loc[ind, 'Area_km2'] = row['geometry'].area / 1000000 # assign the row's geometry length to a new column, Area
    
    for ind, row in gdf.iterrows(): # iterate over each row in the GeoDataFrame
        gdf.loc[ind, 'Length_m'] = row['geometry'].length  # assign the row's geometry length to a new column, Length


#This scale_bar function adds a scale bar to the output map:
def scale_bar(ax, location=(0.1, 0.05)):
    x0, x1, y0, y1 = ax.get_extent()
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]
    #sbx = x0 + (x1 - x0) * location[0]
    #sby = y0 + (y1 - y0) * location[1]

    ax.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=7, transform=ax.projection)
    ax.plot([sbx, sbx - 5000], [sby, sby], color='k', linewidth=6, transform=ax.projection)
    ax.plot([sbx-5000, sbx - 10000], [sby, sby], color='w', linewidth=6, transform=ax.projection)
    ax.plot([sbx-9000, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=ax.projection)

    ax.text(sbx, sby-4500, '10 km', transform=ax.projection, fontsize=6)
    ax.text(sbx-5250, sby-4500, '5', transform=ax.projection, fontsize=6)#should be 6250 but doesn't place well
    ax.text(sbx-9750, sby-4500, '1', transform=ax.projection, fontsize=6)# should be 11250 but doesn't place well
    ax.text(sbx-12500, sby-4500, '0', transform=ax.projection, fontsize=6)# add the scale bar to the axis


# Ask for essential user input:
#first ask for user to input ASSI name to be investigated

Selected_ASSI = input("Enter the name of ASSI to investigate, or enter \'All\' for a Northern Ireland level overview:")

ASSI = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/EGM722_Project//data_files/ASSI.shp')).to_crs(epsg=2157)


count=0
while count < 2:
    try:
        if Selected_ASSI in ASSI.NAME.values or Selected_ASSI =='All':
            print('This is a valid choice')
            break
        elif Selected_ASSI not in ASSI.NAME.values:
            print('\nThis is an invalid choice. Please try again.')
            Selected_ASSI = input("Enter the name of ASSI to investigate, or enter \'All\' for a Northern Ireland level overview:")
            count += 1
    except ValueError:
        print("only text input allowed")

if count == 2: print('\n\n\n\nProgramme quitting due to invalid user input.............................'
                     '\n\nPlease refer to the user guide to help identify a valid ASSI name for input.'); os._exit(0)


#then ask user to determine the buffer distance to be used
Dist_km_str = input("\n\nSpecify a buffer distance in kilometers (no decimals or commas allowed):" )
#TODO: Verify user input is a keyboard number
print('\n\nData processing in progress.....................')

Dist_km_int = int(Dist_km_str)
Dist_m_int = Dist_km_int*1000

# adding and work with the ASSI data #
ASSI = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/EGM722_Project//data_files/ASSI.shp')).to_crs(epsg=2157)
assign_Area_Length(ASSI) #apply user created function to assign lenght and area to gdf
ASSI = ASSI.drop(['MAP_SCALE', 'CONFIRMDAY', 'CONFIRM_HA', 'DECLAREDAY','DECLARE_HA',
                  'GIS_AREA', 'GIS_LENGTH', 'PARTIES', 'Shape_STAr', 'Shape_STLe', 'Hyperlink'], axis=1)    #Drop unneccessary fields

newASSIorder = ['OBJECTID','geometry', 'REFERENCE',  'NAME', 'COUNTY', 'SPECIESPT1', 'SPECIESPT2', #Create new order for columns
                  'HABITAT', 'EARTH_SCI', 'Area_km2', 'Length_m']                   
ASSI= ASSI.reindex(columns=newASSIorder)                                                           #Apply new order for columns

if Selected_ASSI=='All':
    ASSI= ASSI
else:
    ASSI = ASSI.loc[ASSI['NAME'] == Selected_ASSI]
    
################################################# # adding and work with the Field data ############################################################
#Add first Agri dataset(inc. Field ID's and geometry)
AgFields = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/EGM722_Project/data_files/AgFields.shp')) # add Agricultural fields data
AgFields.to_crs(epsg=2157, inplace=True)
assign_Area_Length(AgFields)             #apply user created function to assign length and area to gdf
newAgFieldsorder = ['geometry', 'FieldID',  'Hectares', 'Area_km2', 'Length_m', 'X_COORD', 'Y_COORD']  #Create new order for columns
                                       
AgFields= AgFields.reindex(columns=newAgFieldsorder)   

#Add second Agri dataset (inc.Field ID's and animal counts)
FieldInfo =  pd.read_excel(os.path.abspath('C:/Carol_PG_CERT_GIS/EGM722_Project/data_files/FieldInfo.xlsx')) #Add in excel table to join data

#join FieldInfo (pandas dataframe) onto the AgFields(geopandas dataframe)
AgFields = AgFields.merge(FieldInfo, on='FieldID', how='left')
AgFields = AgFields.drop(['X_COORD', 'Y_COORD'], axis=1) # drop unrequired columns



#################Initial spatial analysis to create a user defined buffer of all ASSIs ###########################

ASSI_buffer = ASSI.copy()
ASSI_buffer.geometry = ASSI.geometry.buffer(Dist_m_int) #create a buffer of ALL ASSIs based upon the User selected Buffer Distance
ASSI_buffer_dis = ASSI_buffer.dissolve()


################################################### overlay fields with buffer ###################################################
FieldsInBuf = gpd.sjoin(AgFields,ASSI_buffer_dis,how='inner',predicate='intersects',) 

 
######################## Create output map to show ASSI, Buffer extent and Fields within Buffer extent ########################


# create the applicable CRS -in this case- Universal Transverse Mercator reference system- to transform the data
myCRS = ccrs.epsg(2157)


# create a figure of size 10x10 (representing the page size in inches)
myFig = plt.figure(figsize=(10, 10)) 

# create an axes object in the figure (within which the data shall be plotted), using the predefined crs
ax = plt.axes(projection=myCRS)  

# first, we set the map extent
xmin, ymin, xmax, ymax = ASSI.total_bounds #then get this dataset bounds and set them against the axes extent '
mapExtent = ax.set_extent([xmin-Dist_m_int-6500, xmax+Dist_m_int+6500, ymin-Dist_m_int-6500, ymax+Dist_m_int+6500], crs=myCRS)




#add towns  to give additional context
towns = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/egm722_Practicals/egm722/week2/data_files/Towns.shp'))
towns.to_crs(epsg=2157, inplace=True)

###- - - - - - - - - - - - - - -  Add background features to map (for aesthetic/contest setting purposes only) - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -- - - -
if Selected_ASSI!='All':
     pass
else:
    ax.add_feature(cartopy.feature.OCEAN)
    ax.add_feature(cartopy.feature.LAND)
    town_handle = ax.plot(towns.geometry.x, towns.geometry.y, 's', color='0.5', ms=6, transform=myCRS) # to add the town point data to map and create town handle for legend:
    # add the text labels for the towns
    for ind, row in towns.iterrows():  # towns.iterrows() returns the index and row
         x, y = row.geometry.x, row.geometry.y  # get the x,y location for each town
         ax.text(x, y, row['TOWN_NAME'].title(), fontsize=8, transform=myCRS)  # use plt.text to place a label at x,y
    
###- - - - - - - - - - - - - - -  Add required data to the map- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -- - - -

#Create Shapely features to add to the map:
AgFields_feature = ShapelyFeature(AgFields['geometry'], myCRS, edgecolor='w', facecolor='lightgrey', linewidth=0.3)
ASSI_feature = ShapelyFeature(ASSI['geometry'], myCRS, edgecolor='none', facecolor='lightgreen', linewidth=1)
FieldsInBuf_feature = ShapelyFeature(FieldsInBuf['geometry'], myCRS, edgecolor='yellow', facecolor='none', linewidth=1)
ASSI_buffer_feature = ShapelyFeature(ASSI_buffer_dis['geometry'], myCRS, edgecolor='red', facecolor='none', hatch='xxx', alpha=0.2, linewidth=1)


#Add Shapely features to the map:
ax.add_feature(AgFields_feature)               # add the Field data to map
ax.add_feature(ASSI_feature)                   # add the ASSI data to map
ax.add_feature(FieldsInBuf_feature)            # add the Selected Field data to map
ax.add_feature(ASSI_buffer_feature)            # add selected ASSI 3km Buffer to map:
   


#add ASSI label to map-
if Selected_ASSI=='All':    #too many to add,if looking at all (there are 394!)
     pass
else:                                           
    ASSI["x"] = ASSI.centroid.map(lambda p: p.x) #this first requires x,yco-ords to be assigned to the feature(s)
    ASSI["y"] = ASSI.centroid.map(lambda p: p.y)
    for ind, row in ASSI.loc[ASSI['NAME'] == Selected_ASSI].iterrows():  # ASSI.iterrows() returns the index and row
        x, y = row.x, row.y  # get the x,y location for each town
    ax.text(x, y, row['NAME'].title(), fontsize=8, color ='red', transform=myCRS)  # use plt.text to place a label at x,y

#-----------------------------------------add gridlines:-----------------------------------------------------------------------

gridlines = ax.gridlines(draw_labels=True,  # draw  labels for the grid lines
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],  # add longitude lines at 0.5 deg intervals
                         ylocs=[54, 54.5, 55, 55.5])  # add latitude lines at 0.5 deg intervals
gridlines.right_labels = False  # turn off the left-side labels
gridlines.top_labels = False  # turn off the bottom labels
gridlines.left_labels = True  # turn on the left-side labels
gridlines.bottom_labels = True  # turn on the bottom labels


#-----------------------------add a north arrow:----------------------------------------------------------------------------------

x, y, arrow_length = 0.93, 0.1, 0.075
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor="black", width=3.5, headwidth=15),
            ha='center', va='center', fontsize=15,
            xycoords=ax.transAxes)


   
#-----------------------------add a title and scalebar:--------------------------------------------------------------------------------    --
if Selected_ASSI!='All':
     ax.set_title("Fields within/partially within " + str(Dist_km_int)+ "km of "+ Selected_ASSI +" ASSI")
else:
     ax.set_title("Fields within/partially within " + str(Dist_km_int)+ "km of an ASSI")
     scale_bar(ax)

################################################Create a map legend############################################################-

# generate a list of handles for the ASSI datasets
ASSI_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgreen', edgecolor='lightgreen')]
ASSI_buffer_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='red', hatch='xxx', alpha=0.2, linewidth=1)]
AgField_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgrey', edgecolor='w')]
FieldsInBuf_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgrey', edgecolor='yellow')]


if Selected_ASSI!='All':
    handles = ASSI_handles + ASSI_buffer_handles+  AgField_handles +FieldsInBuf_handles
    labels = ['ASSI', (str(Dist_km_int))+'km Buffer','Field','Field Inside']
else:
    handles =  town_handle +  ASSI_handles + ASSI_buffer_handles+  AgField_handles +FieldsInBuf_handles
    labels = ['Town', 'ASSI', (str(Dist_km_int))+'km Buffer','Field','Field Inside']


leg = ax.legend(handles, labels, title='Legend', title_fontsize=12,
                fontsize=10, loc='upper left', frameon=True, framealpha=1)


#-----------------------------outputName:--------------------------------------------------------------------------------    --
#First To create a relevant filename (based on ASSI Reference) to use for saving ma, excel and shapefile outputs, first
ASSICode = str(FieldsInBuf.REFERENCE.unique())
ASSICode = ASSICode.replace("[", "")
ASSICode = ASSICode.replace("]", "")
ASSICode = ASSICode.replace("'","")


if Selected_ASSI!='All':
   OutputName =ASSICode+"_"+ str(Dist_km_int)+ "km_" + Selected_ASSI  #then use the ASSICode to create the prefix name for any output:
else:
   OutputName ="ALL_ASSI"+ str(Dist_km_int)+ "km" #then use the ASSICode to create the prefix name for any output:
 

#------------------------save the map, tabular and spatial output, to xlsx, png and shp respectively: ---------------------------------------------------------------------------------
myFig.savefig(OutputName+'_map.png', dpi=300, bbox_inches='tight')
print('Saving map image to ............'+str(OutputName)+'_map.png')


#Drop unrequired fields before exporting to excel
xlsx_FieldOutput = FieldsInBuf.drop(['geometry', 'index_right', 'OBJECTID', 'REFERENCE', 'NAME', 'COUNTY', 'SPECIESPT1', 'SPECIESPT2', 'HABITAT', 'EARTH_SCI', 'Area_km2_right', 'Length_m_right'], axis=1)
xlsx_FieldOutput= xlsx_FieldOutput.rename(columns={'Area_km2_left': 'Area_km2', 'Length_m_left': 'Length_m'})
xlsx_FieldOutput.to_excel(OutputName+"_Fields.xlsx") # exports the features to an excel file for future use (if required)
print('Saving tabular data to..........' +str(OutputName) +"_Fields.xlsx")
FieldsInBuf.to_file(OutputName+"_Fields.shp")
print('Saving spatial data to..........' +str(OutputName) +"_Fields.shp")
ASSI_buffer.to_file(OutputName+"_Buffer.shp")
print('Saving spatial data to..........' +str(OutputName) +"_Buffer.shp")

if Selected_ASSI=='All':
   pass
else:
    ASSI.to_file(ASSICode+ '_' +Selected_ASSI+"_ASSI.shp")
    print("Saving spatial data to.........."+ ASSICode+ '_' +Selected_ASSI+"_ASSI.shp")


#--------------------------------------Output stats to All text file------------------------------------------------------------------------
#Field Info
total_Area = AgFields.area.sum()/1000000# Total area of all fields
total_Area_inside = FieldsInBuf.area.sum()/1000000 # total area of fields falling within the BUFFER
total_Area_outside = total_Area -total_Area_inside # total area of fields falling outside the BUFFER

percentAllFields=total_Area/total_Area*100
percentFieldsInside=total_Area_inside/total_Area*100
percentFieldsOutside=100-percentFieldsInside

#Animal Info
NIPigCount=FieldInfo['Pig_Count'].sum()
NICattleCount=FieldInfo['Cattle_Count'].sum()
NIPoultryHouseCount =FieldInfo['PoultryHouses'].sum()

totalPigCount= FieldsInBuf['Pig_Count'].sum()
total_CattleCount= FieldsInBuf['Cattle_Count'].sum()
totalPoultryHouses= FieldsInBuf['PoultryHouses'].sum()

percentPigCount= totalPigCount/NIPigCount*100
percentCattleCount= total_CattleCount/NICattleCount*100
percentPoultryHouses= totalPoultryHouses/NIPoultryHouseCount*100

AvPigCount= FieldsInBuf['Pig_Count'].mean()
AvCattleCount= FieldsInBuf['Cattle_Count'].mean()
AvPoultyHouses= FieldsInBuf['PoultryHouses'].mean()


if Selected_ASSI =="All":
   Selected_ASSI = " an ASSI"
else:
    pass
    
print('Saving summary data to..........' +str(OutputName) + "_Results.txt")

with open(OutputName + "_Results.txt", "a") as f:
  print(OutputName + " Results ", file=f)
  print(" ", file=f)
  print(" ", file=f)
  print("Field Info:", file=f)
  print("Total area of all fields in NI is {:.0f} km2".format(total_Area), file=f)
  print("Total area of all fields falling within / partially within " +str(Dist_km_int)+"km of" +Selected_ASSI+":       {:.0f} km2 ({:.2f}%)".format(total_Area_inside,percentFieldsInside), file=f)
  print("Total area of all fields falling entirely outside of " +str(Dist_km_int)+"km from "+Selected_ASSI+":         {:.0f} km2 ({:.2f}%)".format(total_Area_outside,percentFieldsOutside), file=f)
  print(" ", file=f)
  print("Animal Info: ", file=f)
  print("Total count of pigs within/ partially within the " +str(Dist_km_int)+"km buffer:                 {:.0f} pigs ({:.2f}%)".format(totalPigCount,percentPigCount), file=f)
  print("Total count of cattle within/ partially within the " +str(Dist_km_int)+"km buffer:             {:.0f} cattle ({:.2f}%)".format(total_CattleCount, percentCattleCount), file=f)
  print("Total count of poultry houses within/ partially within the " +str(Dist_km_int)+"km buffer:        {:.0f} poultry houses ({:.2f}%)".format(totalPoultryHouses,percentPoultryHouses ), file=f)
  print(" ", file=f)
  print(" ", file=f)
  print("Mean number of pigs in fields within/ partially within " +str(Dist_km_int)+"km of "+Selected_ASSI+":                     {:.0f} pigs".format(AvPigCount), file=f)
  print("Mean number of cattle in fields within/ partially within " +str(Dist_km_int)+"km of "+Selected_ASSI+":                  {:.0f} cattle".format(AvCattleCount), file=f)
  print("Mean number of poultry houses in fields within/ partially within " +str(Dist_km_int)+"km of "+Selected_ASSI+":           {:.0f} poultry houses".format(AvPoultyHouses), file=f)
  print(" ", file=f)
  print(" ", file=f)  
  print(" ", file=f)
  print(" ", file=f) 
  print("Descriptive Statistics for fields within "+ str(Dist_km_int)+"km", file=f)
  print(" ", file=f) 
  print(FieldsInBuf.describe(),file=f)


print('The script has run successfully and created the following files:')
print('1 x Map File (png format)')
print('1 x Workbook Map Output (xlsx format)')

if Selected_ASSI != "an ASSI":
    print('3 x Spatial File Outputs (shp format)')
else:
    print('2 x Spatial File Outputs (shp format)')  #"an ASSI" is the current value if the user input 'ALL' at the start

print('1 x Text File (txt format)')

