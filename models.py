from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="citoyen")

    # Relation : un utilisateur → plusieurs messages
    messages = db.relationship("Message", backref="author", lazy=True)

    def set_password(self, password):
        """Hash et stocke le mot de passe"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    province = db.Column(db.String(50), nullable=False)

    # Clé étrangère vers User
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Message {self.id} by User {self.user_id}>"
