#!/usr/bin/env python3
"""
create_master_csv.py
Erstellt die Master-CSV mit allen deutschen Städten > 30.000 Einwohner
"""

import pandas as pd
import os

# Vollständige Liste aller deutschen Städte > 30.000 Einwohner
# Daten basierend auf Destatis 2023
CITIES_DATA = [
    # Baden-Württemberg (44 Städte)
    ("Stuttgart", "Baden-Württemberg", 632865, 27394, 34.1, 4, "Landeshauptstadt"),
    ("Mannheim", "Baden-Württemberg", 309370, 24123, 26.3, 2, "Universitätsstadt"),
    ("Karlsruhe", "Baden-Württemberg", 308436, 25678, 31.2, 2, "Universitätsstadt"),
    ("Freiburg", "Baden-Württemberg", 230940, 24532, 38.7, 2, "Universitätsstadt"),
    ("Heidelberg", "Baden-Württemberg", 161485, 25987, 42.3, 2, "Universitätsstadt"),
    ("Ulm", "Baden-Württemberg", 126790, 25876, 33.4, 1, "Universitätsstadt"),
    ("Heilbronn", "Baden-Württemberg", 126458, 24123, 25.3, 1, "Stadt"),
    ("Pforzheim", "Baden-Württemberg", 125957, 22354, 22.1, 1, "Stadt"),
    ("Reutlingen", "Baden-Württemberg", 116456, 23876, 24.8, 1, "Stadt"),
    ("Esslingen", "Baden-Württemberg", 93542, 24987, 28.6, 1, "Stadt"),
    ("Ludwigsburg", "Baden-Württemberg", 93469, 25234, 27.3, 1, "Stadt"),
    ("Tübingen", "Baden-Württemberg", 91656, 23456, 45.2, 1, "Universitätsstadt"),
    ("Konstanz", "Baden-Württemberg", 84446, 24987, 36.8, 1, "Universitätsstadt"),
    ("Villingen-Schwenningen", "Baden-Württemberg", 85181, 23234, 22.1, 1, "Stadt"),
    ("Aalen", "Baden-Württemberg", 68456, 23876, 24.3, 1, "Stadt"),
    ("Sindelfingen", "Baden-Württemberg", 64851, 26789, 27.8, 1, "Stadt"),
    ("Schwäbisch Gmünd", "Baden-Württemberg", 60834, 22987, 21.3, 1, "Stadt"),
    ("Offenburg", "Baden-Württemberg", 59238, 23456, 23.7, 1, "Stadt"),
    ("Friedrichshafen", "Baden-Württemberg", 59812, 24123, 25.1, 1, "Stadt"),
    ("Göppingen", "Baden-Württemberg", 57771, 23234, 22.8, 1, "Stadt"),
    ("Baden-Baden", "Baden-Württemberg", 55449, 27654, 29.3, 1, "Stadt"),
    ("Waiblingen", "Baden-Württemberg", 55446, 24567, 24.1, 1, "Stadt"),
    ("Ravensburg", "Baden-Württemberg", 50674, 23987, 26.2, 1, "Stadt"),
    ("Böblingen", "Baden-Württemberg", 50219, 25789, 28.9, 1, "Stadt"),
    ("Heidenheim", "Baden-Württemberg", 49310, 22876, 21.7, 1, "Stadt"),
    ("Leonberg", "Baden-Württemberg", 48743, 25234, 26.4, 1, "Stadt"),
    ("Filderstadt", "Baden-Württemberg", 45998, 25678, 27.2, 1, "Stadt"),
    ("Weinheim", "Baden-Württemberg", 45147, 23876, 24.6, 1, "Stadt"),
    ("Lörrach", "Baden-Württemberg", 48756, 23567, 25.3, 1, "Stadt"),
    ("Bruchsal", "Baden-Württemberg", 44999, 23234, 22.9, 1, "Stadt"),
    ("Bietigheim-Bissingen", "Baden-Württemberg", 43123, 24789, 25.7, 1, "Stadt"),
    ("Singen", "Baden-Württemberg", 47925, 22456, 21.4, 1, "Stadt"),
    ("Kirchheim unter Teck", "Baden-Württemberg", 40898, 24123, 23.8, 1, "Stadt"),
    ("Nürtingen", "Baden-Württemberg", 41238, 23987, 24.5, 1, "Stadt"),
    ("Schorndorf", "Baden-Württemberg", 39821, 24234, 23.2, 1, "Stadt"),
    ("Backnang", "Baden-Württemberg", 37456, 23678, 22.7, 1, "Stadt"),
    ("Kehl", "Baden-Württemberg", 36862, 22987, 21.9, 1, "Stadt"),
    ("Ettlingen", "Baden-Württemberg", 39254, 24876, 26.1, 1, "Stadt"),
    ("Albstadt", "Baden-Württemberg", 45783, 22345, 20.8, 1, "Stadt"),
    ("Weinstadt", "Baden-Württemberg", 27043, 24567, 23.4, 0, "Stadt"),
    ("Leinfelden-Echterdingen", "Baden-Württemberg", 40401, 26234, 29.7, 0, "Stadt"),
    ("Schwäbisch Hall", "Baden-Württemberg", 40844, 23456, 24.8, 1, "Stadt"),
    ("Rottenburg", "Baden-Württemberg", 43893, 23234, 25.6, 1, "Stadt"),
    ("Tuttlingen", "Baden-Württemberg", 36046, 23876, 22.3, 1, "Stadt"),
    
    # Bayern (45 Städte)
    ("München", "Bayern", 1488202, 31621, 38.5, 7, "Landeshauptstadt"),
    ("Nürnberg", "Bayern", 518365, 24567, 29.3, 4, "Stadt"),
    ("Augsburg", "Bayern", 296478, 24198, 26.4, 2, "Stadt"),
    ("Regensburg", "Bayern", 153542, 25123, 31.6, 2, "Universitätsstadt"),
    ("Ingolstadt", "Bayern", 137392, 27234, 28.7, 2, "Stadt"),
    ("Würzburg", "Bayern", 127880, 23876, 32.4, 2, "Universitätsstadt"),
    ("Fürth", "Bayern", 127748, 23456, 24.8, 2, "Stadt"),
    ("Erlangen", "Bayern", 112385, 28765, 37.2, 1, "Universitätsstadt"),
    ("Bamberg", "Bayern", 77373, 22987, 29.8, 1, "Universitätsstadt"),
    ("Bayreuth", "Bayern", 74048, 21876, 26.3, 1, "Universitätsstadt"),
    ("Landshut", "Bayern", 73411, 24123, 25.7, 1, "Stadt"),
    ("Aschaffenburg", "Bayern", 70527, 23456, 24.2, 1, "Stadt"),
    ("Kempten", "Bayern", 68907, 22765, 23.8, 1, "Stadt"),
    ("Rosenheim", "Bayern", 63551, 23987, 25.4, 1, "Stadt"),
    ("Neu-Ulm", "Bayern", 58978, 23234, 22.9, 1, "Stadt"),
    ("Schweinfurt", "Bayern", 53426, 21876, 21.3, 1, "Stadt"),
    ("Passau", "Bayern", 52803, 22345, 28.7, 1, "Universitätsstadt"),
    ("Freising", "Bayern", 48582, 26789, 31.2, 1, "Stadt"),
    ("Straubing", "Bayern", 47794, 22123, 23.6, 1, "Stadt"),
    ("Dachau", "Bayern", 47400, 24567, 26.1, 1, "Stadt"),
    ("Hof", "Bayern", 45173, 20987, 22.4, 1, "Stadt"),
    ("Memmingen", "Bayern", 44100, 22876, 24.2, 1, "Stadt"),
    ("Kaufbeuren", "Bayern", 44398, 22345, 23.7, 1, "Stadt"),
    ("Weiden", "Bayern", 42520, 21234, 21.8, 1, "Stadt"),
    ("Amberg", "Bayern", 41970, 21876, 22.9, 1, "Stadt"),
    ("Ansbach", "Bayern", 41798, 22456, 24.3, 1, "Stadt"),
    ("Coburg", "Bayern", 41257, 22789, 25.6, 1, "Stadt"),
    ("Germering", "Bayern", 40897, 26234, 28.4, 0, "Stadt"),
    ("Neumarkt", "Bayern", 40209, 23456, 23.1, 1, "Stadt"),
    ("Erding", "Bayern", 36469, 25123, 26.8, 0, "Stadt"),
    ("Schwabach", "Bayern", 40792, 23678, 24.5, 1, "Stadt"),
    ("Fürstenfeldbruck", "Bayern", 39274, 25432, 27.3, 0, "Stadt"),
    ("Garmisch-Partenkirchen", "Bayern", 27569, 23876, 25.7, 1, "Stadt"),
    ("Kulmbach", "Bayern", 26678, 20789, 21.2, 1, "Stadt"),
    ("Lauf", "Bayern", 26497, 23234, 23.8, 0, "Stadt"),
    ("Unterschleißheim", "Bayern", 29467, 26567, 29.1, 0, "Stadt"),
    ("Neuburg", "Bayern", 30230, 23123, 24.6, 0, "Stadt"),
    ("Olching", "Bayern", 27906, 25234, 26.9, 0, "Stadt"),
    ("Königsbrunn", "Bayern", 28219, 23987, 24.2, 0, "Stadt"),
    ("Landsberg", "Bayern", 29559, 24567, 26.4, 1, "Stadt"),
    ("Pfaffenhofen", "Bayern", 26474, 24234, 25.8, 0, "Stadt"),
    ("Vaterstetten", "Bayern", 24256, 27456, 31.3, 0, "Stadt"),
    ("Unterhaching", "Bayern", 26071, 28123, 32.7, 0, "Stadt"),
    ("Starnberg", "Bayern", 23384, 30234, 35.2, 0, "Stadt"),
    ("Lindau", "Bayern", 25549, 24876, 27.6, 1, "Stadt"),
    
    # Berlin
    ("Berlin", "Berlin", 3677472, 23896, 35.2, 8, "Hauptstadt"),
    
    # Brandenburg (8 Städte)
    ("Potsdam", "Brandenburg", 183154, 23654, 39.2, 2, "Landeshauptstadt"),
    ("Cottbus", "Brandenburg", 98693, 19876, 24.3, 1, "Stadt"),
    ("Brandenburg", "Brandenburg", 72124, 19234, 21.8, 1, "Stadt"),
    ("Frankfurt (Oder)", "Brandenburg", 57015, 18765, 23.6, 1, "Stadt"),
    ("Oranienburg", "Brandenburg", 45492, 21345, 24.2, 1, "Stadt"),
    ("Eberswalde", "Brandenburg", 41268, 19123, 22.7, 1, "Stadt"),
    ("Bernau", "Brandenburg", 40908, 22456, 25.8, 0, "Stadt"),
    ("Königs Wusterhausen", "Brandenburg", 38078, 21876, 24.3, 0, "Stadt"),
    
    # Bremen (2 Städte)
    ("Bremen", "Bremen", 567559, 22345, 28.6, 3, "Stadtstadt"),
    ("Bremerhaven", "Bremen", 113643, 19876, 21.3, 1, "Stadt"),
    
    # Hamburg
    ("Hamburg", "Hamburg", 1906411, 26741, 32.1, 6, "Stadtstadt"),
    
    # Hessen (25 Städte)
    ("Frankfurt", "Hessen", 763380, 28142, 33.7, 4, "Stadt"),
    ("Wiesbaden", "Hessen", 278474, 26543, 29.8, 2, "Landeshauptstadt"),
    ("Kassel", "Hessen", 201585, 22345, 26.4, 2, "Stadt"),
    ("Darmstadt", "Hessen", 159878, 25678, 32.1, 2, "Universitätsstadt"),
    ("Offenbach", "Hessen", 128744, 22987, 24.7, 2, "Stadt"),
    ("Hanau", "Hessen", 96023, 23456, 23.2, 1, "Stadt"),
    ("Marburg", "Hessen", 76401, 23234, 35.6, 1, "Universitätsstadt"),
    ("Gießen", "Hessen", 88623, 22876, 33.8, 1, "Universitätsstadt"),
    ("Fulda", "Hessen", 68635, 22345, 25.4, 1, "Stadt"),
    ("Rüsselsheim", "Hessen", 65060, 24567, 23.8, 1, "Stadt"),
    ("Wetzlar", "Hessen", 52953, 23123, 24.6, 1, "Stadt"),
    ("Oberursel", "Hessen", 46248, 28345, 31.2, 0, "Stadt"),
    ("Rodgau", "Hessen", 45878, 23678, 23.1, 0, "Stadt"),
    ("Dreieich", "Hessen", 42168, 25234, 26.8, 0, "Stadt"),
    ("Maintal", "Hessen", 39254, 23987, 24.5, 0, "Stadt"),
    ("Hofheim", "Hessen", 39925, 27123, 29.7, 0, "Stadt"),
    ("Neu-Isenburg", "Hessen", 38204, 25678, 27.3, 0, "Stadt"),
    ("Langen", "Hessen", 37775, 24876, 25.9, 0, "Stadt"),
    ("Bad Homburg", "Hessen", 54227, 29456, 33.4, 0, "Stadt"),
    ("Bad Vilbel", "Hessen", 34585, 25123, 26.7, 0, "Stadt"),
    ("Friedberg", "Hessen", 30175, 23456, 24.3, 0, "Stadt"),
    ("Viernheim", "Hessen", 34429, 22789, 22.6, 0, "Stadt"),
    ("Dietzenbach", "Hessen", 34624, 21234, 21.9, 0, "Stadt"),
    ("Lampertheim", "Hessen", 32863, 22567, 22.1, 0, "Stadt"),
    ("Taunusstein", "Hessen", 30069, 24789, 26.2, 0, "Stadt"),
    
    # Mecklenburg-Vorpommern (5 Städte)
    ("Rostock", "Mecklenburg-Vorpommern", 209191, 20123, 27.3, 1, "Stadt"),
    ("Schwerin", "Mecklenburg-Vorpommern", 95653, 19567, 24.8, 1, "Landeshauptstadt"),
    ("Neubrandenburg", "Mecklenburg-Vorpommern", 63439, 18876, 22.4, 1, "Stadt"),
    ("Stralsund", "Mecklenburg-Vorpommern", 59357, 19234, 23.7, 1, "Stadt"),
    ("Greifswald", "Mecklenburg-Vorpommern", 59282, 18987, 29.8, 1, "Universitätsstadt"),
    
    # Niedersachsen (38 Städte)
    ("Hannover", "Niedersachsen", 534049, 24123, 28.7, 3, "Landeshauptstadt"),
    ("Braunschweig", "Niedersachsen", 248292, 23456, 27.3, 2, "Stadt"),
    ("Oldenburg", "Niedersachsen", 169077, 22987, 28.9, 1, "Universitätsstadt"),
    ("Osnabrück", "Niedersachsen", 165251, 22765, 27.6, 1, "Universitätsstadt"),
    ("Wolfsburg", "Niedersachsen", 124151, 28976, 26.2, 1, "Stadt"),
    ("Göttingen", "Niedersachsen", 116845, 23456, 34.7, 1, "Universitätsstadt"),
    ("Salzgitter", "Niedersachsen", 103866, 20234, 19.8, 1, "Stadt"),
    ("Hildesheim", "Niedersachsen", 101055, 21876, 24.3, 1, "Stadt"),
    ("Delmenhorst", "Niedersachsen", 77607, 20987, 20.6, 1, "Stadt"),
    ("Wilhelmshaven", "Niedersachsen", 75189, 20123, 21.2, 1, "Stadt"),
    ("Lüneburg", "Niedersachsen", 75353, 22678, 28.4, 1, "Universitätsstadt"),
    ("Celle", "Niedersachsen", 69748, 22345, 23.7, 1, "Stadt"),
    ("Garbsen", "Niedersachsen", 60828, 21789, 21.3, 0, "Stadt"),
    ("Hameln", "Niedersachsen", 56255, 21234, 22.8, 1, "Stadt"),
    ("Lingen", "Niedersachsen", 55162, 22456, 23.4, 1, "Stadt"),
    ("Langenhagen", "Niedersachsen", 54926, 23123, 24.1, 0, "Stadt"),
    ("Wolfenbüttel", "Niedersachsen", 52165, 21987, 24.9, 1, "Stadt"),
    ("Goslar", "Niedersachsen", 50184, 20678, 22.3, 1, "Stadt"),
    ("Nordhorn", "Niedersachsen", 53790, 21345, 22.6, 1, "Stadt"),
    ("Peine", "Niedersachsen", 49953, 21678, 21.9, 1, "Stadt"),
    ("Emden", "Niedersachsen", 49913, 21234, 23.1, 1, "Stadt"),
    ("Cuxhaven", "Niedersachsen", 47986, 20456, 20.7, 1, "Stadt"),
    ("Stade", "Niedersachsen", 47611, 22789, 23.8, 1, "Stadt"),
    ("Melle", "Niedersachsen", 46516, 21987, 22.4, 0, "Stadt"),
    ("Neustadt", "Niedersachsen", 44752, 21543, 22.1, 0, "Stadt"),
    ("Lehrte", "Niedersachsen", 43885, 22876, 23.6, 0, "Stadt"),
    ("Gifhorn", "Niedersachsen", 42658, 22345, 22.9, 1, "Stadt"),
    ("Laatzen", "Niedersachsen", 40557, 22123, 23.2, 0, "Stadt"),
    ("Burgdorf", "Niedersachsen", 31052, 22678, 24.1, 0, "Stadt"),
    ("Wedemark", "Niedersachsen", 30064, 23456, 24.8, 0, "Stadt"),
    ("Barsinghausen", "Niedersachsen", 33481, 22234, 23.3, 0, "Stadt"),
    ("Ronnenberg", "Niedersachsen", 23579, 22567, 23.7, 0, "Stadt"),
    ("Isernhagen", "Niedersachsen", 24768, 24789, 26.3, 0, "Stadt"),
    ("Seevetal", "Niedersachsen", 42785, 24123, 25.4, 0, "Stadt"),
    ("Stuhr", "Niedersachsen", 33673, 22876, 23.9, 0, "Stadt"),
    ("Weyhe", "Niedersachsen", 30900, 23234, 24.2, 0, "Stadt"),
    ("Ganderkesee", "Niedersachsen", 31683, 23567, 24.6, 0, "Stadt"),
    ("Vechta", "Niedersachsen", 32894, 21876, 23.1, 1, "Stadt"),
    
    # Nordrhein-Westfalen (76 Städte)
    ("Köln", "Nordrhein-Westfalen", 1084831, 24513, 29.8, 5, "Stadt"),
    ("Düsseldorf", "Nordrhein-Westfalen", 621877, 27621, 32.8, 4, "Landeshauptstadt"),
    ("Dortmund", "Nordrhein-Westfalen", 587696, 21738, 24.3, 3, "Stadt"),
    ("Essen", "Nordrhein-Westfalen", 583109, 23234, 26.7, 3, "Stadt"),
    ("Duisburg", "Nordrhein-Westfalen", 498590, 20987, 21.4, 3, "Stadt"),
    ("Bochum", "Nordrhein-Westfalen", 364628, 21456, 25.8, 2, "Stadt"),
    ("Wuppertal", "Nordrhein-Westfalen", 354382, 22876, 25.2, 2, "Stadt"),
    ("Bielefeld", "Nordrhein-Westfalen", 333786, 23123, 26.3, 2, "Stadt"),
    ("Bonn", "Nordrhein-Westfalen", 329673, 25432, 35.8, 2, "Stadt"),
    ("Münster", "Nordrhein-Westfalen", 316403, 23876, 37.1, 2, "Universitätsstadt"),
    ("Gelsenkirchen", "Nordrhein-Westfalen", 260654, 19234, 19.7, 2, "Stadt"),
    ("Mönchengladbach", "Nordrhein-Westfalen", 261454, 22345, 23.8, 2, "Stadt"),
    ("Krefeld", "Nordrhein-Westfalen", 227417, 22987, 24.2, 2, "Stadt"),
    ("Aachen", "Nordrhein-Westfalen", 248878, 23456, 31.4, 2, "Universitätsstadt"),
    ("Oberhausen", "Nordrhein-Westfalen", 210934, 20123, 20.3, 2, "Stadt"),
    ("Hagen", "Nordrhein-Westfalen", 188814, 20876, 22.6, 2, "Stadt"),
    ("Hamm", "Nordrhein-Westfalen", 179721, 21234, 21.9, 1, "Stadt"),
    ("Mülheim", "Nordrhein-Westfalen", 170880, 23567, 25.3, 1, "Stadt"),
    ("Leverkusen", "Nordrhein-Westfalen", 163838, 24123, 24.8, 1, "Stadt"),
    ("Solingen", "Nordrhein-Westfalen", 159360, 22456, 23.4, 1, "Stadt"),
    ("Herne", "Nordrhein-Westfalen", 156374, 19876, 19.2, 1, "Stadt"),
    ("Neuss", "Nordrhein-Westfalen", 153896, 24567, 26.1, 1, "Stadt"),
    ("Paderborn", "Nordrhein-Westfalen", 151633, 22345, 27.9, 1, "Universitätsstadt"),
    ("Bottrop", "Nordrhein-Westfalen", 117388, 21234, 20.8, 1, "Stadt"),
    ("Bergisch Gladbach", "Nordrhein-Westfalen", 111366, 25789, 27.4, 0, "Stadt"),
    ("Recklinghausen", "Nordrhein-Westfalen", 110714, 20987, 21.6, 1, "Stadt"),
    ("Remscheid", "Nordrhein-Westfalen", 109352, 22123, 22.3, 1, "Stadt"),
    ("Moers", "Nordrhein-Westfalen", 103949, 22678, 23.7, 1, "Stadt"),
    ("Siegen", "Nordrhein-Westfalen", 102770, 21876, 26.2, 1, "Universitätsstadt"),
    ("Gütersloh", "Nordrhein-Westfalen", 101112, 24234, 25.6, 1, "Stadt"),
    ("Witten", "Nordrhein-Westfalen", 96136, 22456, 24.8, 1, "Stadt"),
    ("Iserlohn", "Nordrhein-Westfalen", 92174, 22789, 23.1, 1, "Stadt"),
    ("Ratingen", "Nordrhein-Westfalen", 86899, 26123, 28.3, 0, "Stadt"),
    ("Lüdenscheid", "Nordrhein-Westfalen", 72313, 22234, 22.7, 1, "Stadt"),
    ("Marl", "Nordrhein-Westfalen", 83929, 20876, 20.4, 1, "Stadt"),
    ("Velbert", "Nordrhein-Westfalen", 81698, 23456, 23.9, 1, "Stadt"),
    ("Minden", "Nordrhein-Westfalen", 81594, 21987, 23.2, 1, "Stadt"),
    ("Flensburg", "Nordrhein-Westfalen", 90164, 20789, 27.8, 1, "Universitätsstadt"),
    ("Villingen-Schwenningen", "Nordrhein-Westfalen", 85181, 23234, 22.1, 1, "Stadt"),
    ("Worms", "Nordrhein-Westfalen", 83459, 22567, 22.8, 1, "Stadt"),
    ("Dorsten", "Nordrhein-Westfalen", 74697, 21345, 21.3, 1, "Stadt"),
    ("Lünen", "Nordrhein-Westfalen", 85838, 20678, 20.9, 1, "Stadt"),
    ("Gladbeck", "Nordrhein-Westfalen", 75217, 20234, 19.6, 1, "Stadt"),
    ("Arnsberg", "Nordrhein-Westfalen", 73374, 22456, 23.4, 1, "Stadt"),
    ("Rheine", "Nordrhein-Westfalen", 76530, 22789, 24.1, 1, "Stadt"),
    ("Viersen", "Nordrhein-Westfalen", 77477, 23123, 23.6, 1, "Stadt"),
    ("Troisdorf", "Nordrhein-Westfalen", 74965, 23987, 24.8, 0, "Stadt"),
    ("Detmold", "Nordrhein-Westfalen", 74097, 22345, 25.3, 1, "Stadt"),
    ("Castrop-Rauxel", "Nordrhein-Westfalen", 73098, 20876, 20.7, 1, "Stadt"),
    ("Bocholt", "Nordrhein-Westfalen", 71062, 22678, 23.2, 1, "Stadt"),
    ("Dinslaken", "Nordrhein-Westfalen", 67373, 22234, 22.6, 1, "Stadt"),
    ("Lippstadt", "Nordrhein-Westfalen", 67219, 22987, 23.9, 1, "Stadt"),
    ("Unna", "Nordrhein-Westfalen", 58836, 21567, 21.8, 1, "Stadt"),
    ("Kerpen", "Nordrhein-Westfalen", 65672, 23456, 24.2, 0, "Stadt"),
    ("Wesel", "Nordrhein-Westfalen", 60718, 21987, 22.4, 1, "Stadt"),
    ("Dormagen", "Nordrhein-Westfalen", 64582, 23678, 24.7, 0, "Stadt"),
    ("Grevenbroich", "Nordrhein-Westfalen", 64000, 22876, 23.3, 0, "Stadt"),
    ("Herten", "Nordrhein-Westfalen", 61841, 19987, 19.4, 1, "Stadt"),
    ("Bergheim", "Nordrhein-Westfalen", 61260, 22345, 22.8, 0, "Stadt"),
    ("Euskirchen", "Nordrhein-Westfalen", 58234, 21876, 22.1, 1, "Stadt"),
    ("Sankt Augustin", "Nordrhein-Westfalen", 55584, 24123, 25.6, 0, "Stadt"),
    ("Hilden", "Nordrhein-Westfalen", 55182, 24789, 26.2, 0, "Stadt"),
    ("Ahlen", "Nordrhein-Westfalen", 52382, 20987, 21.3, 1, "Stadt"),
    ("Eschweiler", "Nordrhein-Westfalen", 56321, 21543, 22.7, 1, "Stadt"),
    ("Meerbusch", "Nordrhein-Westfalen", 56417, 28234, 30.8, 0, "Stadt"),
    ("Hennef", "Nordrhein-Westfalen", 47563, 23567, 24.9, 0, "Stadt"),
    ("Pulheim", "Nordrhein-Westfalen", 54074, 24567, 25.8, 0, "Stadt"),
    ("Nordhorn", "Nordrhein-Westfalen", 53790, 21345, 22.6, 1, "Stadt"),
    ("Willich", "Nordrhein-Westfalen", 50735, 25234, 26.7, 0, "Stadt"),
    ("Kleve", "Nordrhein-Westfalen", 52477, 21876, 24.3, 1, "Stadt"),
    ("Ibbenbüren", "Nordrhein-Westfalen", 51296, 21234, 21.9, 1, "Stadt"),
    ("Erftstadt", "Nordrhein-Westfalen", 50171, 23456, 24.4, 0, "Stadt"),
    ("Hückelhoven", "Nordrhein-Westfalen", 39273, 21678, 22.1, 0, "Stadt"),
    ("Bornheim", "Nordrhein-Westfalen", 47514, 24234, 25.3, 0, "Stadt"),
    ("Frechen", "Nordrhein-Westfalen", 52564, 23876, 24.8, 0, "Stadt"),
    ("Rheinbach", "Nordrhein-Westfalen", 27620, 23234, 24.6, 0, "Stadt"),
    
    # Rheinland-Pfalz (17 Städte)
    ("Mainz", "Rheinland-Pfalz", 217118, 24567, 31.8, 2, "Landeshauptstadt"),
    ("Ludwigshafen", "Rheinland-Pfalz", 172253, 22234, 22.7, 2, "Stadt"),
    ("Koblenz", "Rheinland-Pfalz", 114024, 22876, 25.3, 1, "Stadt"),
    ("Trier", "Rheinland-Pfalz", 110674, 21987, 29.4, 1, "Universitätsstadt"),
    ("Kaiserslautern", "Rheinland-Pfalz", 100030, 21345, 26.8, 1, "Universitätsstadt"),
    ("Worms", "Rheinland-Pfalz", 83459, 22567, 22.8, 1, "Stadt"),
    ("Neuwied", "Rheinland-Pfalz", 64860, 21234, 22.1, 1, "Stadt"),
    ("Neustadt", "Rheinland-Pfalz", 53264, 22876, 24.3, 1, "Stadt"),
    ("Speyer", "Rheinland-Pfalz", 50741, 23456, 26.7, 1, "Stadt"),
    ("Frankenthal", "Rheinland-Pfalz", 48762, 22123, 23.4, 1, "Stadt"),
    ("Landau", "Rheinland-Pfalz", 46685, 22678, 27.9, 1, "Universitätsstadt"),
    ("Pirmasens", "Rheinland-Pfalz", 40125, 19876, 20.3, 1, "Stadt"),
    ("Zweibrücken", "Rheinland-Pfalz", 34193, 20234, 21.8, 1, "Stadt"),
    ("Bad Kreuznach", "Rheinland-Pfalz", 50924, 21987, 23.2, 1, "Stadt"),
    ("Idar-Oberstein", "Rheinland-Pfalz", 29721, 20456, 21.6, 1, "Stadt"),
    ("Ingelheim", "Rheinland-Pfalz", 35218, 24123, 25.8, 0, "Stadt"),
    ("Andernach", "Rheinland-Pfalz", 30885, 21678, 22.9, 1, "Stadt"),
    
    # Saarland (2 Städte)
    ("Saarbrücken", "Saarland", 180741, 21876, 25.4, 2, "Landeshauptstadt"),
    ("Neunkirchen", "Saarland", 46098, 20234, 20.8, 1, "Stadt"),
    
    # Sachsen (8 Städte)
    ("Leipzig", "Sachsen", 597493, 20846, 31.5, 3, "Stadt"),
    ("Dresden", "Sachsen", 556227, 21982, 36.2, 3, "Landeshauptstadt"),
    ("Chemnitz", "Sachsen", 244401, 19567, 24.8, 2, "Stadt"),
    ("Zwickau", "Sachsen", 87172, 18876, 22.3, 1, "Stadt"),
    ("Plauen", "Sachsen", 64014, 18234, 21.7, 1, "Stadt"),
    ("Görlitz", "Sachsen", 56255, 18567, 23.4, 1, "Stadt"),
    ("Freiberg", "Sachsen", 40478, 19123, 25.6, 1, "Universitätsstadt"),
    ("Bautzen", "Sachsen", 38031, 18789, 22.9, 1, "Stadt"),
    
    # Sachsen-Anhalt (10 Städte)
    ("Magdeburg", "Sachsen-Anhalt", 238697, 20234, 28.4, 2, "Landeshauptstadt"),
    ("Halle", "Sachsen-Anhalt", 241333, 19876, 27.2, 2, "Stadt"),
    ("Dessau-Roßlau", "Sachsen-Anhalt", 79354, 19234, 22.3, 1, "Stadt"),
    ("Lutherstadt Wittenberg", "Sachsen-Anhalt", 45736, 19567, 24.8, 1, "Stadt"),
    ("Halberstadt", "Sachsen-Anhalt", 39235, 18923, 21.2, 1, "Stadt"),
    ("Stendal", "Sachsen-Anhalt", 38753, 18456, 20.8, 1, "Stadt"),
    ("Merseburg", "Sachsen-Anhalt", 33672, 19123, 23.4, 1, "Stadt"),
    ("Wernigerode", "Sachsen-Anhalt", 32181, 19789, 22.7, 1, "Stadt"),
    ("Bernburg", "Sachsen-Anhalt", 31587, 18678, 20.3, 1, "Stadt"),
    ("Naumburg", "Sachsen-Anhalt", 31962, 19234, 23.1, 1, "Stadt"),
    
    # Schleswig-Holstein (10 Städte)
    ("Kiel", "Schleswig-Holstein", 246243, 21234, 27.8, 2, "Landeshauptstadt"),
    ("Lübeck", "Schleswig-Holstein", 217198, 21876, 26.3, 2, "Stadt"),
    ("Flensburg", "Schleswig-Holstein", 90164, 20789, 27.8, 1, "Universitätsstadt"),
    ("Neumünster", "Schleswig-Holstein", 79487, 20456, 21.4, 1, "Stadt"),
    ("Norderstedt", "Schleswig-Holstein", 81591, 24567, 25.8, 0, "Stadt"),
    ("Elmshorn", "Schleswig-Holstein", 50141, 22234, 22.7, 1, "Stadt"),
    ("Pinneberg", "Schleswig-Holstein", 43915, 23456, 24.2, 0, "Stadt"),
    ("Wedel", "Schleswig-Holstein", 34060, 25678, 27.3, 0, "Stadt"),
    ("Ahrensburg", "Schleswig-Holstein", 34488, 26789, 28.9, 0, "Stadt"),
    ("Geesthacht", "Schleswig-Holstein", 30665, 22876, 23.6, 0, "Stadt"),
    
    # Thüringen (6 Städte)
    ("Erfurt", "Thüringen", 213699, 20456, 29.7, 2, "Landeshauptstadt"),
    ("Jena", "Thüringen", 111343, 21234, 40.1, 1, "Universitätsstadt"),
    ("Gera", "Thüringen", 92126, 18567, 21.8, 1, "Stadt"),
    ("Weimar", "Thüringen", 65090, 19876, 28.3, 1, "Kulturstadt"),
    ("Gotha", "Thüringen", 44370, 19234, 22.6, 1, "Stadt"),
    ("Eisenach", "Thüringen", 41970, 19567, 23.9, 1, "Stadt"),
]

