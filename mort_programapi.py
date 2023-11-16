import pandas as pd
import requests
from termcolor import colored
from fredapi import Fred

def mcompare(Mortgage_US_AVG, Quoted_rate):
    if Quoted_rate - Mortgage_US_AVG > 0:
        return colored('Above US average -> ' + str(Mortgage_US_AVG), 'red')
    elif Quoted_rate - Mortgage_US_AVG < 0:
        return colored('Below US Average -> ' + str(Mortgage_US_AVG), 'green')


while True:
    Quoted_rate = float(input("What is the quoted rate?" ))
    fred = Fred(api_key='5d2a56d5981ea3e548e729a11be0c21a')
    MORTGAGE30US = fred.get_series('MORTGAGE30US')
    Mortgage_US_AVG = float(MORTGAGE30US.tail(1))
    print(mcompare(Mortgage_US_AVG, Quoted_rate))
    check = input("Do you want to quit or start again? enter Y to restart or another key to end: ")
    if check.upper() == "Y": #go back to the top
        continue
    print ('Fin')
    break


