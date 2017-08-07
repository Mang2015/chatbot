from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Unicode(32), unique=True, nullable=False)
    information = db.Column(db.Unicode(1024))

    def __init__(self, username, information):
        self.username = username
        self.information = information

class State(db.Model):
    sid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    s_info = db.Column(db.Unicode(1024))

    def __init__(self, s_info):
        self.s_info = s_info
        
