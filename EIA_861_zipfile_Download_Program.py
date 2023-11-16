#install dependencies
#py -m pip install pandas xlrd os io zipfile urllib

import pandas as pd
import os
import io
from zipfile import ZipFile
import urllib
import zipfile
import requests

print('WELCOME!')
print("  ")
print("------------")

Dir_path = input("What is the directory path for saving EIA ZIP data files?:  ")
os.chdir(Dir_path)
r = Dir_path.replace("/", "\\")
EIA20r = r + '\\EIA'   

while True:
    Current_year = (input("What is the current (most recent) EIA 861 year available? --NOTE: ENTER the 4 digit year ex. 2020 and press ENTER key to continue: ")) 
    
    print("  ")
    print("------------")
    
    e_Years = input("What are the previous EIA 861 years to be downloaded to this location? --NOTE: ENTER the 4 digit year followed by a comma ex. 2017, 2018, 2019; press ENTER key to continue: ") 
    e_Years = e_Years.split(",")
    e_Years.append(Current_year)
    
    print("  ")
    print("------------")
    
    print(e_Years)
    check1 = input("Is the list above the correct list of years to be downloaded? ENTER N if incorrect, otherwise press any key to continue: ")
    
    print("  ")
    print("------------")
    print("One Moment Please")
    
    if check1.upper() == "N": #start over if selected NOTE
        continue
    #download zip files from EIA website and in directory path folder:
    for i in range(len(e_Years)):
        if (i==len(e_Years)-1):
            urlc = "https://www.eia.gov/electricity/data/eia861/zip/f861" + Current_year + '.zip'
            E861c = urllib.request.urlretrieve(urlc, "EIA" + Current_year + ".zip")
        else:
            url = 'https://www.eia.gov/electricity/data/eia861/archive/zip/f861' + e_Years[i] + '.zip'
            E861 = urllib.request.urlretrieve(url, "EIA" + e_Years[i] + ".zip")
            
    print("  ")
    print("------------")
    
    print('DOWNLOAD SUCCESSFUL')
    break
    
print('END and CLOSE')
