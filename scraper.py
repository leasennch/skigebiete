import requests
from bs4 import BeautifulSoup
import datetime
import scraperwiki
import csv

linkliste = []
reader = csv.reader(open("skigebiete_linkliste.csv"))
for row in reader:
    linkliste.append(row[0])

skigebiete_final = []
for gebiet_link in linkliste:
    print(gebiet_link)
    website = requests.get("https://www.bergfex.ch"+gebiet_link).text
    soup = BeautifulSoup(website, "html.parser")

    # Titel des Skigebiets
    titel = soup.find('h1', {"class": "has-sup"})
    titel = (titel.text.replace("Skigebiet ", ""))
    # Offene Skilifte auslesen
    for skigebiet in soup.find_all('table', class_="schneewerte"):
        offenelifte = (skigebiet.find_all('td')[-1].text).split(" von ") # Auslesen im Format "12 von 24" (offene Lifte sind immer das letzte TD, deshalb -1)
        total = offenelifte[1].strip()
        offen = offenelifte[0].strip()
        now = datetime.datetime.now()
        zeitstempel = now.strftime("%Y-%m-%d_%H-%M")
        scraperwiki.sqlite.save(unique_keys=[zeitstempel], data={"zeit": zeitstempel, "titel": titel, "totallifte": total, "offen": offen})
