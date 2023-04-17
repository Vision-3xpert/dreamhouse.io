import pandas as pd
import requests
import os
import json

def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))

    geojson_path = os.path.join(base_path, "MTLTieks.geojson")
    with open(geojson_path, 'r') as file:
        Montreal = json.load(file)

    clean_price = []
    clean_bed = []
    clean_bath = []



    superficie_path = os.path.join(base_path, "CSVs/Superficie_quartier.csv")
    superficie = pd.read_csv(superficie_path)

    démographie_path = os.path.join(base_path, "CSVs/demographie.csv")
    démographie = pd.read_csv(démographie_path)
    démo_quartier = pd.merge(superficie,démographie, how="left")


    price_per_piece_path = os.path.join(base_path, "Export/Price_per_piece.csv")
    Price_per_piece = pd.read_csv(price_per_piece_path)

    Rest_per_KM_path = os.path.join(base_path, "Export/Rest_per_KM.csv")
    Rest_per_KM = pd.read_csv(Rest_per_KM_path)

    Communitycenters_path = os.path.join(base_path, "Export/Communitycenters.csv")
    Communitycenters = pd.read_csv(Communitycenters_path)

    houses_path = os.path.join(base_path, "Export/Houses2V1.csv")
    houses = pd.read_csv(houses_path)

    Mairies_path = os.path.join(base_path, "Export/Mairies.csv")
    Mairies = pd.read_csv(Mairies_path)

    Parcs_path = os.path.join(base_path, "Export/Parcs.csv")
    Parcs = pd.read_csv(Parcs_path)

    Sportscenters_path = os.path.join(base_path, "Export/Sportscenters.csv")
    Sportscenters = pd.read_csv(Sportscenters_path)

    houses["beds"] = houses['beds'].fillna(0)
    houses["baths"] = houses['baths'].fillna(0)
    for index, row in houses.iterrows():
        clean_price.append(int(row["price"].replace("\xa0", "").replace(" $", "")))
        if not isinstance(row['beds'], int):
            clean_bed.append(int(row["beds"].split(" ")[0]))
        else:
            clean_bed.append(row['beds'])
        if not isinstance(row['baths'], int):
            clean_bath.append(int(row["baths"].split(" ")[0]))
        else:
            clean_bath.append(row['baths'])

    houses["price"] = clean_price
    houses["beds"] = clean_bed
    houses["baths"] = clean_bath

    demographics = {}
    for i, row in démo_quartier.iterrows():
        age_groups = {
            "0-14": row["0-14"],
            "15-29": row["15-29"],
            "30-59": row["30-59"],
            "60+": row["60+"],
        }
        max_age_group = max(age_groups, key=age_groups.get)
        Superficie_km2 = row["Superficie (km2)"]
        Habitants = row["Habitants"]
        Revenu = row["Revenu median"]
        ville = row['NOM']
        demographics[ville] = [Superficie_km2,Habitants,max_age_group, Revenu]

    test = houses.groupby("NOM").mean(numeric_only=True).round(2)
    my_dict = {i: r[:0 - 2] for i, r in test.iterrows()}
    new_dict = {}
    for ville, scores in my_dict.items():
        new_dict[ville] = {}
        for score_type, score_value in scores.items():
            new_dict[ville][score_type] = score_value

    quartiers_images = {i: f"{i}.jpg" for i, r in test.iterrows()}

    return Montreal, new_dict, quartiers_images, superficie, Price_per_piece, Rest_per_KM, Communitycenters, houses, Mairies, Parcs, Sportscenters, demographics

Montreal, new_dict, quartiers_images,superficie, Price_per_piece, Rest_per_KM, Communitycenters, houses, Mairies, Parcs, Sportscenters, demographics = load_data()

