
from flask import Flask, render_template, request, session
import pandas as pd
import folium as fl
import requests
from folium.features import GeoJson


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
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/', methods=['GET', 'POST'])
def home():
    sorted_recommandations = []

    if request.method == 'POST':
        cafe_weight = int(request.form['cafe'])
        car_weight = int(request.form['car'])
        walk_weight = int(request.form['walk'])
        park_weight = int(request.form['park'])
        quiet_weight = int(request.form['quiet'])
        cycling_weight = int(request.form['cycling'])
        transit_weight = int(request.form['transit'])
        vibrant_weight = int(request.form['vibrant'])
        daycares_weight = int(request.form['daycares'])
        primary_weight = int(request.form['primary'])
        shopping_weight = int(request.form['shopping'])
        groceries_weight = int(request.form['groceries'])
        nightlife_weight = int(request.form['nightlife'])
        restaurant_weight = int(request.form['restaurant'])
        high_school_weight = int(request.form['high_school'])

        recommandations = {}
        for k, v in new_dict.items():
            scores = {
                'car_score': car_weight * new_dict[k]['car_score'],
                'cafe_score': cafe_weight * new_dict[k]['cafe_score'],
                'walk_score': walk_weight * new_dict[k]['walk_score'],
                'park_score': park_weight * new_dict[k]['park_score'],
                'quiet_score': quiet_weight * new_dict[k]['quiet_score'],
                'cycling_score': cycling_weight * new_dict[k]['cycling_score'],
                'transit_score': transit_weight * new_dict[k]['transit_score'],
                'vibrant_score': vibrant_weight * new_dict[k]['vibrant_score'],
                'daycares_score': daycares_weight * new_dict[k]['daycares_score'],
                'primary_score': primary_weight * new_dict[k]['primary_score'],
                'shopping_score': shopping_weight * new_dict[k]['shopping_score'],
                'groceries_score': groceries_weight * new_dict[k]['groceries_score'],
                'nightlife_score': nightlife_weight * new_dict[k]['nightlife_score'],
                'restaurant_score': restaurant_weight * new_dict[k]['restaurant_score'],
                'high_school_score': high_school_weight * new_dict[k]['high_school_score']
            }

            total_score = round(sum(scores.values()), 1)
            recommandations[k] = [total_score] + list(scores.values())

        sorted_recommandations = sorted(recommandations.items(), key=lambda x: x[1][0], reverse=True)
        price_per_PQ = {row["NOM"]: row["Price_per_piece"] for index, row in Price_per_piece.iterrows()}
        démo = {row["NOM"]: [row["Habitants"], row["Superficie (km2)"]] for index, row in superficie.iterrows()}

        return render_template('result.html', recommendations=sorted_recommandations,
                               cafe_weight=cafe_weight, car_weight=car_weight, quiet_weight=quiet_weight,
                               quartiers_images=quartiers_images, price_piece=price_per_PQ, démo=démo)

    return render_template('form.html')
  

def create_marker(df, icon, color, map):
    for index, row in df.iterrows():
        lat, lon = row['Lat'], row['Lon']
        showcase = fl.Icon(icon=icon, prefix='fa', color=color)
        marker = fl.Marker(location=[lat, lon], icon=showcase)
        popup_html = f'<b>{row["Centre"]}</b><br>{row["Addresse"]}'
        marker.add_child(fl.Popup(popup_html))
        marker.add_to(map)

def filter_dataframe(df, key, value):
    return df[df[key].str.contains(value)] if value else df

def get_request_arg_int(request, arg_name):
    arg_value = request.args.get(arg_name)
    return int(arg_value) if arg_value else None

