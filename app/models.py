from . import db
from datetime import datetime


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    author = db.Column(db.String(50))
    image_url = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    rental_fee = db.Column(db.Integer, default=100)
    transactions = db.relationship('Transaction', backref='book')


class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    debt = db.Column(db.Integer, default=0)
    transactions = db.relationship('Transaction', backref='member')


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    transaction_type = db.Column(db.Enum('return', 'issue',
                                         name='transaction_types'),
                                 nullable=False)
    date_of_transaction = db.Column(db.DateTime, default=datetime.now())
