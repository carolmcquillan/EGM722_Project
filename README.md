# EGM722_Project
Repo for EGM722 Programming project

#Brief introduction to the repository - what it is, how to get started with it, and so on.**
#To be tailored,,,,,,
READMEFILE: Ulster_AEC Script: How-To Guide

Introduction

This Python script uses external modules including Geopandas, Cartopy and Matplotlib to plot a map of flooding in Lower Lough Erne in Country Fermanagh, Northern Ireland. Numpy, Pandas and Geopandas are used to perform spatial operations including converting to different projections, calculating area of polygons, and selecting geometries from one shapefile based on the geometry of another. The script runs on Python 3.8.
Since the API has been developed with specific test data, it is necessary to clone the Ulster_AEC GitHub repository to your computer so that the data files are available for the programme to use.

Running Ulster_AEC’s script

The script’s dependencies are GeoPandas, Pandas, Cartopy, Matplotlib, Numpy, Pandas and OS. These can be accessed by cloning the Ulster_AEC environment on your local machine. 
To clone the repository and reproduce the environment for the script to run, you need to install on your computer: 
•	Git (https://git-scm.com/downloads) 
•	Conda (https://docs.anaconda.com/anaconda/install/) 
Then, you need to clone the below repository to your computer using Git:
•	GitHub repository: https://github.com/AnnaQueenOfScots/Ulster_AEC
Once cloned, to duplicate the necessary environment for the project in Anaconda:
•	Use the environment.yml file which should now be on your local machine. 
This should enable you to run the script in Python 3.8 with all dependencies working. The gitignore file was created for PyCharm so that IDE is recommended. The data_files folder on your local machine should contain seven shapefiles (.shp) and their related files (e.g. .shx, .dbf, .prj).

This repository contains:
A python script: script.py
A folder containing six shapefiles: data_files 
An MIT licence file: LICENCE
A gitignore file: .gitignore
An environment file: Ulster_AEC.yml 

Troubleshooting Advice
•	Make sure shapefiles have all their related files in the data_files folder- at least .shp (feature geometry), .shx (index of feature geometry), .dbf (attribute information) and .prj (projection information) (see next point) are necessary for them to be opened by GeoPandas (Autodesk Support, 2014). These files are included in the test data.  
•	Projection Information: Make sure a Coordinate Reference System (projection) is specified for shapefiles. Naïve files- those with no spatial reference system- cannot be reprojected with cartopy. A GIS such as QGIS can project naïve files if necessary. 
•	For help with functions, use the help() method.  
•	If GeoPandas is not recognised, ensure your IDE is set to read the Ulster_AEC script. This might involve changing environments in Conda or configuring interpreter settings in PyCharm or other IDE. 