@app.route('/quartier', methods=["POST", "GET"])
def quartier():
    nom_quartier = "Ville-Marie"

    # Apply filters
    filtered_house = houses.loc[houses['NOM'] == nom_quartier]
    filtered_house = filter_dataframe(filtered_house, 'titre', request.args.get('type'))
    min_price = get_request_arg_int(request, 'min_price')
    max_price = get_request_arg_int(request, 'max_price')
    if min_price and max_price:
        filtered_house = filtered_house[(filtered_house['price'] >= min_price) & (filtered_house['price'] <= max_price)]
    min_bedrooms = get_request_arg_int(request, 'min_bedrooms')
    if min_bedrooms:
        filtered_house = filtered_house[filtered_house['beds'] >= min_bedrooms]
    min_bathrooms = get_request_arg_int(request, 'min_bathrooms')
    if min_bathrooms:
        filtered_house = filtered_house[filtered_house['baths'] >= min_bathrooms]

    # Prepare DataFrames
    Mairie = Mairies.loc[Mairies['NOM'] == nom_quartier].dropna(subset=['Lat', 'Lon'])
    Parc = Parcs.loc[Parcs['NOM'] == nom_quartier].dropna(subset=['Lat', 'Lon'])
    Sportscenter = Sportscenters.loc[Sportscenters['NOM'] == nom_quartier].dropna(subset=['Lat', 'Lon'])
    community = Communitycenters.loc[Communitycenters['NOM'] == nom_quartier].dropna(subset=['Lat', 'Lon'])

    map = fl.Map(location=[45.50884, -73.58781], zoom_start=11)

    # Add markers to the map
    create_marker(community, "book", "orange", map)
    create_marker(Sportscenter, "bicycle", "black", map)
    create_marker(Parc, "tree", "green", map)
    create_marker(Mairie, "flag", "red", map)

    # Your existing code for styling, adding layers, and fitting bounds

    # Add house markers
    for index, row in filtered_house.iterrows():
        html= f"""
        <article class="card" style =" width: 250px; height: 275px; border-radius: 25px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3); overflow: hidden; margin: auto;">
        <div class="thumb" style =" width: auto;height: 50%;"> <img src="{row["image"]}" style="width:100%; height:100%;" alt=""></div>
        <div class="infos" style=" background: #fff; transition: 0.4s 0.15s cubic-bezier(0.17, 0.67, 0.5, 1.03); display: flex flex-direction: column;">
        <div class="details" style="border-bottom: 0.5px solid #d9d9d9; padding: 14px 24px; ">
            <h2 class="title" style=" margin: 5px 0; color: #6a6b6d;font-size: 0.8rem;">{row["titre"]}</h2>
            <h3 class="price" style="   margin: 5px 0; font-size: 2rem; font-weight: 400; margin: 0px 0px; color: #4e958b; cursor: pointer;"> {row["price"]}</h3>
            <h3 class="addresse" style="margin: 5px 0; font-size: 0.8rem; font-weight: 400; color: #4b4444;"> {row["Addresse"]}</h3>
        </div>
        <div class="pieces" style=" display: flex; justify-content: space-around;">
        <div class="flexy" style="display: flex; align-items: center; justify-content: space-evenly;">
        <svg class="icon" style= "width: 25px; height: 25px; padding-right: 10px;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M0 16L3 5V1a1 1 0 0 1 1-1h16a1 1 0 0 1 1 1v4l3 11v5a1 1 0 0 1-1 1v2h-1v-2H2v2H1v-2a1 1 0 0 1-1-1v-5zM19 5h1V1H4v4h1V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1h2V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1zm0 1v2a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1V6h-2v2a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V6H3.76L1.04 16h21.92L20.24 6H19zM1 17v4h22v-4H1zM6 4v4h4V4H6zm8 0v4h4V4h-4z"></path>
        </svg>
        <p><span class="">{row["beds"]}</span> Bedrooms</p>

        </div>
        <div class="flexy" style="display: flex; align-items: center; justify-content: space-evenly;">
        <svg class="icon" style= "width: 25px; height: 25px; padding-right: 10px;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path fill-rule="evenodd" d="M17.03 21H7.97a4 4 0 0 1-1.3-.22l-1.22 2.44-.9-.44 1.22-2.44a4 4 0 0 1-1.38-1.55L.5 11h7.56a4 4 0 0 1 1.78.42l2.32 1.16a4 4 0 0 0 1.78.42h9.56l-2.9 5.79a4 4 0 0 1-1.37 1.55l1.22 2.44-.9.44-1.22-2.44a4 4 0 0 1-1.3.22zM21 11h2.5a.5.5 0 1 1 0 1h-9.06a4.5 4.5 0 0 1-2-.48l-2.32-1.15A3.5 3.5 0 0 0 8.56 10H.5a.5.5 0 0 1 0-1h8.06c.7 0 1.38.16 2 .48l2.32 1.15a3.5 3.5 0 0 0 1.56.37H20V2a1 1 0 0 0-1.74-.67c.64.97.53 2.29-.32 3.14l-.35.36-3.54-3.54.35-.35a2.5 2.5 0 0 1 3.15-.32A2 2 0 0 1 21 2v9zm-5.48-9.65l2 2a1.5 1.5 0 0 0-2-2zm-10.23 17A3 3 0 0 0 7.97 20h9.06a3 3 0 0 0 2.68-1.66L21.88 14h-7.94a5 5 0 0 1-2.23-.53L9.4 12.32A3 3 0 0 0 8.06 12H2.12l3.17 6.34z"></path>
        </svg>
        <p><span class="">{row["baths"]}</span> Bathrooms</p>
        </div>

        </div>
        </div>
        </article>
        """
        lat, lon = row["Lat"], row["Lon"]
        popup = fl.Popup(html=html, max_width=500)
        icon_book = fl.Icon(icon='map-pin', prefix='fa', color='blue')
        fl.Marker(location=[lat, lon], popup=popup, icon=icon_book).add_to(map)

    
    def style_function(feature):
        return {
        'fillOpacity': 0.4,
        'color': 'blue',
        'weight': 2,
        }
    for i in range(len(Montreal["features"])):
        if Montreal["features"][i]['properties']['NOM'] == nom_quartier:
            layer = GeoJson(Montreal["features"][i], style_function=style_function)
            bounds = fl.GeoJson(Montreal["features"][i]).get_bounds()
            map.fit_bounds(bounds, max_zoom=13)
            map.add_child(layer)
    return render_template('quartier.html', nom_quartier=nom_quartier, map=map._repr_html_())

