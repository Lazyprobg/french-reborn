from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    if request.method == "POST":
        # Pour plus tard : traitement de la connexion
        identifiant = request.form.get("identifiant")
        mot_de_passe = request.form.get("mot_de_passe")
        # Pour l'instant, on ne fait rien avec
        return redirect(url_for("menu"))

    return render_template("connexion.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
