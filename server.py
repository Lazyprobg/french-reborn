from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# ==========================
# INITIALISATION
# ==========================

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key")

# ==========================
# DATABASE
# ==========================

uri = os.environ.get("DATABASE_URL")
if not uri:
    uri = "sqlite:///data.db"

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
    province = db.Column(db.String(100))

    messages = db.relationship("Message", backref="user", lazy=True)

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

class Mute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    province = db.Column(db.String(100), nullable=False)
    muted_username = db.Column(db.String(80), nullable=False)

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

@app.route("/channel/French_Reborn")
def channel_fre():
    if "username" not in session:
        return redirect(url_for("connexion"))

    user = User.query.filter_by(username=session["username"]).first()
    return render_template(
        "channel_Fre.html",
        user_role=user.role,
        current_user=user.username
    )

# ==========================
# ROUTES MESSAGES
# ==========================

@app.route("/send_message", methods=["POST"])
def send_message():
    if "username" not in session:
        return jsonify({"success": False}), 401

    content = request.json.get("content", "").strip()
    if not content:
        return jsonify({"success": False}), 400

    user = User.query.filter_by(username=session["username"]).first()
    message = Message(user_id=user.id, province=user.province, content=content)
    db.session.add(message)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/messages")
def get_messages():
    if "username" not in session:
        return jsonify([])

    user = User.query.filter_by(username=session["username"]).first()
    muted = [m.muted_username for m in Mute.query.filter_by(province=user.province)]
    messages = Message.query.filter_by(province=user.province).order_by(Message.timestamp)

    return jsonify([
        {
            "username": m.user.username,
            "role": m.user.role,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        }
        for m in messages if m.user.username not in muted
    ])
