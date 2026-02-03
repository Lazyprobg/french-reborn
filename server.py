from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import datetime
import os

from models import db, User, Message, MutedUser

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ================= AUTH =================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return render_template("connexion.html")

        session["username"] = user.username
        session["province"] = user.province
        return redirect("/channel")

    return render_template("connexion.html")


@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        username = request.form.get("nom")
        password = request.form.get("mot_de_passe")

        if User.query.filter_by(username=username).first():
            return "Utilisateur déjà existant", 400

        user = User(username=username, province="French Reborn")
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        session["username"] = user.username
        session["province"] = user.province
        return redirect("/channel")

    return render_template("inscription.html")


@app.route("/channel")
def channel():
    if "username" not in session:
        return redirect("/login")
    return render_template("channel_Fre.html", username=session["username"])


@app.route("/messages")
def messages():
    muted = {m.username for m in MutedUser.query.all()}
    msgs = Message.query.order_by(Message.timestamp.asc()).all()

    return jsonify([
        {
            "username": m.author.username,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        }
        for m in msgs if m.author.username not in muted
    ])


@app.route("/send", methods=["POST"])
def send():
    if "username" not in session:
        return "", 403

    if MutedUser.query.filter_by(username=session["username"]).first():
        return "", 403

    content = request.json.get("content", "").strip()
    if not content:
        return "", 400

    user = User.query.filter_by(username=session["username"]).first()

    msg = Message(
        content=content,
        province=session["province"],
        author=user
    )

    db.session.add(msg)
    db.session.commit()
    return "", 204
