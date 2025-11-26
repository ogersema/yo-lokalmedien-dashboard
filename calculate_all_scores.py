#!/usr/bin/env python3
"""
calculate_all_scores.py
Berechnet Scores für alle Städte in der Master-CSV
"""

import pandas as pd
import numpy as np

def calculate_scores():
    """Berechnet alle Scores basierend auf der Master-CSV"""
    
    # Lade Master-CSV
    df = pd.read_csv('data/cities-master.csv')
    print(f"📊 Berechne Scores für {len(df)} Städte...")
    
    # Berechne einzelne Score-Komponenten
    for idx, row in df.iterrows():
        # Medien Score (max 25)
        medien = 25
        if row['Lokalzeitungen'] >= 5:
            medien -= 10
        elif row['Lokalzeitungen'] >= 3:
            medien -= 6
        elif row['Lokalzeitungen'] >= 2:
            medien -= 3
        
        if row.get('Funke', False):
            medien -= 3
        if row.get('Ippen', False):
            medien -= 3
        if row.get('Madsack', False):
            medien -= 3
        if row.get('DuMont', False):
            medien -= 2
        
        df.at[idx, 'Score_Medien'] = max(5, min(25, medien))
        
        # Zielgruppe Score (max 25)
        zielgruppe = 0
        zielgruppe += min(12, (row['Akademikerquote'] / 40) * 12)
        zielgruppe += min(13, ((row['Kaufkraft'] - 18000) / 15000) * 13)
        df.at[idx, 'Score_Zielgruppe'] = max(5, min(25, zielgruppe))
        
        # Digital Score (max 25)
        digital = 12
        if row.get('OpenData', False):
            digital += 5
        digital += min(8, (row.get('SmartCityIndex', 50) / 100) * 8)
        df.at[idx, 'Score_Digital'] = max(5, min(25, digital))
        
        # Wirtschaft Score (max 25)
        wirtschaft = 15
        wirtschaft += min(10, ((row['Kaufkraft'] - 20000) / 10000) * 10)
        df.at[idx, 'Score_Wirtschaft'] = max(5, min(25, wirtschaft))
        
        # Identität Score (max 25)
        identitaet = 15
        if row['Einwohner'] < 100000:
            identitaet += 3
        if row.get('Typ', '') in ['Universitätsstadt', 'Landeshauptstadt']:
            identitaet += 2
        df.at[idx, 'Score_Identitaet'] = max(5, min(25, identitaet))
        
        # Praktikabilität Score (max 25)
        praktikabilitaet = 15
        if 50000 <= row['Einwohner'] <= 200000:
            praktikabilitaet += 5
        elif row['Einwohner'] < 50000:
            praktikabilitaet += 3
        df.at[idx, 'Score_Praktikabilitaet'] = max(5, min(25, praktikabilitaet))
        
        # Gesamtscore
        total = (df.at[idx, 'Score_Medien'] + df.at[idx, 'Score_Zielgruppe'] + 
                df.at[idx, 'Score_Digital'] + df.at[idx, 'Score_Wirtschaft'] + 
                df.at[idx, 'Score_Identitaet'] + df.at[idx, 'Score_Praktikabilitaet']) * 4 / 6
        
        df.at[idx, 'Score_Gesamt'] = int(total)
    
    # Sortiere nach Score
    df = df.sort_values('Score_Gesamt', ascending=False)
    
    # Speichere aktualisierte CSV
    df.to_csv('data/cities-master.csv', index=False)
    
    # Statistiken
    print(f"✅ Scores berechnet!")
    print(f"   Durchschnitt: {df['Score_Gesamt'].mean():.1f}")
    print(f"   Top-Städte (75+): {len(df[df['Score_Gesamt'] >= 75])}")
    print(f"   Beste Stadt: {df.iloc[0]['Stadt']} ({df.iloc[0]['Score_Gesamt']})")
    
    return df

if __name__ == '__main__':
    calculate_scores()
