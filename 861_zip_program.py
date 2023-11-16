#install dependencies
#py -m pip install pandas xlrd os io zipfile urllib

import pandas as pd
import os
import io
from zipfile import ZipFile
import urllib
import zipfile
import requests


def read_zip(zip_fn, extract_fn=None):
    zf = ZipFile(zip_fn)
    if extract_fn:
        return zf.read(extract_fn)
    else:
        return {name:zf.read(name) for name in zf.namelist()}

Dir_path = input("What is the directory path for saving EIA ZIP data files?:  ")
os.chdir(Dir_path)
r = Dir_path.replace("/", "\\")
EIA20r = r + '\\EIA'   

while True:
    Current_year = (input("What is the current year? --NOTE: list the last two digits ex. 2020 enter 20 -- : ")) 
    e_Years = input("What are the previous years to be downloaded to this location? --NOTE: list the last two digits followed by a comma ex. for 2018, 2017 ENTER 17, 18 : ") 
    e_Years = e_Years.split(",")
    e_Years.append(Current_year)
    print(e_Years)
    check1 = input("Is this the correct list of years to be downloaded? ENTER N if incorrect, otherwise press any key to continue: ")
    if check1.upper() == "N": #start over if selected NOTE
        continue
    #download zip files from EIA website and in directory path folder:
    for i in range(len(e_Years)):
        if (i==len(e_Years)-1):
            urlc = "https://www.eia.gov/electricity/data/eia861/zip/f86120" + Current_year + '.zip'
            E861c = urllib.request.urlretrieve(urlc, "EIA" + Current_year + ".zip")
        else:
            url = 'https://www.eia.gov/electricity/data/eia861/archive/zip/f86120' + e_Years[i] + '.zip'
            E861 = urllib.request.urlretrieve(url, "EIA" + e_Years[i] + ".zip")
    print('Fin')
    break


    