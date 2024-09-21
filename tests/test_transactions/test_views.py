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

        self.test_member = Member(name="John Doe", debt=0, books_borrowed=1)
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
        pass

    def test_issue_book_on_invalid_data(self):
        """Test the issue book route with invalid data."""
        pass

    def test_issue_book_on_invalid_id(self):
        """Test the issue book route with invalid id."""
        data = {"member_id": 1, "book_id": sys.maxsize, "type": "issue"}

        response = self.client.post("/api/transactions/issue_book", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot get book!", response.json["Error"])

    def test_retrieve_book(self):
        """Test the retrieve book route."""
        pass

    def test_retrieve_book_on_invalid_data(self):
        """Test the retrieve book route with invalid data."""
        data = {"member_id": sys.maxsize, "book_id": None}

        response = self.client.post("/api/transactions/retrieve_book", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Validation failed", response.json["Error"])

    def test_retrieve_book_updates_member_debt_on_penalty(self):
        """Test the retrieve book route updates member debt on penalty."""
        pass

    def test_penalty_update_on_retrieve_book(self):
        """Test the penalty update on retrieve book route."""
        pass

    def test_retrieve_book_with_no_penalty(self):
        """Test the retrieve book route with no penalty."""
        pass

    def test_get_transactions(self):
        """Test the get transactions route."""
        pass
