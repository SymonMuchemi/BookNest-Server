from unittest import TestCase
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
            "title": 'Testing',
            "author": 'John Doe',
            "quantity": 25,
            "penalty_fee": 25
        }

        response = self.client.post('/api/books/create', json=payload)
                
        self.assertEqual(response.status_code, 201)
        self.assertIn('Book created succesfully', response.json['Message'])
        self.assertEqual(response.json['book']['title'], 'Testing')
        self.assertEqual(response.json['book']['author'], 'John Doe')
        self.assertEqual(response.json['book']['quantity'], 25)
        self.assertEqual(response.json['book']['penalty_fee'], 25)
        
    def test_create_book_validation_error(self):
        """Test creation of book with invalid data"""
        payload = {
            "title": None,
            "author": 258,
            "quantity": 5,
            "penalty_fee": 2.5
        }

        response = self.client.post('/api/books/create', json=payload)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Validation failed', response.json['Error'])

    def test_delete_book(self):
        """Check if delete book route works"""
        book = Book(
            title='Test Book',
            author='John Doe',
            quantity=4,
            penalty_fee=20
        )
        
        db.session.add(book)
        db.session.commit()
        
        stored_book = Book.query.filter_by(title='Test Book').first()
        
        response = self.client.delete(f'/api/books/delete/{stored_book.id}')
        
        retrieved_book = Book.query.filter_by(title='Test Book').first()
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(retrieved_book)
        self.assertIn('Deletion succesfull!', response.json['Message'])

    def test_delete_book_on_invalid_id(self):
        """Check if delete book route returns error on invalid id."""
        response = self.client.delete('/api/books/delete/100')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Could not find book', response.json['Error'])
        
    def test_get_books(self):
        """Check get_books route."""
        payload = {
            'page': 1,
            'per_page': 2
        }

        book1 = Book(
            title='Test Book',
            author='John Doe',
            quantity=4,
            penalty_fee=20
        )
        book2 = Book(
            title='Test Book',
            author='John Doe',
            quantity=4,
            penalty_fee=20
        )
        book3 = Book(
            title='Test Book',
            author='John Doe',
            quantity=4,
            penalty_fee=20
        )
        book4 = Book(
            title='Test Book',
            author='John Doe',
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

    def test_get_by_name(self):
        """Check get_by_name endpoint return appropriate book data."""
        book1 = Book(
            title='Test Book',
            author='John Doe',
            quantity=4,
            penalty_fee=20
        )
        
        book2 = Book(
            title='Another book',
            author='John Doe',
            quantity=4,
            penalty_fee=20
        )

        book3 = Book(
            title='The Last Book',
            author='Mitchelle White',
            quantity=4,
            penalty_fee=20
        )

        db.session.add(book1)
        db.session.add(book2)
        db.session.add(book3)
        
        db.session.commit()
        
        response = self.client.get('/api/books/get_by_name/book')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)

    def test_get_by_name_on_empty_return(self):
        """Check if get_by_id endpoint returns an error message if book is not found."""
        response = self.client.get('/api/books/get_by_name/bob')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Could not find book', response.json['Error'])

    def test_get_by_author_on_empty_return(self):
        """Check if get_by_author endpoint returns an error message if author is not found."""
        response = self.client.get('/api/books/get_by_author/bob')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Could not find book', response.json['Error'])

    def test_get_by_author(self):
        """Check if get_by_author endpoint returns appropriate data."""
        book1 = Book(
            title='Test Book',
            author='John Doe',
            quantity=4,
            penalty_fee=20
        )
        
        book2 = Book(
            title='Another book',
            author='John Doe',
            quantity=4,
            penalty_fee=20
        )

        book3 = Book(
            title='The Last Book',
            author='Mitchelle White',
            quantity=4,
            penalty_fee=20
        )

        db.session.add(book1)
        db.session.add(book2)
        db.session.add(book3)
        
        db.session.commit()
        
        response = self.client.get('/api/books/get_by_author/white')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    def test_update(self):
        """Check if update routes updates book."""
        book = Book(
            title='Test Book',
            author='John Doe',
            quantity=4,
            penalty_fee=20
        )
        
        db.session.add(book)
        db.session.commit()
        
        update_data = {
            'title': 'Updated Book',
            'author': 'Jane Doe',
            'quantity': 10,
            'penalty_fee': 15
        }
        
        retrieved_book = Book.query.filter_by(title='Test Book').first()
        
        response = self.client.put(f'/api/books/update/{retrieved_book.id}',json=update_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Book updated successfully', response.json['Message'])
        self.assertEqual('Jane Doe', response.json['New book']['author'])
        self.assertEqual(10, response.json['New book']['quantity'])
        self.assertEqual(15, response.json['New book']['penalty_fee'])

    def test_update_on_invalid_data(self):
        """Check if update route returns error on invalid data."""
        book = Book(
            title='Test Book',
            author='John Doe',
            quantity=4,
            penalty_fee=20
        )
        
        db.session.add(book)
        db.session.commit()
        
        update_data = {
            'title': None,
            'author': 258,
            'quantity': 10,
            'penalty_fee': 15
        }
        
        retrieved_book = Book.query.filter_by(title='Test Book').first()
        
        response = self.client.put(f'/api/books/update/{retrieved_book.id}',json=update_data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Validation failed.', response.json['Error'])
