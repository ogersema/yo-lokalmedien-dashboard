import pandas as pd
import json

# Load Sachsen-Anhalt cities
df = pd.read_csv('sachsen-anhalt-staedte.csv')

# Calculate scores for each city
cities = []
for idx, row in df.iterrows():
    # Calculate individual scores
    medien_score = 22  # Base score for cities without major publishers
    if row['DuMont']:
        medien_score -= 3
    if row['Lokalzeitungen'] >= 2:
        medien_score -= 3
        
    zielgruppe_score = min(20, 5 + (row['Akademikerquote'] / 3) + ((row['Kaufkraft'] - 18000) / 1000))
    digital_score = 12 if row['OpenData'] else 8
    digital_score += min(8, row['SmartCityIndex'] / 10)
    
    wirtschaft_score = min(20, 10 + (row['BIP_Mio'] / 1000))
    identitaet_score = min(20, 10 + (row['Kultureinrichtungen'] / 5) + (row['Vereine'] / 50))
    praktikabilitaet_score = 18 if row['Einwohner'] < 100000 else 15
    
    total_score = int((medien_score + zielgruppe_score + digital_score + wirtschaft_score + identitaet_score + praktikabilitaet_score) * 0.667)
    
    city = {
        'name': row['Stadt'],
        'bundesland': 'Sachsen-Anhalt',
        'einwohner': int(row['Einwohner']),
        'kaufkraft': float(row['Kaufkraft']),
        'akademikerquote': float(row['Akademikerquote']),
        'lokalzeitungen': int(row['Lokalzeitungen']),
        'typ': 'Landeshauptstadt' if 'Magdeburg' in row['Stadt'] else 'Stadt',
        'openData': bool(row['OpenData']),
        'funke': False,
        'ippen': False,
        'madsack': False,
        'dumont': bool(row['DuMont']),
        'lat': float(row['Lat']),
        'lng': float(row['Lng']),
        'scores': {
            'medien': int(medien_score),
            'zielgruppe': int(zielgruppe_score),
            'digital': int(digital_score),
            'wirtschaft': int(wirtschaft_score),
            'identitaet': int(identitaet_score),
            'praktikabilitaet': int(praktikabilitaet_score)
        },
        'score': total_score,
        'description': f"{'Landeshauptstadt' if 'Magdeburg' in row['Stadt'] else 'Stadt'} mit {int(row['Einwohner']):,} Einwohnern in Sachsen-Anhalt"
    }
    cities.append(city)

# Sort by score
cities.sort(key=lambda x: x['score'], reverse=True)

# Print results
print(f"✅ {len(cities)} Städte in Sachsen-Anhalt verarbeitet")
print(f"\n📊 Top 5 Städte:")
for i, city in enumerate(cities[:5], 1):
    print(f"   {i}. {city['name']}: {city['score']} Punkte")

# Save as JSON
with open('sachsen-anhalt-cities.json', 'w', encoding='utf-8') as f:
    json.dump(cities, f, ensure_ascii=False, indent=2)
    
print(f"\n✅ Datei 'sachsen-anhalt-cities.json' erstellt")