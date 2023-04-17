import folium as fl


def create_marker(df, icon, color, map,image,couleur):
    for index, row in df.iterrows():
        lat, lon = row['Lat'], row['Lon']
        showcase = fl.Icon(icon=icon, prefix='fa', color=color)
        marker = fl.Marker(location=[lat, lon], icon=showcase)
        popup_html = f"""    <article class="card" style =" width: 225px; height: 250px; border-radius: 25px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3); overflow: hidden; margin: auto;">
        <div class="thumb" style =" width: auto;height: 50%;"> <img src="/static/images/{image}.jpg" style="width:100%; height:100%;" alt=""></div>
        <div class="details" style=" padding: 14px 24px;display:flex; flex-direction:column; ">
            <h2 class="title" style=" margin: 10px 0; color: #6a6b6d;font-size: 0.8rem;">{row["Centre"]}</h2>
            <h3 class="price" style="   margin: 10px 0; font-size: 1rem; font-weight: 400; margin: 0px 0px; color: {couleur}; cursor: pointer;">{row["Addresse"]}</h3>
            <a class="addresse" href="https://www.google.com/maps/place/{row["Addresse"]}" target="_blank" style="background: {couleur}; padding: 10px; width:60%; color: #fff; text-align:center; margin: 10px auto; border-radius: 25px;"> StreetView <i class="fa-solid fa-magnifying-glass-location"></i></a>
        </div>
        </article>"""
        marker.add_child(fl.Popup(popup_html))
        marker.add_to(map)

def filter_dataframe(df, key, value):
    return df[df[key].str.contains(value)] if value else df

def get_request_arg_int(request, arg_name):
    arg_value = request.args.get(arg_name)
    return int(arg_value) if arg_value else None

def style_function(feature):
    return {
    'fillOpacity': 0.4,
    'color': 'blue',
    'weight': 2,
    }
def generate_explanation(recommendation, scores):
    # Trouver les 3 critères les plus importants
    top_criteria = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]

    # Générer une phrase expliquant la recommandation
    explanation = []

    for i, criterion in enumerate(top_criteria):
        if criterion[0] == 'car_score':
            explanation .append("Un accès facile en voiture et un stationnement abondant pour les résidents et les visiteurs.")
        elif criterion[0] == 'cafe_score':
            explanation .append("Un grand nombre de cafés pour les amateurs de caféine et les espaces de travail détendus.")
        elif criterion[0] == 'walk_score':
            explanation .append("Une excellente accessibilité à pied, permettant de se déplacer facilement sans véhicule.")
        elif criterion[0] == 'park_score':
            explanation .append("De nombreux parcs et espaces verts pour les activités de plein air et la détente.")
        elif criterion[0] == 'quiet_score':
            explanation .append("Un environnement paisible et calme pour les résidents qui préfèrent la tranquillité.")
        elif criterion[0] == 'cycling_score':
            explanation .append("Des pistes cyclables et une infrastructure cyclable pour les amateurs de vélo.")
        elif criterion[0] == 'transit_score':
            explanation .append("Un accès pratique aux transports en commun pour les déplacements sans voiture.")
        elif criterion[0] == 'vibrant_score':
            explanation .append("Une atmosphère animée et dynamique, avec des activités et des événements réguliers.")
        elif criterion[0] == 'daycares_score':
            explanation .append("Un bon nombre de garderies pour les familles avec de jeunes enfants.")
        elif criterion[0] == 'primary_score':
            explanation .append("Des écoles primaires de qualité pour les familles avec de jeunes enfants.")
        elif criterion[0] == 'shopping_score':
            explanation .append("Des centres commerciaux et des boutiques pour répondre aux besoins des acheteurs.")
        elif criterion[0] == 'groceries_score':
            explanation .append("Un accès facile aux épiceries pour les besoins quotidiens en alimentation.")
        elif criterion[0] == 'nightlife_score':
            explanation .append("Une vie nocturne animée avec des bars, des clubs et des lieux de divertissement.")
        elif criterion[0] == 'restaurant_score':
            explanation .append("Une variété de restaurants pour satisfaire les goûts culinaires des résidents et des visiteurs.")
        elif criterion[0] == 'high_school_score':
            explanation .append("Des écoles secondaires de qualité pour les familles avec des adolescents.")

    return explanation
def zip_lists(*args):
    return zip(*args)