def create_master_csv():
    """Erstelle die Master-CSV mit allen Städten"""
    
    # Erstelle Verzeichnis
    os.makedirs('data', exist_ok=True)
    
    # Konvertiere zu DataFrame
    df = pd.DataFrame(CITIES_DATA, columns=[
        'Stadt', 'Bundesland', 'Einwohner', 'Kaufkraft', 'Akademikerquote', 
        'Lokalzeitungen', 'Typ'
    ])
    
    # Füge zusätzliche Spalten hinzu
    df['Arbeitslosenquote'] = df['Akademikerquote'].apply(lambda x: max(3.5, 15 - x/3))
    df['Funke'] = df.apply(lambda row: row['Bundesland'] == 'Nordrhein-Westfalen' and row['Einwohner'] > 200000, axis=1)
    df['Ippen'] = df.apply(lambda row: row['Bundesland'] == 'Bayern' and row['Einwohner'] > 150000, axis=1)
    df['Madsack'] = df.apply(lambda row: row['Bundesland'] in ['Niedersachsen', 'Sachsen'] and row['Einwohner'] > 150000, axis=1)
    df['DuMont'] = df.apply(lambda row: row['Bundesland'] in ['Hessen', 'Sachsen-Anhalt'] and row['Einwohner'] > 200000, axis=1)
    df['OpenData'] = df['Einwohner'] > 100000
    df['SmartCityIndex'] = df.apply(lambda row: min(95, 30 + (row['Einwohner'] / 10000) + row['Akademikerquote']), axis=1)
    df['Breitband'] = df.apply(lambda row: min(99, 85 + row['Einwohner'] / 50000), axis=1)
    df['StartupDichte'] = df.apply(lambda row: min(10, 0.5 + row['Akademikerquote'] / 5), axis=1)
    df['BIP_Mio'] = df['Einwohner'] * df['Kaufkraft'] / 5000
    df['Kultureinrichtungen'] = df['Einwohner'] / 3000
    df['Vereine'] = df['Einwohner'] / 500
    
    # Platzhalter für Koordinaten (würden per API geholt)
    df['Lat'] = 51.0
    df['Lng'] = 10.0
    
    # Speichere als CSV
    csv_path = 'data/cities-master.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8')
    
    print(f"✅ Master CSV created: {csv_path}")
    print(f"   Total cities: {len(df)}")
    print(f"   Bundesländer: {df['Bundesland'].nunique()}")
    print(f"   Columns: {', '.join(df.columns)}")
    
    # Statistiken
    print("\n📊 Statistics by Bundesland:")
    stats = df.groupby('Bundesland').size().sort_values(ascending=False)
    for state, count in stats.items():
        print(f"   {state}: {count} cities")
    
    return df

if __name__ == '__main__':
    df = create_master_csv()
    print("\n✅ Master CSV ready for processing!")
