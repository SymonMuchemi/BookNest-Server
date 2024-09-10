from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    author = db.Column(db.String(50))
    image_url = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    penalty_fee = db.Column(db.Integer, default=10)
    
    transactions = db.relationship('Transaction', backref='book')


class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    debt = db.Column(db.Integer, default=0)
    books_borrowed = db.Column(db.Integer, default=0)
    
    transactions = db.relationship('Transaction', backref='member')


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    type = db.Column(db.Enum('return', 'issue',
                                         name='transaction_types'),
                                 nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())


class Librarian(db.Model):
    __tablename__ = 'librarians'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128))
    
    @property
    def password(self):
        raise AttributeError('Password is not readable.')
    
    @password.setter
    def password(self, password):
        """Hashes librarian's password and sets it.

        Args:
            password (str): The password to be hashed.
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Checks if password mathes instance's password.

        Args:
            password (str): password hash value.

        Returns:
            bool: True if matching, False otherwise.
        """
        return check_password_hash(self.password_hash, password)
