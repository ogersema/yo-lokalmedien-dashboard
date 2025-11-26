import json

# Load existing 30 cities
with open('/mnt/user-data/outputs/cities-data-complete.json', 'r', encoding='utf-8') as f:
    existing_cities = json.load(f)

# Load new Sachsen-Anhalt cities
with open('sachsen-anhalt-cities.json', 'r', encoding='utf-8') as f:
    sachsen_anhalt_cities = json.load(f)

# Combine all cities
all_cities = existing_cities + sachsen_anhalt_cities

# Sort by score
all_cities.sort(key=lambda x: x['score'], reverse=True)

# Save combined data
with open('cities-data-40.json', 'w', encoding='utf-8') as f:
    json.dump(all_cities, f, ensure_ascii=False, indent=2)

# Statistics
print(f"✅ Kombinierte Datei erstellt mit {len(all_cities)} Städten")
print(f"\n📊 Neue Gesamtstatistik:")
print(f"   Gesamt: {len(all_cities)} Städte")
print(f"   Top-Städte (75+): {len([c for c in all_cities if c['score'] >= 75])}")
print(f"   Mittlere (60-74): {len([c for c in all_cities if 60 <= c['score'] < 75])}")
print(f"   Niedrige (<60): {len([c for c in all_cities if c['score'] < 60])}")

# Bundesländer-Verteilung
bundeslaender = {}
for city in all_cities:
    bl = city['bundesland']
    bundeslaender[bl] = bundeslaender.get(bl, 0) + 1

print(f"\n📍 Verteilung nach Bundesländern:")
for bl, count in sorted(bundeslaender.items(), key=lambda x: x[1], reverse=True):
    print(f"   {bl}: {count} Städte")

print(f"\n🏆 Top 10 Städte:")
for i, city in enumerate(all_cities[:10], 1):
    print(f"   {i}. {city['name']}: {city['score']} Punkte")