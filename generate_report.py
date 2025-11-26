#!/usr/bin/env python3
"""
generate_report.py
Generiert einen Update-Report in Markdown
"""

import pandas as pd
import json
import os
from datetime import datetime

def generate_report():
    """Generiert einen detaillierten Update-Report"""
    
    # Lade Daten
    df = pd.read_csv('data/cities-master.csv')
    
    # Report Header
    report = f"""# 📊 City Dashboard Update Report
    
**Datum:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
**Städte gesamt:** {len(df)}
**Bundesländer:** {df['Bundesland'].nunique()}

## 📈 Statistiken

### Score-Verteilung
- **Durchschnitt:** {df['Score_Gesamt'].mean():.1f}
- **Top-Städte (75+):** {len(df[df['Score_Gesamt'] >= 75])}
- **Mittlere (60-74):** {len(df[(df['Score_Gesamt'] >= 60) & (df['Score_Gesamt'] < 75)])}
- **Niedrige (<60):** {len(df[df['Score_Gesamt'] < 60])}

### 🏆 Top 10 Städte
"""
    
    # Top 10
    top10 = df.nlargest(10, 'Score_Gesamt')
    for idx, (_, row) in enumerate(top10.iterrows(), 1):
        report += f"{idx}. **{row['Stadt']}** ({row['Bundesland']}): {row['Score_Gesamt']:.0f} Punkte\n"
    
    # Bundesländer-Statistik
    report += "\n### 📍 Städte nach Bundesland\n"
    by_state = df.groupby('Bundesland').agg({
        'Stadt': 'count',
        'Score_Gesamt': 'mean'
    }).sort_values('Stadt', ascending=False)
    
    for state, data in by_state.iterrows():
        report += f"- **{state}:** {data['Stadt']:.0f} Städte (⌀ Score: {data['Score_Gesamt']:.1f})\n"
    
    # Medienwettbewerb
    report += "\n### 📰 Medienwettbewerb\n"
    without_publisher = df[~(df['Funke'] | df['Ippen'] | df['Madsack'] | df['DuMont'])]
    report += f"- Städte ohne Großverlag: {len(without_publisher)} ({len(without_publisher)/len(df)*100:.1f}%)\n"
    report += f"- Mit Funke: {df['Funke'].sum()}\n"
    report += f"- Mit Ippen: {df['Ippen'].sum()}\n"
    report += f"- Mit Madsack: {df['Madsack'].sum()}\n"
    report += f"- Mit DuMont: {df['DuMont'].sum()}\n"
    
    # Digitalisierung
    report += "\n### 💻 Digitalisierung\n"
    report += f"- Städte mit Open Data: {df['OpenData'].sum()} ({df['OpenData'].sum()/len(df)*100:.1f}%)\n"
    if 'SmartCityIndex' in df.columns:
        report += f"- Durchschnittlicher Smart City Index: {df['SmartCityIndex'].mean():.1f}\n"
    
    # Größenklassen
    report += "\n### 🏙️ Städte nach Größe\n"
    report += f"- Über 500.000: {len(df[df['Einwohner'] > 500000])} Städte\n"
    report += f"- 200.000-500.000: {len(df[(df['Einwohner'] >= 200000) & (df['Einwohner'] < 500000)])} Städte\n"
    report += f"- 100.000-200.000: {len(df[(df['Einwohner'] >= 100000) & (df['Einwohner'] < 200000)])} Städte\n"
    report += f"- 50.000-100.000: {len(df[(df['Einwohner'] >= 50000) & (df['Einwohner'] < 100000)])} Städte\n"
    report += f"- 30.000-50.000: {len(df[df['Einwohner'] < 50000])} Städte\n"
    
    # Dateien generiert
    report += "\n## 📁 Generierte Dateien\n"
    files_to_check = [
        'cities-config.json',
        'data/cities-core.json',
        'data/cities-tier2.json',
        'data/cities-tier3.json',
        'data/cities-complete.json'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) / 1024
            report += f"- ✅ `{file_path}` ({size:.1f} KB)\n"
        else:
            report += f"- ⚠️ `{file_path}` (nicht generiert)\n"
    
    # Bundesland-Dateien
    bl_dir = 'data/bundeslaender'
    if os.path.exists(bl_dir):
        bl_files = [f for f in os.listdir(bl_dir) if f.endswith('.json')]
        report += f"\n### Bundesland-Dateien\n"
        report += f"- {len(bl_files)} Bundesland-Dateien generiert\n"
    
    # Empfehlungen
    report += "\n## 💡 Empfehlungen\n\n"
    
    # Top Opportunities
    top_opportunities = df[
        (df['Score_Gesamt'] >= 70) & 
        (df['Einwohner'] >= 50000) & 
        (df['Einwohner'] <= 200000) &
        (~(df['Funke'] | df['Ippen'] | df['Madsack']))
    ].nlargest(5, 'Score_Gesamt')
    
    if len(top_opportunities) > 0:
        report += "### 🎯 Top Expansion-Kandidaten\n"
        report += "Städte mit hohem Score, optimaler Größe und ohne Großverlag:\n\n"
        for _, row in top_opportunities.iterrows():
            report += f"- **{row['Stadt']}** ({row['Bundesland']}): Score {row['Score_Gesamt']:.0f}, {row['Einwohner']:,.0f} Einwohner\n"
    
    # Footer
    report += f"\n---\n*Report generiert am {datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}*\n"
    
    # Speichere Report
    with open('update-report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    return report

if __name__ == '__main__':
    generate_report()
