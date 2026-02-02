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


def find_user(username):
    users = load_users()
    for user in users:
        if user["username"] == username:
            return user
    return None


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

        user = find_user(username)
        if not user:
            return redirect(url_for("connexion"))

        if user["password_token"] != hash_password(password):
            return redirect(url_for("connexion"))

        # Connexion réussie
        if user.get("province"):
            return redirect(url_for("channel_fre"))

        return redirect(url_for("choose_province"))

    return render_template("connexion.html")


@app.route("/choose_p")
def choose_province():
    return render_template("choose_p.html")


@app.route("/choose_p/french_reborn", methods=["POST"])
def choose_french_reborn():
    username = request.form.get("username")
    users = load_users()

    for user in users:
        if user["username"] == username:
            user["province"] = "French_Reborn"
            break

    save_users(users)
    return redirect(url_for("channel_fre"))


@app.route("/channel/French_Reborn")
def channel_fre():
    return render_template("channel_Fre.html")

@app.route("/inscription")
def inscription():
    return render_template("inscription.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

