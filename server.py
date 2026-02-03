from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# =========================
# APP INIT
# =========================

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# Database (Render compatible)
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

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
# MUTE SYSTEM
# =========================

@app.route("/mute_user", methods=["POST"])
def mute_user():
    user = User.query.filter_by(username=session["username"]).first()
    if not is_lazy() and "mute" not in user_permissions(user):
        return jsonify({"success": False}), 403

    target = request.json.get("username")
    if target and not MutedUser.query.filter_by(username=target).first():
        db.session.add(MutedUser(username=target))
        db.session.commit()

    return jsonify({"success": True})


@app.route("/unmute_user", methods=["POST"])
def unmute_user():
    user = User.query.filter_by(username=session["username"]).first()
    if not is_lazy() and "unmute" not in user_permissions(user):
        return jsonify({"success": False}), 403

    target = request.json.get("username")
    mu = MutedUser.query.filter_by(username=target).first()
    if mu:
        db.session.delete(mu)
        db.session.commit()

    return jsonify({"success": True})

# =========================
# ROLES & ADMIN
# =========================

@app.route("/create_role", methods=["POST"])
def create_role():
    if not is_lazy():
        return "", 403

    data = request.get_json()
    role = Role(
        name=data["name"],
        province=session["province"]
    )
    db.session.add(role)
    db.session.commit()

    for p in data.get("permissions", []):
        db.session.add(
            RolePermission(role_id=role.id, permission=p)
        )

    db.session.commit()
    return jsonify({"success": True})


@app.route("/assign_role", methods=["POST"])
def assign_role():
    if not is_lazy():
        return "", 403

    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if not user:
        return "", 404

    db.session.add(
        UserRole(user_id=user.id, role_id=data["role_id"])
    )
    db.session.commit()
    return jsonify({"success": True})


@app.route("/roles")
def roles():
    if not is_lazy():
        return jsonify([])

    roles = Role.query.filter_by(
        province=session["province"]
    ).all()

    return jsonify([
        {"id": r.id, "name": r.name} for r in roles
    ])


@app.route("/my_permissions")
def my_permissions():
    if "username" not in session:
        return jsonify([])

    user = User.query.filter_by(
        username=session["username"]
    ).first()

    return jsonify(list(user_permissions(user)))

# =========================
# START SERVER (RENDER OK)
# =========================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
