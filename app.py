from flask import Flask
from flask_sqlalchemy import SQLALchemy
import os

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLALchemy(app)
uri = os.environ.get("DATABASE_URL")
if uri.startswith("postgres://"):
 uri = uri.replace("postgres://", 'postgresql:// 1)

app.config[SQLALCHEMY_DATABASE_URI"] = uri
