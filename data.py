import pandas as pd
import requests

def load_data():
    quartier_url = 'https://data.montreal.ca/dataset/00bd85eb-23aa-4669-8f1b-ba9a000e3dd8/resource/e9b0f927-8f75-458c-8fda-b5da65cc8b73/download/limadmin.geojson'
    Montreal = []
    clean_price = []
    clean_bed = []
    clean_bath = []

    try:
        r2 = requests.get(quartier_url, timeout=30)
    except requests.exceptions.RequestException as erreur2:
        print(f"Erreur de connexion à l'adresse web suivante {quartier_url} : {erreur2}")
    else:
        if r2.status_code >= 200 and r2.status_code <= 299:
            Montreal = r2.json()
        else:
            print(f"Erreur de connexion à l'adresse web suivante {quartier_url} : erreur {r2.status_code}")

    superficie = pd.read_csv("CSVs/Superficie_quartier.csv")
    Price_per_piece = pd.read_csv("Export/Price_per_piece.csv")
    Rest_per_KM = pd.read_csv("Export/Rest_per_KM.csv")
    Communitycenters = pd.read_csv("Export/Communitycenters.csv")
    houses = pd.read_csv("Export/Houses2V1.csv")
    Mairies = pd.read_csv("Export/Mairies.csv")
    Parcs = pd.read_csv("Export/Parcs.csv")
    Sportscenters = pd.read_csv("Export/Sportscenters.csv")

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

    test = houses.groupby("NOM").mean().round(2)
    my_dict = {i: r[:0 - 2] for i, r in test.iterrows()}
    new_dict = {}
    for ville, scores in my_dict.items():
        new_dict[ville] = {}
        for score_type, score_value in scores.items():
            new_dict[ville][score_type] = score_value

    quartiers_images = {i: f"{i}.jpg" for i, r in test.iterrows()}

    return Montreal, new_dict, quartiers_images,superficie, Price_per_piece, Rest_per_KM, Communitycenters, houses, Mairies, Parcs, Sportscenters

Montreal, new_dict, quartiers_images,superficie, Price_per_piece, Rest_per_KM, Communitycenters, houses, Mairies, Parcs, Sportscenters = load_data()
