#!/usr/bin/env python
# coding: utf-8

# ## Skigebiete scrapen

# In[3]:


# Libraries laden
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime


# Einzelne Seiten zu Skigebieten absaugen, Öffnungszeiten abspeichern, bzw. Fehler loggen

# In[4]:


linkliste = []
df_skigebiete = pd.read_csv("/Users/leasenn/Google Drive/CAS Datenjournalismus/skigebiete/skigebiete_linkliste.csv")
linkliste = df_skigebiete["skigebiete"].values.tolist()

skigebiete_final = []
errors = []
for gebiet_link in linkliste:
    website = requests.get("https://www.bergfex.ch"+gebiet_link).text
    soup = BeautifulSoup(website, "html.parser")

    # Titel des Skigebiets
    titel = soup.find('h1', {"class": "has-sup"})
    titel = (titel.text.replace("Skigebiet ", ""))
    # Offene Skilifte auslesen
    liveangaben = soup.find_all('table', class_="schneewerte")

    now = datetime.datetime.now()
    zeitstempel = now.strftime("%Y-%m-%d_%H-%M")

    if len(liveangaben) > 0:
        for skigebiet in liveangaben:
            offenelifte = (skigebiet.find_all('td')[-1].text).split(" von ") # Auslesen im Format "12 von 24" (offene Lifte sind immer das letzte TD, deshalb -1)
            total = offenelifte[1].strip()
            offen = offenelifte[0].strip()

            # Zeitquelle angeben
            aktualisiertam = skigebiet.find_all('td')[0].text.replace("Heute", now.strftime("%d.%m.%Y")).replace("Gestern", (now-datetime.timedelta(days=1)).strftime("%d.%m.%Y"))
            tage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
            for tag in tage:
                if(tag in aktualisiertam):
                    teile_datum = aktualisiertam.replace(tag,"").split(", ")
                    aktualisiertam = teile_datum[1]+"2018, "+teile_datum[2]

            skigebiete_final.append({"zeit_scraping": zeitstempel, "zeit_siteaktualisiert": aktualisiertam, "titel": titel, "totallifte": total, "offen": offen})
    else:
        errors.append({"status": "failed", "gebiet": gebiet_link, "zeitstempel" : zeitstempel})


# Alles abspeichern

# In[5]:


pd.DataFrame(skigebiete_final).to_csv('/Users/leasenn/Google Drive/CAS Datenjournalismus/skigebiete/skigebiete_oeffnungszeiten/oeffnungszeiten_'+zeitstempel+".csv")
pd.DataFrame(errors).to_csv('/Users/leasenn/Google Drive/CAS Datenjournalismus/skigebiete/skigebiete_oeffnungszeiten/errors_'+zeitstempel+".csv")


# In[ ]:
