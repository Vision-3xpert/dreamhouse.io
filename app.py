from flask import Flask, render_template, request, session, redirect, url_for
import folium as fl
from folium.features import GeoJson
import numpy as np
import pandas as pd



from data import Montreal, new_dict, quartiers_images, superficie, Price_per_piece, Rest_per_KM, Communitycenters, houses, Mairies, Parcs, Sportscenters
from utils import create_marker, filter_dataframe, get_request_arg_int, style_function


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


@app.route('/save_weights', methods=['POST'])
def save_weights():
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
    session['cafe_weight'] = cafe_weight
    session['car_weight'] = car_weight
    session['walk_weight'] = walk_weight
    session['park_weight'] = park_weight
    session['quiet_weight'] = quiet_weight
    session['cycling_weight'] = cycling_weight
    session['transit_weight'] = transit_weight
    session['vibrant_weight'] = vibrant_weight
    session['daycares_weight'] = daycares_weight
    session['primary_weight'] = primary_weight
    session['shopping_weight'] = shopping_weight
    session['groceries_weight'] = groceries_weight
    session['nightlife_weight'] = nightlife_weight
    session['restaurant_weight'] = restaurant_weight
    session['high_school_weight'] = high_school_weight
    sorted_recommandations = []

    car_weight = session.get('car_weight', [])
    cafe_weight = session.get('cafe_weight', [])
    walk_weight = session.get('walk_weight', [])
    park_weight = session.get('park_weight', [])
    quiet_weight = session.get('quiet_weight', [])
    cycling_weight = session.get('cycling_weight', [])
    transit_weight = session.get('transit_weight', [])
    vibrant_weight = session.get('vibrant_weight', [])
    daycares_weight = session.get('daycares_weight', [])
    primary_weight = session.get('primary_weight', [])
    shopping_weight = session.get('shopping_weight', [])               
    groceries_weight = session.get('groceries_weight', [])
    nightlife_weight = session.get('nightlife_weight', [])
    restaurant_weight = session.get('restaurant_weight', [])
    high_school_weight = session.get('high_school_weight', [])
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
                               quartiers_images=quartiers_images, price_piece=price_per_PQ, démo=démo)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('form.html')

