#!/usr/bin/env python3
"""
Stadt-Dashboard Datenprocessor
Automatisiert die Score-Berechnung für deutsche Städte
"""

import pandas as pd
import json
import math

class StadtScoreCalculator:
    def __init__(self):
        # Gewichtungen für die Kategorien
        self.weights = {
            'medien': 0.167,
            'zielgruppe': 0.167,
            'digital': 0.167,
            'wirtschaft': 0.167,
            'identitaet': 0.167,
            'praktikabilitaet': 0.167
        }
        
    def calculate_medien_score(self, row):
        """Berechnet Medienwettbewerb Score (0-25 Punkte)"""
        score = 25
        
        # Weniger Lokalzeitungen = höherer Score
        zeitungen = row.get('Lokalzeitungen', 0)
        if zeitungen == 0:
            score = 25
        elif zeitungen == 1:
            score -= 3
        elif zeitungen == 2:
            score -= 6
        else:
            score -= min(12, zeitungen * 3)
        
        # Großverlage reduzieren Score
        if row.get('Funke', False):
            score -= 4
        if row.get('Ippen', False):
            score -= 4
        if row.get('Madsack', False):
            score -= 4
        if row.get('DuMont', False):
            score -= 3
            
        return max(5, min(25, score))
    
    def calculate_zielgruppe_score(self, row):
        """Berechnet Zielgruppen Score (0-25 Punkte)"""
        score = 0
        
        # Akademikerquote (max 10 Punkte)
        akademiker = row.get('Akademikerquote', 20)
        score += min(10, (akademiker / 45) * 10)
        
        # Kaufkraft (max 10 Punkte)  
        kaufkraft = row.get('Kaufkraft', 22000)
        score += min(10, ((kaufkraft - 20000) / 12000) * 10)
        
        # Arbeitslosigkeit (max 5 Punkte, niedriger ist besser)
        arbeitslos = row.get('Arbeitslosenquote', 5)
        score += max(0, 5 - (arbeitslos / 2))
        
        return max(5, min(25, score))
    
    def calculate_digital_score(self, row):
        """Berechnet Digital Score (0-25 Punkte)"""
        score = 0
        
        # Open Data (5 Punkte)
        if row.get('OpenData', False):
            score += 5
            
        # Smart City Index (max 10 Punkte)
        smart_city = row.get('SmartCityIndex', 50)
        score += (smart_city / 100) * 10
        
        # Breitband (max 5 Punkte)
        breitband = row.get('Breitband', 90)
        score += (breitband / 100) * 5
        
        # Startup-Dichte (max 5 Punkte)
        startups = row.get('StartupDichte', 2)
        score += min(5, startups)
        
        return max(5, min(25, score))
    
    def calculate_wirtschaft_score(self, row):
        """Berechnet Wirtschaftskraft Score (0-25 Punkte)"""
        score = 0
        
        # BIP (max 15 Punkte)
        bip = row.get('BIP_Mio', 3000)
        score += min(15, (bip / 10000) * 15)
        
        # Kaufkraft als Indikator (max 10 Punkte)
        kaufkraft = row.get('Kaufkraft', 22000)
        score += min(10, ((kaufkraft - 20000) / 10000) * 10)
        
        return max(5, min(25, score))
    
    def calculate_identitaet_score(self, row):
        """Berechnet Lokale Identität Score (0-25 Punkte)"""
        score = 10  # Basiswert
        
        # Kultureinrichtungen (max 8 Punkte)
        kultur = row.get('Kultureinrichtungen', 20)
        score += min(8, (kultur / 50) * 8)
        
        # Vereine (max 7 Punkte)
        vereine = row.get('Vereine', 200)
        score += min(7, (vereine / 400) * 7)
        
        return max(5, min(25, score))
    
    def calculate_praktikabilitaet_score(self, row):
        """Berechnet Praktikabilität Score (0-25 Punkte)"""
        score = 15  # Basiswert für alle Städte über 30k
        
        # Einwohnerzahl (optimal: 50k-200k)
        einwohner = row.get('Einwohner', 50000)
        if 50000 <= einwohner <= 200000:
            score += 5
        elif 30000 <= einwohner < 50000:
            score += 3
        elif 200000 < einwohner <= 500000:
            score += 2
        
        # Open Data als Indikator für Kooperationsbereitschaft
        if row.get('OpenData', False):
            score += 5
            
        return max(5, min(25, score))
    
    def calculate_total_score(self, row):
        """Berechnet den Gesamtscore"""
        scores = {
            'medien': self.calculate_medien_score(row),
            'zielgruppe': self.calculate_zielgruppe_score(row),
            'digital': self.calculate_digital_score(row),
            'wirtschaft': self.calculate_wirtschaft_score(row),
            'identitaet': self.calculate_identitaet_score(row),
            'praktikabilitaet': self.calculate_praktikabilitaet_score(row)
        }
        
        # Gewichtete Summe
        total = sum(scores[key] * 4 for key in scores.keys()) / 6
        
        return round(total), scores

def process_cities_csv(input_file, output_file):
    """Verarbeitet CSV und fügt Scores hinzu"""
    
    calculator = StadtScoreCalculator()
    df = pd.read_csv(input_file)
    
    # Berechne Scores für jede Stadt
    cities_data = []
    
    for idx, row in df.iterrows():
        total_score, category_scores = calculator.calculate_total_score(row)
        
        city = {
            'name': row['Stadt'],
            'bundesland': row['Bundesland'],
            'einwohner': int(row['Einwohner']),
            'kaufkraft': float(row['Kaufkraft']),
            'akademikerquote': float(row['Akademikerquote']),
            'lokalzeitungen': int(row['Lokalzeitungen']),
            'typ': 'Stadt',
            'openData': bool(row.get('OpenData', False)),
            'funke': bool(row.get('Funke', False)),
            'ippen': bool(row.get('Ippen', False)),
            'madsack': bool(row.get('Madsack', False)),
            'lat': float(row['Lat']),
            'lng': float(row['Lng']),
            'scores': category_scores,
            'score': total_score,
            'description': f"Stadt mit {int(row['Einwohner']):,} Einwohnern"
        }
        cities_data.append(city)
    
    # Sortiere nach Score
    cities_data.sort(key=lambda x: x['score'], reverse=True)
    
    # Speichere als JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cities_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(cities_data)} Städte verarbeitet")
    print(f"📊 Top 5 Städte:")
    for i, city in enumerate(cities_data[:5], 1):
        print(f"   {i}. {city['name']}: {city['score']} Punkte")
    
    return cities_data

if __name__ == "__main__":
    # Beispiel-Aufruf
    cities = process_cities_csv('stadt-daten-template.csv', 'cities-output.json')
    
    # Statistiken
    avg_score = sum(c['score'] for c in cities) / len(cities)
    print(f"\n📈 Durchschnittlicher Score: {avg_score:.1f}")
    print(f"🏆 Städte mit Score > 75: {len([c for c in cities if c['score'] > 75])}")
    print(f"📍 Städte ohne Großverlag: {len([c for c in cities if not any([c['funke'], c['ippen'], c['madsack']])])}")
