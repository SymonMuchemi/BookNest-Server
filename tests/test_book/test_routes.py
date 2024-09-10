from unittest import TestCase
from app.books.views import create_book
from app.models import Book
from app import create_app, db


class TestBookRoutes(TestCase):
    def setUp(self):
        """Set up the test client and app context."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_hello_world(self):
        """Test the hello world route."""
        response = self.client.get('/api/books/hello')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello world')

    def test_create_book(self):
        """Test the create_book route"""
        payload = {
            "name": 'Testing',
            "author": 'John Doe',
            "quantity": 25,
            "image_url": "https://some.site.com/image.jpg",
            "penalty_fee": 25
        }

        response = self.client.post('/api/books/create', json=payload)
                
        self.assertEqual(response.status_code, 201)
        self.assertIn('Book created succesfully', response.json['Message'])
        self.assertEqual(response.json['book']['name'], 'Testing')
        self.assertEqual(response.json['book']['author'], 'John Doe')
        self.assertEqual(response.json['book']['quantity'], 25)
        self.assertEqual(response.json['book']['image_url'], "https://some.site.com/image.jpg")
        self.assertEqual(response.json['book']['penalty_fee'], 25)
        
    def test_create_book_validation_error(self):
        """Test creation of book with invalid data"""
        payload = {
            "name": None,
            "author": 258,
            "quantity": 5,
            "image_url": "https://example.com/alchemist.jpg",
            "penalty_fee": 2.5
        }

        response = self.client.post('/api/books/create', json=payload)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Validation failed', response.json['Error'])

    def test_delete_book(self):
        """Check if delete book route works"""
        book = Book(
            name='Test Book',
            author='John Doe',
            image_url='https://test.com/image.jpg',
            quantity=4,
            penalty_fee=20
        )
        
        db.session.add(book)
        db.session.commit()
        
        stored_book = Book.query.filter_by(name='Test Book').first()
        
        response = self.client.delete(f'/api/books/delete/{stored_book.id}')
        
        retrieved_book = Book.query.filter_by(name='Test Book').first()
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(retrieved_book)
        self.assertIn('Deletion succesfull!', response.json['Message'])
        
    def test_get_books(self):
        """Check get_books route."""
        payload = {
            'page': 1,
            'per_page': 2
        }

        book1 = Book(
            name='Test Book',
            author='John Doe',
            image_url='https://test.com/image.jpg',
            quantity=4,
            penalty_fee=20
        )
        book2 = Book(
            name='Test Book',
            author='John Doe',
            image_url='https://test.com/image.jpg',
            quantity=4,
            penalty_fee=20
        )
        book3 = Book(
            name='Test Book',
            author='John Doe',
            image_url='https://test.com/image.jpg',
            quantity=4,
            penalty_fee=20
        )
        book4 = Book(
            name='Test Book',
            author='John Doe',
            image_url='https://test.com/image.jpg',
            quantity=4,
            penalty_fee=20
        )
        
        db.session.add(book1)
        db.session.add(book2)
        db.session.add(book3)
        db.session.add(book4)
        
        db.session.commit()
        
        response = self.client.get('/api/books/get_books', query_string=payload)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(4, response.json['total_books'])
        self.assertEqual(2, response.json['total_pages'])
        self.assertEqual(1, response.json['current_page'])
        self.assertEqual(2, response.json['per_page'])
        self.assertEqual(True, response.json['has_next'])
        self.assertEqual(False, response.json['has_prev'])
        self.assertEqual(2, response.json['next_page'])
        self.assertEqual(None, response.json['prev_page'])
