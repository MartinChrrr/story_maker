from extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    hash = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.TEXT, unique=True, nullable=True)
    one_line = db.Column(db.TEXT, unique=True, nullable=True)
    title = db.Column(db.TEXT, unique=True, nullable=True)
