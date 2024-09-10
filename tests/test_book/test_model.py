from unittest import TestCase
from app.models import Book
from app import create_app, db

app = create_app('testing')


class TestBookModel(TestCase):
    """Tests the Book model"""
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_create_book(self):
        """Check book is created and stored correctly"""
        book = Book(
            name='Test Book',
            author='John Doe',
            image_url='http://test.com/image.jpg',
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
        
    def test_unique_name_constraints(self):
        """Check if """
