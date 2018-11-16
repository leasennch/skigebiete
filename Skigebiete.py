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

# In[60]:


path = "/Users/leasenn/Google Drive/CAS Datenjournalismus/skigebiete/"
linkliste = []
df_skigebiete = pd.read_csv(path+"skigebiete_linkliste.csv") # Bereits kreierte Liste von Skigebieten verwenden
linkliste = df_skigebiete["skigebiete"].values.tolist()

skigebiete_final = []
errors = []
now = datetime.datetime.now()
zeitstempel = now.strftime("%Y-%m-%d_%H-%M")

for gebiet_link in linkliste:
    print(gebiet_link)
    website = requests.get("https://www.bergfex.ch"+gebiet_link).text
    soup = BeautifulSoup(website, "html.parser")
    try:
        # Live-Angaben auslesen
        infoboxes = soup.find_all('div', class_="snow-value")

        # Schneehöhe
        schneehoehe_berg = infoboxes[1].text.replace("cm", "").strip()
        schneehoehe_tal = infoboxes[2].text.replace("cm", "").strip()

        # Anlagen
        offene_anlagen = infoboxes[3].text.split(" von ") # Auslesen im Format "12 von 24" (offene Lifte sind immer das letzte TD, deshalb -1)
        total = offene_anlagen[1].strip()
        offen = offene_anlagen[0].strip()

        # Aktualisierungsdatum
        datum = infoboxes[0]
        # Zeitquelle angeben und formatieren, für "Heute" und "Gestern" richtiges Datum einsetzen...
        aktualisiertam = datum.text.replace("Heute", now.strftime("%d.%m.%Y")).replace("Gestern", (now-datetime.timedelta(days=1)).strftime("%d.%m.%Y")).strip()
        # bzw. für "Mo", "Di" und Co. Buchstaben rausnehmen und Jahreszahl anhängen
        tage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        for tag in tage:
            if(tag in aktualisiertam):
                teile_datum = aktualisiertam.replace(tag,"").split(", ")
                aktualisiertam = teile_datum[1]+now.strftime("%Y")+", "+teile_datum[2]

        aktualisiertam = datetime.datetime.strptime(aktualisiertam, "%d.%m.%Y, %H:%M").strftime("%Y-%m-%d_%H-%M")

        # Alles ins Dict schreiben
        skigebiete_final.append({"zeit_scraping": zeitstempel, "zeit_siteaktualisiert": aktualisiertam, "titel": gebiet_link, "totallifte": total, "offen": offen, "schneehoehe_berg":schneehoehe_berg, "schneehoehe_tal": schneehoehe_tal})
    except:
        errors.append({"status": "failed", "gebiet": gebiet_link, "zeitstempel" : zeitstempel})


# Alles abspeichern

# In[62]:


pd.DataFrame(skigebiete_final).to_csv(path+'skigebiete_oeffnungszeiten/oeffnungszeiten_'+zeitstempel+".csv")
pd.DataFrame(errors).to_csv(path+'skigebiete_oeffnungszeiten/errors_'+zeitstempel+".csv")


# In[ ]:
