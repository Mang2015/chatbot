from flask import Flask
import SQLAlchemy
import os
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy()
db.init_app(app)
from app.models import *
with app.app_context():
    db.create_all()

from app import echoserver
#hello
