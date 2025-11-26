#!/usr/bin/env python3
"""
fetch_coordinates.py
Holt fehlende Koordinaten für Städte via Nominatim API
"""

import pandas as pd
import time
import requests
from urllib.parse import quote

def fetch_coordinates():
    """Holt Koordinaten für Städte ohne Lat/Lng"""
    
    df = pd.read_csv('data/cities-master.csv')
    
    # Finde Städte ohne korrekte Koordinaten
    missing = df[(df['Lat'] == 51.0) | (df['Lng'] == 10.0) | df['Lat'].isna() | df['Lng'].isna()]
    
    if len(missing) == 0:
        print("✅ Alle Städte haben bereits Koordinaten")
        return
    
    print(f"📍 Hole Koordinaten für {len(missing)} Städte...")
    
    for idx, row in missing.iterrows():
        city_name = row['Stadt']
        bundesland = row['Bundesland']
        
        # Nominatim API Query
        query = f"{city_name}, {bundesland}, Deutschland"
        url = f"https://nominatim.openstreetmap.org/search?q={quote(query)}&format=json&limit=1"
        
        headers = {
            'User-Agent': 'City-Dashboard-Bot/1.0'
        }
        
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                df.at[idx, 'Lat'] = lat
                df.at[idx, 'Lng'] = lon
                print(f"  ✅ {city_name}: {lat:.4f}, {lon:.4f}")
            else:
                print(f"  ⚠️ {city_name}: Keine Koordinaten gefunden")
                # Setze Default für Bundesland
                defaults = {
                    'Baden-Württemberg': (48.7784, 9.1800),
                    'Bayern': (48.7904, 11.4979),
                    'Berlin': (52.5200, 13.4050),
                    'Brandenburg': (52.4125, 12.5316),
                    'Bremen': (53.0793, 8.8017),
                    'Hamburg': (53.5511, 9.9937),
                    'Hessen': (50.6521, 9.1624),
                    'Mecklenburg-Vorpommern': (53.6127, 12.4296),
                    'Niedersachsen': (52.6367, 9.8451),
                    'Nordrhein-Westfalen': (51.4332, 7.6616),
                    'Rheinland-Pfalz': (49.9129, 7.4496),
                    'Saarland': (49.3964, 7.0230),
                    'Sachsen': (51.1045, 13.2017),
                    'Sachsen-Anhalt': (51.9503, 11.6923),
                    'Schleswig-Holstein': (54.2194, 9.6961),
                    'Thüringen': (50.8614, 11.0522)
                }
                if bundesland in defaults:
                    df.at[idx, 'Lat'] = defaults[bundesland][0]
                    df.at[idx, 'Lng'] = defaults[bundesland][1]
            
            # Rate limiting - sei höflich zur API
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ {city_name}: Fehler - {e}")
            continue
    
    # Speichere aktualisierte CSV
    df.to_csv('data/cities-master.csv', index=False)
    print(f"✅ Koordinaten aktualisiert!")

if __name__ == '__main__':
    fetch_coordinates()
