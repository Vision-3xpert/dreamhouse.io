from flask import Flask, render_template, request
import pandas as pd
houses = pd.read_csv("Export/Propriétés_map.csv")
test = houses.groupby("NOM").mean().round(2)
#quartier_liste = [i for i,r in test.iterrows()]
my_dict = {i:r[:0-3] for i,r in test.iterrows()}
new_dict = {}
new_dict = {}
for ville, scores in my_dict.items():
    new_dict[ville] = {}
    for score_type, score_value in scores.items():
        new_dict[ville][score_type] = score_value

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        cafe_weight = int(request.form['cafe'])
        car_weight = int(request.form['car'])
        quiet_weight = int(request.form['quiet'])

        total_score = []
        quartier_liste = []
        recommandations = {}
        for k, v in new_dict.items():
            quartier_liste.append(k)
            car_score = round(car_weight * new_dict[k]['car_score'],1)
            cafe_score = round(cafe_weight * new_dict[k]['cafe_score'],1)
            quiet_score = round(quiet_weight * new_dict[k]['quiet_score'],1)
            total_score = round(cafe_score + car_score + quiet_score, 1)

            recommandations[k] = [total_score, cafe_score, car_score, quiet_score]
        sorted_recommandations = sorted(recommandations.items(), key=lambda x: x[1][0], reverse=True)

        # Ajouter le texte explicatif pour chaque recommandation
        textes_explicatifs = []
        for i in range(3):
            quartier = sorted_recommandations[i][0]
            poids = {
                'cafe_score': cafe_weight,
                'car_score': car_weight,
                'quiet_score': quiet_weight
            }
            scores = sorted_recommandations[i][1][1:]
            critere = max(poids, key=poids.get)
            notes_ponderees = {k: v * poids[k] for k, v in new_dict[quartier].items() if k in poids}
            meilleur_critere = [k for k, v in notes_ponderees.items() if v == max(notes_ponderees.values())]
            #textes_explicatifs.append(f"Nous vous recommandons {quartier} puisque vous avez attribué un poids de {poids.get(critere, 0)} au critère {critere} et ce quartier est coté {new_dict[quartier].get(critere, 0)} et il obtient une bonne note consistante pour vos autres critères, comme : {[k for k, v in new_dict[quartier].items() if v == max(scores)]} avec un score de {max(scores)}")

            textes_explicatifs.append(f"Nous vous recommandons {quartier} puisque vous avez attribué un poids de {poids[critere]} au critère {critere} et ce quartier est coté {new_dict[quartier][critere]} et il obtient une bonne note consistante pour vos autres critères, comme : {meilleur_critere} avec un score de {max(notes_ponderees.values())}")
            #textes_explicatifs.append(f"Nous vous recommandons {quartier} puisque vous avez attribué un poids de {poids[critere]} au critère {critere} et ce quartier est coté {new_dict[quartier][critere]} et il obtient une bonne note consistante pour vos autres critères, comme : {[k for k, v in new_dict[quartier].items() if v == max(scores)]} avec un score de {max(scores)}")

        return render_template('result.html', recommendations=sorted_recommandations, textes_explicatifs=textes_explicatifs, cafe_weight=cafe_weight, car_weight=car_weight,quiet_weight=quiet_weight)
    return render_template('form.html')



if __name__ == '__main__':
    app.run(debug=True)