from flask import Flask, render_template, request, redirect, url_for
import json
import os
import hashlib

app = Flask(__name__)

USERS_FILE = "users.json"


def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    return render_template("connexion.html")


@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        nom = request.form.get("nom")
        mot_de_passe = request.form.get("mot_de_passe")

        if not (5 <= len(nom) <= 20) or len(mot_de_passe) < 1:
            return redirect(url_for("inscription"))

        users = load_users()
        new_id = users[-1]["id"] + 1 if users else 1

        new_user = {
            "id": new_id,
            "username": nom,
            "password_token": hash_password(mot_de_passe)
        }

        users.append(new_user)
        save_users(users)

        return redirect(url_for("connexion"))

    return render_template("inscription.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
