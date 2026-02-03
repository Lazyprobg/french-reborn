from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import datetime
import os

from models import db, User, Message, MutedUser

# =========================
# APP INIT
# =========================

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# =========================
# DATABASE CONFIG
# =========================

database_url = os.environ.get("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if not database_url:
    database_url = "sqlite:///database.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# =========================
# INIT DB
# =========================

with app.app_context():
    db.create_all()

# =========================
# ROUTES - NAVIGATION
# =========================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =========================
# AUTH
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session["username"] = user.username
            session["province"] = user.province
            return redirect("/channel")

        return render_template("connexion.html", error=True)

    return render_template("connexion.html")


@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        username = request.form.get("nom")
        password = request.form.get("mot_de_passe")

        if User.query.filter_by(username=username).first():
            return render_template("inscription.html", error=True)

        user = User(
            username=username,
            password=password,
            province="French Reborn"
        )

        db.session.add(user)
        db.session.commit()

        session["username"] = user.username
        session["province"] = user.province

        return redirect("/channel")

    return render_template("inscription.html")

# =========================
# CHAT
# =========================

@app.route("/channel")
def channel():
    if "username" not in session:
        return redirect("/login")

    return render_template(
        "channel_Fre.html",
        username=session["username"]
    )


@app.route("/messages")
def messages():
    muted_ids = {m.user_id for m in MutedUser.query.all()}

    msgs = Message.query.order_by(Message.timestamp.asc()).all()

    return jsonify([
        {
            "username": m.user.username,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        }
        for m in msgs if m.user_id not in muted_ids
    ])


@app.route("/send", methods=["POST"])
def send():
    if "username" not in session:
        return "", 403

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        return "", 403

    if MutedUser.query.filter_by(user_id=user.id).first():
        return "", 403

    content = request.json.get("content", "").strip()
    if not content:
        return "", 400

    msg = Message(
        user_id=user.id,
        content=content
    )

    db.session.add(msg)
    db.session.commit()
    return "", 204

# =========================
# START SERVER
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
