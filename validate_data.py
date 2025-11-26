#!/usr/bin/env python3
"""
validate_data.py
Validiert die Datenintegrität und prüft auf Fehler
"""

import pandas as pd
import json
import os
import sys

def validate_data():
    """Validiert alle generierten Daten"""
    
    errors = []
    warnings = []
    
    # 1. Prüfe Master-CSV
    if not os.path.exists('data/cities-master.csv'):
        errors.append("❌ Master-CSV nicht gefunden!")
        return False
    
    df = pd.read_csv('data/cities-master.csv')
    print(f"📋 Validiere {len(df)} Städte...")
    
    # Prüfe Pflichtfelder
    required_fields = ['Stadt', 'Bundesland', 'Einwohner', 'Kaufkraft', 'Lat', 'Lng']
    for field in required_fields:
        if field not in df.columns:
            errors.append(f"❌ Pflichtfeld '{field}' fehlt!")
        elif df[field].isna().any():
            missing_count = df[field].isna().sum()
            warnings.append(f"⚠️ {missing_count} fehlende Werte in '{field}'")
    
    # 2. Prüfe JSON-Dateien
    json_files = [
        'cities-config.json',
        'data/cities-core.json'
    ]
    
    for json_file in json_files:
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        print(f"  ✅ {json_file}: {len(data)} Einträge")
                    elif isinstance(data, dict):
                        print(f"  ✅ {json_file}: Valid config")
            except json.JSONDecodeError as e:
                errors.append(f"❌ {json_file}: Invalid JSON - {e}")
        else:
            warnings.append(f"⚠️ {json_file} nicht gefunden")
    
    # 3. Prüfe Datenqualität
    if len(df) > 0:
        # Score-Verteilung
        if 'Score_Gesamt' in df.columns:
            avg_score = df['Score_Gesamt'].mean()
            if avg_score < 50 or avg_score > 80:
                warnings.append(f"⚠️ Ungewöhnlicher Durchschnittsscore: {avg_score:.1f}")
        
        # Einwohner-Plausibilität
        if df['Einwohner'].min() < 30000:
            warnings.append(f"⚠️ Stadt mit weniger als 30.000 Einwohnern gefunden")
        
        # Duplikate
        duplicates = df[df.duplicated(subset=['Stadt', 'Bundesland'], keep=False)]
        if len(duplicates) > 0:
            errors.append(f"❌ {len(duplicates)} doppelte Städte gefunden!")
    
    # 4. Prüfe Verzeichnisstruktur
    required_dirs = ['data', 'data/bundeslaender', 'scripts']
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            warnings.append(f"⚠️ Verzeichnis '{dir_path}' fehlt")
    
    # Ausgabe
    print("\n" + "="*50)
    print("VALIDIERUNGSERGEBNIS")
    print("="*50)
    
    if errors:
        print("\n❌ FEHLER:")
        for error in errors:
            print(f"  {error}")
        print("\n⛔ Validierung fehlgeschlagen!")
        return False
    
    if warnings:
        print("\n⚠️ WARNUNGEN:")
        for warning in warnings:
            print(f"  {warning}")
    
    print("\n✅ Validierung erfolgreich!")
    print(f"  - {len(df)} Städte validiert")
    print(f"  - Alle Pflichtfelder vorhanden")
    print(f"  - JSON-Dateien gültig")
    
    return True

if __name__ == '__main__':
    success = validate_data()
    sys.exit(0 if success else 1)
