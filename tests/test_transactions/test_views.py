from unittest import TestCase
from app import create_app, db
from app.models import Member, Transaction, Book
from app.utils import TransactionType
from datetime import datetime, timedelta
from pdb import set_trace

import sys


class TestTransactionRoutes(TestCase):
    def setUp(self):
        """Set up the test client and app context."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.test_member = Member(name="John Doe", debt=0, books_borrowed=0)
        self.test_book = Book(title="The Alchemist", author="Paulo Coelho", quantity=5)

        db.session.add(self.test_member)
        db.session.add(self.test_book)

        db.session.commit()

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_hello_world(self):
        """Test the hello world route."""
        response = self.client.get("/api/transactions/hello")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode("utf-8"), "Hello from transactions.")

    def test_issue_book(self):
        """Check if a member is issued a book."""
        data = {
            "member_id": self.test_member.id,
            "book_id": self.test_book.id,
        }

        response = self.client.post("/api/transactions/issue_book", json=data)
        self.assertEqual(response.status_code, 201)

        record = Transaction.query.filter_by(
            book_id=self.test_book.id, member_id=self.test_member.id
        ).first()

        self.assertIsNotNone(record)
        self.assertEqual(record.type, TransactionType.ISSUE)
        self.assertEqual(record.book_id, self.test_book.id)
        self.assertEqual(record.member_id, self.test_member.id)
        self.assertIsNone(record.returned_on)

        member = db.session.get(Member, self.test_member.id)
        book = db.session.get(Book, self.test_book.id)

        self.assertEqual(member.books_borrowed, 1)
        self.assertEqual(member.debt, 0)
        self.assertEqual(book.quantity, 4)

    def test_issue_book_on_book_already_issued(self):
        """Test the issue book route on a book already issued."""
        data = {
            "member_id": self.test_member.id,
            "book_id": self.test_book.id,
        }

        first_issue_response = self.client.post(
            "/api/transactions/issue_book", json=data
        )
        self.assertEqual(first_issue_response.status_code, 201)

        data = {
            "member_id": self.test_member.id,
            "book_id": self.test_book.id,
        }

        second_issue_response = self.client.post(
            "/api/transactions/issue_book", json=data
        )
        self.assertEqual(second_issue_response.status_code, 400)
        self.assertIn(
            "Book already issued to member", second_issue_response.json["Error"]
        )

    def test_issue_book_on_book_not_available(self):
        """Test the issue book route on a book not available."""
        self.test_book.quantity = 0
        db.session.merge(self.test_book)
        db.session.commit()

        data = {
            "member_id": self.test_member.id,
            "book_id": self.test_book.id,
        }

        response = self.client.post("/api/transactions/issue_book", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Book not available", response.json["Error"])

    def test_issue_book_on_member_with_pending_penalty(self):
        """Test the issue book route on a member with pending penalty."""
        self.test_member.debt = 100
        db.session.merge(self.test_member)
        db.session.commit()

        data = {
            "member_id": self.test_member.id,
            "book_id": self.test_book.id,
        }

        response = self.client.post("/api/transactions/issue_book", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Member must pay pending penalties!", response.json["Error"])

    def test_issue_book_on_member_with_books_borrowed(self):
        """Test the issue book route on a member with books borrowed."""
        self.test_member.books_borrowed = 3
        db.session.merge(self.test_member)
        db.session.commit()

        data = {
            "member_id": self.test_member.id,
            "book_id": self.test_book.id,
        }

        response = self.client.post("/api/transactions/issue_book", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Member cannot borrow more than 3 books!", response.json["Error"])

    def test_issue_book_on_invalid_data(self):
        """Test the issue book route with invalid data."""
        bad_data = {"member_id": sys.maxsize, "book_id": None}

        response = self.client.post("/api/transactions/issue_book", json=bad_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Validation failed", response.json["Error"])

    def test_issue_book_on_invalid_id(self):
        """Test the issue book route with invalid id."""
        data = {"member_id": 1, "book_id": sys.maxsize, "type": "issue"}

        response = self.client.post("/api/transactions/issue_book", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot get book!", response.json["Error"])

    def test_retrieve_book(self):
        """Test the retrieve book route."""
        issue_data = {
            "member_id": self.test_member.id,
            "book_id": self.test_book.id,
        }

        self.client.post("/api/transactions/issue_book", json=issue_data)

        retrieve_data = {
            "member_id": self.test_member.id,
            "book_id": self.test_book.id,
        }

        response = self.client.post(
            "/api/transactions/retrieve_book", json=retrieve_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Return transaction recorded successfully", response.json["Message"]
        )

        record = Transaction.query.filter_by(
            book_id=self.test_book.id, member_id=self.test_member.id
        ).first()

        self.assertIsNotNone(record)
        self.assertEqual(record.type, TransactionType.RETURN)
        self.assertEqual(record.book_id, self.test_book.id)
        self.assertEqual(record.member_id, self.test_member.id)
        self.assertIsNotNone(record.returned_on)
        self.assertEqual(record.charge, 0)
    
    def test_retrieve_book_on_book_not_issued(self):
        """Test the retrieve book route on a book not issued."""
        data = {
            "member_id": self.test_member.id,
            "book_id": self.test_book.id,
        }

        response = self.client.post("/api/transactions/retrieve_book", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Book not issued to member", response.json["Error"])
    
    def test_retrieve_book_on_invalid_member(self):
        """Test the retrieve book route with invalid member."""
        data = {
            "member_id": sys.maxsize,
            "book_id": self.test_book.id,
        }

        response = self.client.post("/api/transactions/retrieve_book", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Book not issued to member!", response.json["Error"])
        
    def test_retrieve_book_on_invalid_book(self):
        """Test the retrieve book route with invalid book."""
        data = {
            "member_id": self.test_member.id,
            "book_id": sys.maxsize,
        }

        response = self.client.post("/api/transactions/retrieve_book", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Book not issued to member!", response.json["Error"])
    
    def test_retrieve_book_on_penalizing_member(self):
        """Test the retrieve book route on a penalizing member."""
        issue_record = Transaction(
            book_id=self.test_book.id,
            member_id=self.test_member.id,
            type=TransactionType.ISSUE,
            issued_on=datetime.now() - timedelta(days=10),
        )
        
        db.session.add(issue_record)
        db.session.commit()
        
        data = {
            "member_id": self.test_member.id,
            "book_id": self.test_book.id,
        }
        
        response = self.client.post("/api/transactions/retrieve_book", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Return transaction recorded successfully", response.json["Message"])
        
        record = Transaction.query.filter_by(
            book_id=self.test_book.id, member_id=self.test_member.id
        ).first()
        
        member = db.session.get(Member, self.test_member.id)
        
        self.assertEqual(record.charge, 30)
        self.assertEqual(record.charge, member.debt)
        self.assertEqual(record.type, TransactionType.RETURN)

    def test_retrieve_book_on_no_penalty(self):
        """Test the retrieve book route on no penalty."""
        issue_record = Transaction(
            book_id=self.test_book.id,
            member_id=self.test_member.id,
            type=TransactionType.ISSUE,
            issued_on=datetime.now() - timedelta(days=5),
        )
        
        db.session.add(issue_record)
        db.session.commit()
        
        data = {
            "member_id": self.test_member.id,
            "book_id": self.test_book.id,
        }
        
        response = self.client.post("/api/transactions/retrieve_book", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Return transaction recorded successfully", response.json["Message"])
        
        record = Transaction.query.filter_by(
            book_id=self.test_book.id, member_id=self.test_member.id
        ).first()
        
        member = db.session.get(Member, self.test_member.id)
        
        self.assertEqual(record.charge, 0)
        self.assertEqual(record.charge, member.debt)
        self.assertEqual(record.type, TransactionType.RETURN)
    
    def test_retrieve_book_on_invalid_data(self):
        """Test the retrieve book route with invalid data."""
        data = {"member_id": sys.maxsize, "book_id": None}

        response = self.client.post("/api/transactions/retrieve_book", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Validation failed", response.json["Error"])
        
    def test_retrieve_book_on_penalizing_member_with_max_debt(self):
        """Test the retrieve book route on a penalizing member with max debt."""
        issue_record = Transaction(
            book_id=self.test_book.id,
            member_id=self.test_member.id,
            type=TransactionType.ISSUE,
            issued_on=datetime.now() - timedelta(days=100),
        )
        
        db.session.add(issue_record)
        db.session.commit()
        
        retrieve_data = {
            "member_id": self.test_member.id,
            "book_id": self.test_book.id,
        }
        
        response = self.client.post("/api/transactions/retrieve_book", json=retrieve_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Return transaction recorded successfully", response.json["Message"])
        
        record = Transaction.query.filter_by(
            book_id=self.test_book.id, member_id=self.test_member.id
        ).first()
        
        member = db.session.get(Member, self.test_member.id)
        
        self.assertEqual(record.charge, 500)
        self.assertEqual(record.charge, member.debt)
        
    def test_retrieve_book_on_invalid_data(self):
        """Test the retrieve book route with invalid data."""
        data = {"member_id": sys.maxsize, "book_id": None}

        response = self.client.post("/api/transactions/retrieve_book", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Validation failed", response.json["Error"])
