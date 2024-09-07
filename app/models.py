from . import db


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    author = db.Column(db.String(50))
    image_url = db.Column(db.Text)
    count = db.Column(db.Integer, default=0)
    rental_fee = db.Column(db.Integer, default=100)


class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    debt = db.Column(db.Integer, default=0)


class Transaction(db.Model):
    __tablename__ = 'transactions'
