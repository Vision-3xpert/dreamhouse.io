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

