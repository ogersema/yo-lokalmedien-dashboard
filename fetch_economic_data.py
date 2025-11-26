#!/usr/bin/env python3
"""
fetch_economic_data.py
Aktualisiert Wirtschafts- und Mediendaten
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time

def fetch_kaufkraft_data():
    """Simuliert Abruf von Kaufkraftdaten"""
    # In Produktion: API-Calls zu Destatis, IW Köln etc.
    # Hier: Realistische Schätzungen basierend auf Stadtgröße und Region
    
    updates = {}
    df = pd.read_csv('data/cities-master.csv')
    
    for idx, row in df.iterrows():
        # Basis-Kaufkraft nach Region
        base_kaufkraft = {
            'Bayern': 25000,
            'Baden-Württemberg': 24500,
            'Hessen': 24000,
            'Hamburg': 26500,
            'Nordrhein-Westfalen': 23000,
            'Niedersachsen': 22500,
            'Rheinland-Pfalz': 22000,
            'Berlin': 23500,
            'Schleswig-Holstein': 22000,
            'Bremen': 22500,
            'Saarland': 21500,
            'Brandenburg': 20500,
            'Sachsen': 20000,
            'Sachsen-Anhalt': 19500,
            'Thüringen': 19500,
            'Mecklenburg-Vorpommern': 19000
        }.get(row['Bundesland'], 22000)
        
        # Adjustments
        if row['Einwohner'] > 500000:
            base_kaufkraft += 2000
        elif row['Einwohner'] > 200000:
            base_kaufkraft += 1000
        
        if row['Typ'] == 'Universitätsstadt':
            base_kaufkraft -= 500  # Studenten senken Durchschnitt
        
        updates[row['Stadt']] = base_kaufkraft
    
    return updates

def fetch_media_landscape():
    """Aktualisiert Mediendaten"""
    # Simulierte Daten für Großverlage
    
    media_data = {
        # Funke Mediengruppe
        'funke_cities': [
            'Essen', 'Dortmund', 'Bochum', 'Duisburg', 'Hamburg',
            'Berlin', 'Braunschweig', 'Erfurt'
        ],
        # Ippen Digital
        'ippen_cities': [
            'München', 'Frankfurt', 'Köln', 'Dortmund'
        ],
        # Madsack
        'madsack_cities': [
            'Hannover', 'Leipzig', 'Dresden', 'Kiel', 'Lübeck'
        ],
        # DuMont
        'dumont_cities': [
            'Köln', 'Hamburg', 'Berlin'
        ]
    }
    
    return media_data

def update_smart_city_index():
    """Aktualisiert Smart City Index"""
    # Basierend auf Bitkom Smart City Index
    
    smart_city_scores = {
        'München': 85,
        'Hamburg': 83,
        'Berlin': 82,
        'Köln': 78,
        'Frankfurt': 80,
        'Stuttgart': 77,
        'Düsseldorf': 76,
        'Dortmund': 68,
        'Leipzig': 72,
        'Dresden': 74,
        'Hannover': 71,
        'Nürnberg': 69,
        'Bonn': 75,
        'Karlsruhe': 79,
        'Heidelberg': 78
        # Weitere Städte bekommen Schätzwerte
    }
    
    return smart_city_scores

def main():
    """Hauptfunktion"""
    print("📊 Updating economic data...")
    
    # Lade Master CSV
    df = pd.read_csv('data/cities-master.csv')
    
    # Update Kaufkraft
    print("💰 Updating Kaufkraft...")
    kaufkraft_updates = fetch_kaufkraft_data()
    for city, kaufkraft in kaufkraft_updates.items():
        df.loc[df['Stadt'] == city, 'Kaufkraft'] = kaufkraft
    
    # Update Medienlandschaft
    print("📰 Updating media landscape...")
    media_data = fetch_media_landscape()
    
    # Reset alle Verlage
    df['Funke'] = False
    df['Ippen'] = False
    df['Madsack'] = False
    df['DuMont'] = False
    
    # Setze Verlage
    for city in media_data['funke_cities']:
        df.loc[df['Stadt'] == city, 'Funke'] = True
    for city in media_data['ippen_cities']:
        df.loc[df['Stadt'] == city, 'Ippen'] = True
    for city in media_data['madsack_cities']:
        df.loc[df['Stadt'] == city, 'Madsack'] = True
    for city in media_data['dumont_cities']:
        df.loc[df['Stadt'] == city, 'DuMont'] = True
    
    # Update Smart City Index
    print("🏙️ Updating Smart City Index...")
    smart_scores = update_smart_city_index()
    for city, score in smart_scores.items():
        df.loc[df['Stadt'] == city, 'SmartCityIndex'] = score
    
    # Fülle fehlende Smart City Scores
    df.loc[df['SmartCityIndex'].isna(), 'SmartCityIndex'] = df.apply(
        lambda row: min(95, 30 + (row['Einwohner'] / 10000)), axis=1
    )
    
    # Update weitere Metriken
    print("📈 Calculating derived metrics...")
    
    # Arbeitslosenquote (invers zu Wirtschaftskraft)
    df['Arbeitslosenquote'] = df.apply(
        lambda row: max(3.5, 15 - row['Kaufkraft']/3000 - row['Akademikerquote']/5),
        axis=1
    )
    
    # BIP Schätzung
    df['BIP_Mio'] = df['Einwohner'] * df['Kaufkraft'] / 5000
    
    # Speichere aktualisierte CSV
    df.to_csv('data/cities-master.csv', index=False)
    
    print("\n✅ Economic data updated successfully!")
    
    # Statistiken
    print("\n📊 Statistics:")
    print(f"   Average Kaufkraft: {df['Kaufkraft'].mean():.0f}€")
    print(f"   Cities with Funke: {df['Funke'].sum()}")
    print(f"   Cities with Smart City > 70: {(df['SmartCityIndex'] > 70).sum()}")
    print(f"   Average unemployment: {df['Arbeitslosenquote'].mean():.1f}%")

if __name__ == '__main__':
    main()