if __name__ == '__main__':
    app.run(debug=True)


          # Calcul des meilleurs quartiers basés sur les entrées de l'utilisateur
  #      top_quartiers = sorted(new_dict.keys(), key=lambda q: -(cafe_weight * new_dict[q]['cafe_score'] + car_weight * new_dict[q]['car_score'] + quiet_weight * new_dict[q]['quiet_score']))[:3]

        # Ajouter le texte explicatif pour chaque recommandation
  #      textes_explicatifs = []
  #      for i in range(3):
  #          quartier = sorted_recommandations[i][0]
  #          poids = {
  #              'cafe_score': cafe_weight,
  #              'car_score': car_weight,
  #              'quiet_score': quiet_weight
  #          }
  #          scores = sorted_recommandations[i][1][1:]
  #          critere = max(poids, key=poids.get)
  #          notes_ponderees = {k: v * poids[k] for k, v in new_dict[quartier].items() if k in poids}
  #          meilleur_critere = [k for k, v in notes_ponderees.items() if v == max(notes_ponderees.values())]
  #          textes_explicatifs.append(f"Nous vous recommandons {quartier} puisque vous avez attribué un poids de {poids[critere]} au critère {critere} et ce quartier est coté {new_dict[quartier][critere]} et il obtient une bonne note consistante pour vos autres critères, comme : {meilleur_critere} avec un score de {max(notes_ponderees.values())}")

   #     return render_template('result.html', recommendations=sorted_recommandations,
   #      #textes_explicatifs=textes_explicatifs,
   #     cafe_weight=cafe_weight, car_weight=car_weight,quiet_weight=quiet_weight, quartiers_images=quartiers_images, price_piece= price_per_PQ, démo = démo)
   # return render_template('form.html')