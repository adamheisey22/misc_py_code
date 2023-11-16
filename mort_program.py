
import pandas as pd
import requests
#from termcolor import colored


def download_file(url, filename=' '):
    try:
        if filename:
            pass
        else:
            filename = req.url[downloadURL.rfind('_')+1:]

        with requests.get(url) as req:
            with open(filename, 'wb') as f:
                for chunk in req.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return filename
    except Exception as e:
        print(e)
        return None


Quoted_rate = float(input("What is the quoted rate?  "))

link = 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=MORTGAGE30US&scale=left&cosd=1971-04-02&coed=2022-03-24&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Weekly%2C%20Ending%20Thursday&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2022-03-26&revision_date=2022-03-26&nd=1971-04-02'

download_file(link, 'mort30USrate.csv')

df = pd.read_csv (r'C:\Users\adamh\Documents\mort30USrate.csv')

Mortgage_US_AVG = float(df['MORTGAGE30US'].tail(1))

def compare(Mortgage_US_AVG, Quoted_rate):
    if Quoted_rate - Mortgage_US_AVG > 0:
        return ('Above US average -> ' + str(Mortgage_US_AVG))
            #return colored('Above US average ->' + str(Mortgage_US_AVG), 'red')
    elif Quoted_rate - Mortgage_US_AVG < 0:
        return ('Below US Average -> ' + str(Mortgage_US_AVG))
            #return colored('Below US Average -> ' + str(Mortgage_US_AVG), 'green')

print(compare(Mortgage_US_AVG, Quoted_rate))