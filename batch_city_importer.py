#!/usr/bin/env python3
"""
Batch-Importer für deutsche Städte
Lädt Städte bundeslandweise und generiert modulare JSON-Dateien
"""

import pandas as pd
import json
import os
from typing import Dict, List

# Städte-Listen nach Bundesland (> 30.000 Einwohner)
CITIES_BY_STATE = {
    "Nordrhein-Westfalen": [
        # Große Städte
        ("Essen", 583109, 23234),
        ("Dortmund", 587696, 21738),
        ("Duisburg", 498590, 20987),
        ("Bochum", 364628, 21456),
        ("Wuppertal", 354382, 22876),
        ("Bielefeld", 333786, 23123),
        ("Bonn", 329673, 25432),
        ("Gelsenkirchen", 260654, 19234),
        ("Mönchengladbach", 261454, 22345),
        ("Krefeld", 227417, 22987),
        # Mittlere Städte
        ("Aachen", 248878, 23456),
        ("Oberhausen", 210934, 20123),
        ("Hagen", 188814, 20876),
        ("Hamm", 179721, 21234),
        ("Mülheim", 170880, 23567),
        ("Leverkusen", 163838, 24123),
        ("Solingen", 159360, 22456),
        ("Herne", 156374, 19876),
        ("Neuss", 153896, 24567),
        ("Paderborn", 151633, 22345),
        # ... weitere Städte
    ],
    
    "Bayern": [
        ("Nürnberg", 518365, 24567),
        ("Augsburg", 296478, 24198),
        ("Regensburg", 153542, 25123),
        ("Ingolstadt", 137392, 27234),
        ("Würzburg", 127880, 23876),
        ("Fürth", 127748, 23456),
        ("Erlangen", 112385, 28765),
        ("Bamberg", 77373, 22987),
        ("Bayreuth", 74048, 21876),
        ("Landshut", 73411, 24123),
        ("Aschaffenburg", 70527, 23456),
        ("Kempten", 68907, 22765),
        ("Rosenheim", 63551, 23987),
        ("Neu-Ulm", 58978, 23234),
        ("Schweinfurt", 53426, 21876),
        # ... weitere
    ],
    
    "Niedersachsen": [
        ("Hannover", 534049, 24123),
        ("Braunschweig", 248292, 23456),
        ("Oldenburg", 169077, 22987),
        ("Osnabrück", 165251, 22765),
        ("Wolfsburg", 124151, 28976),
        ("Göttingen", 116845, 23456),
        ("Salzgitter", 103866, 20234),
        ("Hildesheim", 101055, 21876),
        ("Delmenhorst", 77607, 20987),
        ("Wilhelmshaven", 75189, 20123),
        # ... weitere
    ],
    
    "Hessen": [
        ("Frankfurt", 763380, 28142),
        ("Wiesbaden", 278474, 26543),
        ("Kassel", 201585, 22345),
        ("Darmstadt", 159878, 25678),
        ("Offenbach", 128744, 22987),
        ("Hanau", 96023, 23456),
        ("Marburg", 76401, 23234),
        ("Gießen", 88623, 22876),
        ("Fulda", 68635, 22345),
        ("Rüsselsheim", 65060, 24567),
        # ... weitere
    ]
}

