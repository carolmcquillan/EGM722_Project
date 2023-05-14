
README: Project for EGM722: Field Identifier  

How to run the script successfully

In addition to a GitHub account, you will need to have git, conda, and python (version 3.11.3) installed on your machine, to run the script.  

1. Download the required files 

Make a clone of and download the following github repository:  carolmcquillan/EGM722_Project: Repo for EGM722 Programming project.  You should now have the requisite script, environment file and all sample datasets required on your machine.  

2. Create a conda environment

You will next need to use the environment (.yml) file in the repo to create the conda environment.  This can be done using Anaconda Navigator, by using the Import button on the Environments tab.
Alternatively, you can use the anaconda prompt.  From the open prompt, first navigate to the local repository and run the following command:    C:\Users\username>conda env create -f environment.yml 
The dependencies are listed here: python 3.11.3, cartopy, geopandas, os, notebook, pandas, pyepsg and openpyxl.  

3. Edit the data paths

The repository includes four datasets used by the script.  D=More detail is provided in the user guide. You will need to edit the script (using either notepad/notepad ++/an IDE of choice), to ensure the correct paths are provided to these datasets.  Simply search ‘c:\’  to find for references to any data paths and replace these references with the path to where you have stored the files on your local machine. 

4. Run the script

You will run the script using python from the anaconda prompt.  Open the prompt window is open, navigate to the directory where you have stored your file and activate the appropriate environment, using the conda activate command.  The environment is called 722Assignment_Carol, 

so enter:                           conda activate  722Assignment_Carol   
Then to run the script, enter:    	ipython Field_Identifier.py

The script should execute and run successfully. For Trouble shooting or more information, please refer to the user guide.     






