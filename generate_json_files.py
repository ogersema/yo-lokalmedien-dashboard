#!/usr/bin/env python3
"""
generate_json_files.py
Generiert alle JSON-Dateien aus der Master-CSV
"""

import pandas as pd
import json
import os
from datetime import datetime

def load_master_csv():
    """Lade die Master-CSV mit allen Städten"""
    csv_path = 'data/cities-master.csv'
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Master CSV not found at {csv_path}")
    
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"✅ Loaded {len(df)} cities from master CSV")
    return df

def calculate_score(row):
    """Berechne den Gesamtscore für eine Stadt"""
    # Medien Score (max 25)
    medien_score = 25
    if row['Lokalzeitungen'] >= 5:
        medien_score -= 10
    elif row['Lokalzeitungen'] >= 3:
        medien_score -= 6
    elif row['Lokalzeitungen'] >= 2:
        medien_score -= 3
    
    if row.get('Funke', False):
        medien_score -= 3
    if row.get('Ippen', False):
        medien_score -= 3
    if row.get('Madsack', False):
        medien_score -= 3
    if row.get('DuMont', False):
        medien_score -= 2
    
    # Zielgruppe Score (max 25)
    zielgruppe_score = 0
    akademiker = row.get('Akademikerquote', 25)
    zielgruppe_score += min(12, (akademiker / 40) * 12)
    
    kaufkraft = row.get('Kaufkraft', 22000)
    zielgruppe_score += min(13, ((kaufkraft - 18000) / 15000) * 13)
    
    # Digital Score (max 25)
    digital_score = 12
    if row.get('OpenData', False):
        digital_score += 5
    
    smart_city = row.get('SmartCityIndex', 50)
    digital_score += min(8, (smart_city / 100) * 8)
    
    # Wirtschaft Score (max 25)
    wirtschaft_score = 15
    kaufkraft_bonus = min(10, ((kaufkraft - 20000) / 10000) * 10)
    wirtschaft_score += kaufkraft_bonus
    
    # Identität Score (max 25)
    identitaet_score = 15
    if row['Einwohner'] < 100000:
        identitaet_score += 3
    if row.get('Typ', '') in ['Universitätsstadt', 'Landeshauptstadt']:
        identitaet_score += 2
    
    # Praktikabilität Score (max 25)
    praktikabilitaet_score = 15
    if 50000 <= row['Einwohner'] <= 200000:
        praktikabilitaet_score += 5
    elif row['Einwohner'] < 50000:
        praktikabilitaet_score += 3
    
    scores = {
        'medien': max(5, min(25, int(medien_score))),
        'zielgruppe': max(5, min(25, int(zielgruppe_score))),
        'digital': max(5, min(25, int(digital_score))),
        'wirtschaft': max(5, min(25, int(wirtschaft_score))),
        'identitaet': max(5, min(25, int(identitaet_score))),
        'praktikabilitaet': max(5, min(25, int(praktikabilitaet_score)))
    }
    
    total = sum(scores.values()) * 4 / 6  # Normalisiere auf 100
    return int(total), scores

def create_city_object(row):
    """Erstelle ein Stadt-Objekt aus einer CSV-Zeile"""
    total_score, scores = calculate_score(row)
    
    return {
        'name': row['Stadt'],
        'bundesland': row['Bundesland'],
        'einwohner': int(row['Einwohner']),
        'kaufkraft': float(row.get('Kaufkraft', 22000)),
        'akademikerquote': float(row.get('Akademikerquote', 25)),
        'lokalzeitungen': int(row.get('Lokalzeitungen', 1)),
        'typ': row.get('Typ', 'Stadt'),
        'openData': bool(row.get('OpenData', False)),
        'funke': bool(row.get('Funke', False)),
        'ippen': bool(row.get('Ippen', False)),
        'madsack': bool(row.get('Madsack', False)),
        'lat': float(row.get('Lat', 51.0)),
        'lng': float(row.get('Lng', 10.0)),
        'scores': scores,
        'score': total_score,
        'description': f"{row.get('Typ', 'Stadt')} mit {int(row['Einwohner']):,} Einwohnern"
    }

