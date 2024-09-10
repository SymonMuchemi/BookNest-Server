from unittest import TestCase
from app.models import Book, Transaction, Member
from app.utils import TransactionType
from app import create_app, db

app = create_app('testing')


class TestBookModel(TestCase):
    """Tests the Book model"""
    def setUp(self):
        """Set up the test client and Flask app context."""
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_create_book(self):
        """Check book is created and stored correctly"""
        book = Book(
            name='Test Book',
            author='John Doe',
            image_url='https://test.com/image.jpg',
            quantity=4,
            penalty_fee=20
        )
        
        db.session.add(book)
        db.session.commit()
        
        retrieved_book = Book.query.filter_by(name='Test Book').first()
        
        self.assertIsNotNone(retrieved_book)
        self.assertEqual(retrieved_book.author, 'John Doe')
        self.assertEqual(retrieved_book.quantity, 4)
        self.assertEqual(retrieved_book.penalty_fee, 20)
    
        
    def test_create_transaction(self):
        """Check transaction is created and stored correctly"""
        book = Book(
            name='Test Book',
            author='John Doe',
            image_url='https://test.com/image.jpg',
            quantity=4,
            penalty_fee=20
        )
        
        db.session.add(book)
        db.session.commit()
        
        retrieved_book = Book.query.filter_by(name='Test Book').first()
        
        transaction = Transaction(
            book_id=retrieved_book.id,
            member_id=1,
            type=TransactionType.ISSUE
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        retrieved_transaction = Transaction.query.filter_by(book_id=retrieved_book.id).first()
        
        self.assertIsNotNone(retrieved_transaction)
        self.assertEqual(retrieved_transaction.member_id, 1)
        self.assertEqual(retrieved_transaction.type, TransactionType.ISSUE)

    def test_create_member(self):
        """Check member is created and stored correctly"""
        member = Member(
            name='John Doe',
            debt=20,
            books_borrowed=3
        )
        
        db.session.add(member)
        db.session.commit()
        
        retrieved_member = Member.query.filter_by(name='John Doe').first()
        
        self.assertIsNotNone(retrieved_member)
        self.assertEqual(retrieved_member.debt, 20)
        self.assertEqual(retrieved_member.books_borrowed, 3)
        
    def test_default_attributes(self):
        """Check instances creation with correct values for default attributes"""
        book = Book(
            name='Another test book',
            author='Janet Doe',
            image_url='https://somesite.com/image',
            quantity=5
        )
        
        db.session.add(book)
        db.session.commit()
        
        retrieved_book = Book.query.filter_by(name='Another test book').first()
        
        self.assertIsNotNone(retrieved_book)
        self.assertEqual(retrieved_book.penalty_fee, 10)

    def test_book_transaction_relationship(self):
        """Check relationship between book and transaction"""
        book = Book(
            name='Test and DSA',
            author='John Doe',
            image_url='https://test.com/image.jpg',
            quantity=4,
            penalty_fee=20
        )
        
        db.session.add(book)
        db.session.commit()

        retrieved_book = Book.query.filter_by(name='Test and DSA').first()
        
        transaction1 = Transaction(
            book_id=retrieved_book.id,
            member_id=2,
            type=TransactionType.ISSUE
        )
        
        transaction2 = Transaction(
            book_id=retrieved_book.id,
            member_id=2,
            type=TransactionType.ISSUE
        )

        db.session.add(transaction1)
        db.session.add(transaction2)
        
        db.session.commit()
        
        self.assertIsNotNone(retrieved_book)
        self.assertIsNotNone(transaction1)
        self.assertIsNotNone(transaction2)
        self.assertIsNotNone(retrieved_book.transactions)
        self.assertEqual(len(retrieved_book.transactions), 2)

    def test_member_transaction_relationship(self):
        """Check relationship between member and transaction"""
        member = Member(
            name='John Doe',
            debt=20,
            books_borrowed=3
        )
        
        db.session.add(member)
        db.session.commit()

        retrieved_member = Member.query.filter_by(name='John Doe').first()
        
        transaction1 = Transaction(
            book_id=1,
            member_id=retrieved_member.id,
            type=TransactionType.ISSUE
        )
        
        transaction2 = Transaction(
            book_id=2,
            member_id=retrieved_member.id,
            type=TransactionType.ISSUE
        )

        db.session.add(transaction1)
        db.session.add(transaction2)
        
        db.session.commit()
        
        self.assertIsNotNone(retrieved_member)
        self.assertIsNotNone(transaction1)
        self.assertIsNotNone(transaction2)
        self.assertIsNotNone(retrieved_member.transactions)
        self.assertEqual(len(retrieved_member.transactions), 2)