@app.route('/quartier', methods=["POST", "GET"])
def quartier():
    car_weight = session.get('car_weight', [])
    cafe_weight = session.get('cafe_weight', [])
    walk_weight = session.get('walk_weight', [])
    park_weight = session.get('park_weight', [])
    quiet_weight = session.get('quiet_weight', [])
    cycling_weight = session.get('cycling_weight', [])
    transit_weight = session.get('transit_weight', [])
    vibrant_weight = session.get('vibrant_weight', [])
    daycares_weight = session.get('daycares_weight', [])
    primary_weight = session.get('primary_weight', [])
    shopping_weight = session.get('shopping_weight', [])               
    groceries_weight = session.get('groceries_weight', [])
    nightlife_weight = session.get('nightlife_weight', [])
    restaurant_weight = session.get('restaurant_weight', [])
    high_school_weight = session.get('high_school_weight', [])
    nom_quartier = request.args.get('quartier')
    # Apply filters
    filtered_house = houses.loc[houses['NOM'] == nom_quartier]
    filtered_house = filter_dataframe(filtered_house, 'titre', request.args.get('type'))
    min_price = get_request_arg_int(request, 'min_price')
    max_price = get_request_arg_int(request, 'max_price')
    if min_price:
        filtered_house = filtered_house[(filtered_house['price'] >= min_price)]
    if max_price:
        filtered_house = filtered_house[(filtered_house['price'] <= max_price)]
    min_bedrooms = get_request_arg_int(request, 'min_bedrooms')
    if min_bedrooms:
        filtered_house = filtered_house[filtered_house['beds'] >= min_bedrooms]
    min_bathrooms = get_request_arg_int(request, 'min_bathrooms')
    if min_bathrooms:
        filtered_house = filtered_house[filtered_house['baths'] >= min_bathrooms]
    scores = filtered_house.apply(lambda row: (row["car_score"] * car_weight +
                                            row["cafe_score"] * cafe_weight +
                                            row["walk_score"] * walk_weight +
                                            row["park_score"] * park_weight +
                                            row["quiet_score"] * quiet_weight +
                                            row["cycling_score"] * cycling_weight +
                                            row["transit_score"] * transit_weight +
                                            row["vibrant_score"] * vibrant_weight +
                                            row["daycares_score"] * daycares_weight +
                                            row["primary_score"] * primary_weight +
                                            row["shopping_score"] * shopping_weight +
                                            row["groceries_score"] * groceries_weight +
                                            row["nightlife_score"] * nightlife_weight +
                                            row["restaurant_score"] * restaurant_weight +
                                            row["high_school_score"] * high_school_weight), axis=1)
    scores = scores.astype(int) # convert scores to integers
    scores_df = pd.DataFrame({'id': filtered_house.index, 'score': scores})
    sorted_scores_df = scores_df.sort_values(by='score', ascending=False)
    nb_house = get_request_arg_int(request, 'nb_house')
    if nb_house:
        nb_house = nb_house
    else:
        nb_house =30
    top_scores_df = sorted_scores_df.head(nb_house)
    top_scores_index = top_scores_df['id'].tolist()
    # Prepare DataFrames
    Mairie = Mairies.loc[Mairies['NOM'] == nom_quartier].dropna(subset=['Lat', 'Lon'])
    Parc = Parcs.loc[Parcs['NOM'] == nom_quartier].dropna(subset=['Lat', 'Lon'])
    Sportscenter = Sportscenters.loc[Sportscenters['NOM'] == nom_quartier].dropna(subset=['Lat', 'Lon'])
    community = Communitycenters.loc[Communitycenters['NOM'] == nom_quartier].dropna(subset=['Lat', 'Lon'])

    map = fl.Map(location=[45.50884, -73.58781], zoom_start=11)
    # Récupérer la liste des cases à cocher cochées
    landmarks = request.args.getlist('landmarks')
    form_submitted = request.args.get('form_submitted')

    # Afficher tous les parcs si park_weight > 0 et si la page n'a pas été soumise
    if park_weight > 0 and not form_submitted:
        parcs = Parc
    # Si la page a été soumise, afficher les parcs en fonction de l'état de la case à cocher
    elif 'parks' in landmarks:
        parcs = Parc
    else:
        parcs = Parc.iloc[0:0]  # Retirer tous les parcs



    nb_parcs = parcs.count()[0]
    if 'sports' not in landmarks:
        Sportscenter = Sportscenter.iloc[0:0] # Retirer tous les centres sportifs
    nb_sports = Sportscenter.count()[0]
    if 'communities' not in landmarks:
        community = community.iloc[0:0] # Retirer tous les centres communautaires
    nb_communities = community.count()[0]
    if 'Mairies' not in landmarks:
        Mairie = Mairie.iloc[0:0] # Retirer toutes les mairies
    nb_mairies = Mairie.count()[0]

    # Add markers to the map
    create_marker(community, "fa-solid fa-masks-theater", "beige", map,"communautaires", "#f2cc8f")
    create_marker(Sportscenter, "fa-solid fa-dumbbell", "cadetblue", map,"sports", "#415a77")
    create_marker(parcs, "tree", "green", map,"parcs", "#57cc99")
    create_marker(Mairie, "fa-solid fa-building-columns", "red", map,"mairies", "#e63946")
    q25 = np.percentile(scores, 25)  # 62.5
    q50 = np.percentile(scores, 50)  # 75.0
    q75 = np.percentile(scores, 75)  # 87.5
    q100 = np.percentile(scores, 100)  # 100.0





    # Your existing code for styling, adding layers, and fitting bounds

    # Add house markers
    for index, row in filtered_house.loc[top_scores_index].iterrows():

        if  'Maison' in row['titre']:
            icon = 'fa fa-home'
        elif 'Condo' in row['titre'] or 'Studio' in row['titre']:
            icon = 'fa fa-building'
        elif 'plex' in row['titre']:
            icon = 'fa-dollar-sign'
        else:
            icon = 'fa-map-marker'
        score = scores.loc[index]

        if score < q25:
            color = "#ef476f"
        elif score < q50:
            color = "#ffd166"
        elif score < q75:
            color = "#06d6a0"
        else:
            color = "#fff"

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
        icon_book = fl.Icon(icon=icon, prefix='fa', color="black", icon_color=color)
        fl.Marker(location=[lat, lon], popup=popup, icon=icon_book).add_to(map)

    
    filter_type = request.args.get('type')
    min_price = get_request_arg_int(request, 'min_price')
    max_price = get_request_arg_int(request, 'max_price')
    min_bedrooms = get_request_arg_int(request, 'min_bedrooms')
    min_bathrooms = get_request_arg_int(request, 'min_bathrooms')
    for i in range(len(Montreal["features"])):
        if Montreal["features"][i]['properties']['NOM'] == nom_quartier:
            layer = GeoJson(Montreal["features"][i], style_function=style_function)
            bounds = fl.GeoJson(Montreal["features"][i]).get_bounds()
            map.fit_bounds(bounds, max_zoom=13)
            map.add_child(layer)
    return render_template('quartier.html', nom_quartier=nom_quartier, map=map._repr_html_(),
                           filter_type=filter_type, min_price=min_price, max_price=max_price, nb_house=nb_house,
                           min_bedrooms=min_bedrooms, min_bathrooms=min_bathrooms, nb_parcs=nb_parcs, nb_sports = nb_sports, nb_communities = nb_communities, nb_mairies = nb_mairies, park_weight = park_weight)


if __name__ == '__main__':
    app.run(debug=True)
