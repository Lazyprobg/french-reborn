from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import hashlib

app = Flask(__name__)
app.secret_key = "super-secret-key"  # requis pour session

USERS_FILE = "users.json"


# ---------- UTILITAIRES ----------

def init_users_file():
    """Crée users.json s'il n'existe pas ou s'il est vide"""
    if not os.path.exists(USERS_FILE) or os.stat(USERS_FILE).st_size == 0:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_users():
    init_users_file()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("❌ ERREUR: users.json corrompu")
        return []


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def find_user(username):
    for user in load_users():
        if user.get("username") == username:
            return user
    return None


# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    if request.method == "POST":
        username = request.form.get("identifiant")
        password = request.form.get("mot_de_passe")

        if not username or not password:
            return redirect(url_for("connexion"))

        user = find_user(username)
        if not user:
            return redirect(url_for("connexion"))

        if user["password_token"] != hash_password(password):
            return redirect(url_for("connexion"))

        # Stockage sécurisé de la session
        session.clear()
        session["username"] = username

        if user.get("province"):
            return redirect(url_for("channel_fre"))

        return redirect(url_for("choose_province"))

    return render_template("connexion.html")


@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        nom = request.form.get("nom")
        mot_de_passe = request.form.get("mot_de_passe")

        if not nom or not mot_de_passe:
            return redirect(url_for("inscription"))

        users = load_users()

        if find_user(nom):
            return redirect(url_for("inscription"))

        new_id = users[-1]["id"] + 1 if users else 1

        users.append({
            "id": new_id,
            "username": nom,
            "password_token": hash_password(mot_de_passe),
            "province": None
        })

        save_users(users)
        return redirect(url_for("connexion"))

    return render_template("inscription.html")


@app.route("/choose_p", methods=["GET", "POST"])
def choose_province():
    if "username" not in session:
        return redirect(url_for("connexion"))

    if request.method == "POST":
        users = load_users()
        for user in users:
            if user["username"] == session["username"]:
                user["province"] = "French_Reborn"
                break

        save_users(users)
        return redirect(url_for("channel_fre"))

    return render_template("choose_p.html")


@app.route("/channel/French_Reborn")
def channel_fre():
    if "username" not in session:
        return redirect(url_for("connexion"))
    return render_template("channel_Fre.html")


# ---------- LANCEMENT ----------

if __name__ == "__main__":
    init_users_file()
    app.run(host="0.0.0.0", port=5000, debug=True)