def generate_tiered_files(cities):
    """Teile Städte in Tiers und speichere sie"""
    # Sortiere nach Score
    cities.sort(key=lambda x: x['score'], reverse=True)
    
    # Erstelle Verzeichnisse
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/bundeslaender', exist_ok=True)
    
    # Tier 1: Top 50
    tier1 = cities[:50]
    with open('data/cities-core.json', 'w', encoding='utf-8') as f:
        json.dump(tier1, f, ensure_ascii=False, indent=2)
    print(f"✅ data/cities-core.json: {len(tier1)} cities")
    
    # Tier 2: 51-150
    if len(cities) > 50:
        tier2 = cities[50:150]
        with open('data/cities-tier2.json', 'w', encoding='utf-8') as f:
            json.dump(tier2, f, ensure_ascii=False, indent=2)
        print(f"✅ data/cities-tier2.json: {len(tier2)} cities")
    
    # Tier 3: 151+
    if len(cities) > 150:
        tier3 = cities[150:]
        with open('data/cities-tier3.json', 'w', encoding='utf-8') as f:
            json.dump(tier3, f, ensure_ascii=False, indent=2)
        print(f"✅ data/cities-tier3.json: {len(tier3)} cities")
    
    return len(tier1), len(cities[50:150]) if len(cities) > 50 else 0, len(cities[150:]) if len(cities) > 150 else 0

def generate_bundesland_files(cities):
    """Gruppiere Städte nach Bundesland und speichere sie"""
    by_state = {}
    for city in cities:
        state = city['bundesland']
        if state not in by_state:
            by_state[state] = []
        by_state[state].append(city)
    
    state_info = []
    for state, state_cities in by_state.items():
        # Sortiere nach Score
        state_cities.sort(key=lambda x: x['score'], reverse=True)
        
        # Erstelle Dateiname
        filename = state.lower().replace(' ', '-').replace('ü', 'ue').replace('ä', 'ae').replace('ö', 'oe')
        filepath = f'data/bundeslaender/{filename}.json'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state_cities, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {filepath}: {len(state_cities)} cities")
        state_info.append({
            'name': state,
            'file': filepath,
            'cities': len(state_cities)
        })
    
    return state_info

def generate_config(total_cities, tier_counts, state_info):
    """Generiere die Konfigurations-Datei"""
    config = {
        'version': '2.0',
        'lastUpdate': datetime.now().strftime('%Y-%m-%d'),
        'totalCities': total_cities,
        'dataSources': {
            'core': {
                'file': 'data/cities-core.json',
                'cities': tier_counts[0],
                'loadOnStart': True
            },
            'tier2': {
                'file': 'data/cities-tier2.json',
                'cities': tier_counts[1],
                'loadOnStart': False
            },
            'tier3': {
                'file': 'data/cities-tier3.json',
                'cities': tier_counts[2],
                'loadOnStart': False
            }
        },
        'bundeslaender': sorted(state_info, key=lambda x: x['name'])
    }
    
    with open('cities-config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ cities-config.json generated")
    return config

def generate_complete_file(cities):
    """Generiere auch eine komplette Datei als Fallback"""
    cities.sort(key=lambda x: x['score'], reverse=True)
    
    with open('data/cities-complete.json', 'w', encoding='utf-8') as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)
    
    print(f"✅ data/cities-complete.json: {len(cities)} cities (fallback)")

def main():
    print("🚀 Starting JSON generation...")
    
    # Lade CSV
    df = load_master_csv()
    
    # Konvertiere zu Stadt-Objekten
    cities = []
    for _, row in df.iterrows():
        try:
            city = create_city_object(row)
            cities.append(city)
        except Exception as e:
            print(f"⚠️ Error processing {row.get('Stadt', 'Unknown')}: {e}")
            continue
    
    print(f"\n📊 Processed {len(cities)} cities")
    
    # Generiere Dateien
    tier_counts = generate_tiered_files(cities)
    state_info = generate_bundesland_files(cities)
    config = generate_config(len(cities), tier_counts, state_info)
    generate_complete_file(cities)
    
    # Statistiken
    print("\n📈 Statistics:")
    print(f"   Total cities: {len(cities)}")
    print(f"   Average score: {sum(c['score'] for c in cities) / len(cities):.1f}")
    print(f"   Top cities (75+): {len([c for c in cities if c['score'] >= 75])}")
    print(f"   States covered: {len(state_info)}")
    
    # Top 5
    print("\n🏆 Top 5 cities:")
    for i, city in enumerate(cities[:5], 1):
        print(f"   {i}. {city['name']}: {city['score']} points")

if __name__ == '__main__':
    main()
