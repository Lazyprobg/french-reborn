from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# =========================
# APP INIT
# =========================

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# =========================
# DATABASE CONFIG (SAFE)
# =========================

database_url = os.environ.get("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
else:
    # ✅ FALLBACK LOCAL / RENDER SAFE
    database_url = "sqlite:///database.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# MODELS
# =========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    province = db.Column(db.String(100), nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class MutedUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(100), nullable=False)


class RolePermission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    permission = db.Column(db.String(50), nullable=False)


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)

# =========================
# INIT DB (IMPORTANT)
# =========================

with app.app_context():
    db.create_all()

# =========================
# UTILS
# =========================

def is_lazy():
    return session.get("username") == "Lazyprobg"


def user_permissions(user):
    perms = set()
    roles = (
        db.session.query(Role)
        .join(UserRole)
        .filter(UserRole.user_id == user.id)
        .all()
    )
    for r in roles:
        for p in RolePermission.query.filter_by(role_id=r.id).all():
            perms.add(p.permission)
    return perms

# =========================
# AUTH
# =========================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session["username"] = user.username
            session["province"] = user.province
            return redirect("/channel")

    return render_template("connexion.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =========================
# CHAT
# =========================

@app.route("/channel")
def channel():
    if "username" not in session:
        return redirect("/")
    return render_template(
        "channel_Fre.html",
        current_user=session["username"]
    )


@app.route("/messages")
def messages():
    msgs = Message.query.order_by(Message.timestamp.asc()).all()
    muted = {m.username for m in MutedUser.query.all()}

    return jsonify([
        {
            "username": m.username,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        }
        for m in msgs if m.username not in muted
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

    msg = Message(
        username=session["username"],
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
