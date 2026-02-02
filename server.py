from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# ==========================
# INITIALISATION APP & DB
# ==========================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key")

# DATABASE_URL pour Render
uri = os.environ.get("DATABASE_URL")
if not uri:
    uri = "sqlite:///data.db"  # fallback local pour tests

# Postgres URI correction
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==========================
# MODELS
# ==========================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="Citoyen")
    province = db.Column(db.String(100), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("messages", lazy=True))

# Crée les tables
with app.app_context():
    db.create_all()

# ==========================
# ROUTES PRINCIPALES
# ==========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        nom = request.form.get("nom")
        mot_de_passe = request.form.get("mot_de_passe")
        if not nom or not mot_de_passe:
            return redirect(url_for("inscription"))

        if User.query.filter_by(username=nom).first():
            return redirect(url_for("inscription"))

        user = User(username=nom)
        user.set_password(mot_de_passe)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("connexion"))

    return render_template("inscription.html")


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    if request.method == "POST":
        username = request.form.get("identifiant")
        password = request.form.get("mot_de_passe")
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return redirect(url_for("connexion"))

        session.clear()
        session["username"] = user.username
        session["role"] = user.role
        session["province"] = user.province

        if user.province:
            return redirect(url_for("channel_fre"))
        return redirect(url_for("choose_province"))

    return render_template("connexion.html")


@app.route("/choose_p", methods=["GET", "POST"])
def choose_province():
    if "username" not in session:
        return redirect(url_for("connexion"))

    if request.method == "POST":
        user = User.query.filter_by(username=session["username"]).first()
        user.province = "French_Reborn"
        db.session.commit()
        session["province"] = user.province
        return redirect(url_for("channel_fre"))

    return render_template("choose_p.html")


@app.route("/channel/French_Reborn")
def channel_fre():
    if "username" not in session:
        return redirect(url_for("connexion"))

    user = User.query.filter_by(username=session["username"]).first()
    return render_template("channel_Fre.html", user_role=user.role)


# ==========================
# ROUTES MESSAGES
# ==========================
@app.route("/send_message", methods=["POST"])
def send_message():
    if "username" not in session:
        return jsonify({"success": False, "error": "Non connecté"}), 401

    data = request.get_json()
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"success": False, "error": "Message vide"}), 400

    user = User.query.filter_by(username=session["username"]).first()
    if not user or not user.province:
        return jsonify({"success": False, "error": "Province non définie"}), 400

    message = Message(
        user_id=user.id,
        province=user.province,
        content=content,
        timestamp=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()
    return jsonify({"success": True})


@app.route("/messages")
def get_messages():
    if "username" not in session:
        return jsonify([])

    user = User.query.filter_by(username=session["username"]).first()
    if not user or not user.province:
        return jsonify([])

    messages = Message.query.filter_by(province=user.province).order_by(Message.timestamp).all()
    return jsonify([
        {
            "username": m.user.username,
            "role": m.user.role,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        } for m in messages
    ])


# ==========================
# LANCEMENT
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