class CityBatchImporter:
    def __init__(self):
        self.all_cities = []
        self.processed_states = []
        
    def generate_city_data(self, name: str, state: str, population: int, kaufkraft: float) -> Dict:
        """Generiere vollständige Stadtdaten mit automatischer Score-Berechnung"""
        
        # Basis-Schätzungen basierend auf Stadtgröße
        if population > 500000:
            lokalzeitungen = 5
            akademikerquote = 32.5
            smart_city = 75
        elif population > 200000:
            lokalzeitungen = 3
            akademikerquote = 28.5
            smart_city = 65
        elif population > 100000:
            lokalzeitungen = 2
            akademikerquote = 25.5
            smart_city = 55
        else:
            lokalzeitungen = 1
            akademikerquote = 22.5
            smart_city = 45
            
        # Verlage (vereinfacht - müsste recherchiert werden)
        funke = state == "Nordrhein-Westfalen" and population > 200000
        madsack = state == "Niedersachsen" and population > 150000
        ippen = state == "Bayern" and population > 100000
        
        # Score-Berechnung
        medien_score = 22
        if lokalzeitungen >= 3:
            medien_score -= 6
        elif lokalzeitungen == 2:
            medien_score -= 3
        if funke or madsack or ippen:
            medien_score -= 4
            
        zielgruppe_score = min(22, 10 + (akademikerquote / 3) + ((kaufkraft - 20000) / 1500))
        digital_score = min(20, 10 + (smart_city / 10))
        wirtschaft_score = min(22, 12 + ((kaufkraft - 20000) / 1200))
        identitaet_score = 15  # Basis
        praktikabilitaet_score = 20 if population < 200000 else 17
        
        total_score = int((medien_score + zielgruppe_score + digital_score + 
                          wirtschaft_score + identitaet_score + praktikabilitaet_score) * 0.667)
        
        return {
            "name": name,
            "bundesland": state,
            "einwohner": population,
            "kaufkraft": kaufkraft,
            "akademikerquote": round(akademikerquote, 1),
            "lokalzeitungen": lokalzeitungen,
            "typ": self.get_city_type(name, state, population),
            "openData": population > 100000,  # Vereinfachte Annahme
            "funke": funke,
            "ippen": ippen,
            "madsack": madsack,
            "lat": 51.0,  # Müsste per API geholt werden
            "lng": 10.0,  # Müsste per API geholt werden
            "scores": {
                "medien": int(medien_score),
                "zielgruppe": int(zielgruppe_score),
                "digital": int(digital_score),
                "wirtschaft": int(wirtschaft_score),
                "identitaet": int(identitaet_score),
                "praktikabilitaet": int(praktikabilitaet_score)
            },
            "score": total_score,
            "description": f"{self.get_city_type(name, state, population)} mit {population:,} Einwohnern"
        }
    
    def get_city_type(self, name: str, state: str, population: int) -> str:
        """Bestimme Stadttyp"""
        if name in ["Berlin", "München", "Hamburg"]:
            return "Metropole"
        elif name in ["Düsseldorf", "Stuttgart", "Hannover", "Dresden", "Mainz", 
                      "Wiesbaden", "Schwerin", "Potsdam", "Erfurt", "Magdeburg"]:
            return "Landeshauptstadt"
        elif "Universität" in name or name in ["Heidelberg", "Göttingen", "Marburg", "Tübingen"]:
            return "Universitätsstadt"
        elif population > 500000:
            return "Großstadt"
        elif population > 100000:
            return "Mittelstadt"
        else:
            return "Stadt"
    
    def import_state(self, state_name: str) -> List[Dict]:
        """Importiere alle Städte eines Bundeslands"""
        if state_name not in CITIES_BY_STATE:
            print(f"❌ Keine Daten für {state_name}")
            return []
            
        cities = []
        for city_data in CITIES_BY_STATE[state_name]:
            if len(city_data) >= 3:
                name, population, kaufkraft = city_data[:3]
                city = self.generate_city_data(name, state_name, population, kaufkraft)
                cities.append(city)
                
        self.all_cities.extend(cities)
        self.processed_states.append(state_name)
        
        print(f"✅ {len(cities)} Städte aus {state_name} importiert")
        return cities
    
    def save_tier_files(self):
        """Teile Städte in Tiers auf und speichere sie"""
        # Sortiere nach Score
        self.all_cities.sort(key=lambda x: x['score'], reverse=True)
        
        # Teile in Tiers
        tier1 = self.all_cities[:50]
        tier2 = self.all_cities[50:150] if len(self.all_cities) > 50 else []
        tier3 = self.all_cities[150:] if len(self.all_cities) > 150 else []
        
        # Speichere Dateien
        os.makedirs('data', exist_ok=True)
        
        with open('data/cities-core.json', 'w', encoding='utf-8') as f:
            json.dump(tier1, f, ensure_ascii=False, indent=2)
            print(f"✅ cities-core.json: {len(tier1)} Städte")
            
        if tier2:
            with open('data/cities-tier2.json', 'w', encoding='utf-8') as f:
                json.dump(tier2, f, ensure_ascii=False, indent=2)
                print(f"✅ cities-tier2.json: {len(tier2)} Städte")
                
        if tier3:
            with open('data/cities-tier3.json', 'w', encoding='utf-8') as f:
                json.dump(tier3, f, ensure_ascii=False, indent=2)
                print(f"✅ cities-tier3.json: {len(tier3)} Städte")
    
    def save_state_files(self):
        """Speichere Städte nach Bundesland"""
        os.makedirs('data/bundeslaender', exist_ok=True)
        
        # Gruppiere nach Bundesland
        by_state = {}
        for city in self.all_cities:
            state = city['bundesland']
            if state not in by_state:
                by_state[state] = []
            by_state[state].append(city)
        
        # Speichere jedes Bundesland
        for state, cities in by_state.items():
            filename = state.lower().replace(' ', '-').replace('ü', 'ue').replace('ä', 'ae')
            with open(f'data/bundeslaender/{filename}.json', 'w', encoding='utf-8') as f:
                json.dump(cities, f, ensure_ascii=False, indent=2)
                print(f"✅ {filename}.json: {len(cities)} Städte")
    
    def generate_config(self):
        """Generiere Konfigurations-Datei"""
        config = {
            "version": "2.0",
            "totalCities": len(self.all_cities),
            "lastUpdate": "2024-11-25",
            "dataSources": {
                "core": {
                    "file": "data/cities-core.json",
                    "cities": min(50, len(self.all_cities)),
                    "loadOnStart": True
                },
                "tier2": {
                    "file": "data/cities-tier2.json",
                    "cities": min(100, max(0, len(self.all_cities) - 50)),
                    "loadOnStart": False
                },
                "tier3": {
                    "file": "data/cities-tier3.json",
                    "cities": max(0, len(self.all_cities) - 150),
                    "loadOnStart": False
                }
            },
            "bundeslaender": []
        }
        
        # Füge Bundesländer hinzu
        by_state = {}
        for city in self.all_cities:
            state = city['bundesland']
            by_state[state] = by_state.get(state, 0) + 1
            
        for state, count in sorted(by_state.items()):
            filename = state.lower().replace(' ', '-').replace('ü', 'ue').replace('ä', 'ae')
            config["bundeslaender"].append({
                "name": state,
                "file": f"data/bundeslaender/{filename}.json",
                "cities": count
            })
        
        with open('cities-config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"✅ cities-config.json erstellt")
        
        return config

# Hauptprogramm
if __name__ == "__main__":
    importer = CityBatchImporter()
    
    print("🚀 Starte Batch-Import deutscher Städte\n")
    
    # Importiere ausgewählte Bundesländer
    for state in ["Nordrhein-Westfalen", "Bayern", "Niedersachsen", "Hessen"]:
        importer.import_state(state)
        print(f"   Gesamt bisher: {len(importer.all_cities)} Städte\n")
    
    # Speichere in verschiedenen Formaten
    print("\n📁 Erstelle Ausgabedateien...")
    importer.save_tier_files()
    importer.save_state_files()
    config = importer.generate_config()
    
    # Statistik
    print(f"\n📊 Finale Statistik:")
    print(f"   Gesamt: {len(importer.all_cities)} Städte")
    print(f"   Bundesländer: {len(importer.processed_states)}")
    print(f"   Top-Score: {importer.all_cities[0]['score']} ({importer.all_cities[0]['name']})")
    print(f"   Durchschnitt: {sum(c['score'] for c in importer.all_cities) / len(importer.all_cities):.1f}")
