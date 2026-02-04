from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(name)

Sécurité (sessions, cookies)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

Base de données

database_url = os.environ.get("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

Import des modèles APRÈS db

from models import User

Création des tables

with app.app_context():
db.create_all()

(ensuite tu ajoutes tes routes ici)"
