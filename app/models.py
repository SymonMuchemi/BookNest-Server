from . import db
from datetime import datetime


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    author = db.Column(db.String(50))
    penalty_fee = db.Column(db.Integer, default=10)
    quantity = db.Column(db.Integer, nullable=False)

    transactions = db.relationship(
        "Transaction", backref="book", cascade="all, delete-orphan"
    )


class Member(db.Model):
    __tablename__ = "members"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    debt = db.Column(db.Integer, default=0)
    books_borrowed = db.Column(db.Integer, default=0)

    transactions = db.relationship(
        "Transaction", backref="member", cascade="all, delete-orphan"
    )


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"))
    issued_on = db.Column(db.DateTime, default=datetime.now())
    returned_on = db.Column(db.DateTime)
    charge = db.Column(db.Integer, default=0)
    type = db.Column(
        db.Enum("issue", "return", name="transaction_types"), nullable=False
    )
