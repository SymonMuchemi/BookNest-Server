from unittest import TestCase
from app import create_app, db
from app.models import Member, Transaction, Book
from app.utils import TransactionType
from datetime import datetime, timedelta

import sys
from pdb import set_trace


class TestTransactionRoutes(TestCase):
    def setUp(self):
        """Set up the test client and app context."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.member = Member(name="John Doe", debt=0, books_borrowed=1)
        self.book = Book(title="The Alchemist", author="Paulo Coelho", quantity=5)

        db.session.add(self.member)
        db.session.add(self.book)

        db.session.commit()

        transaction = Transaction(
            member_id=self.member.id, book_id=self.book.id, type=TransactionType.ISSUE
        )
        db.session.add(transaction)
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
        """Test the issue book route."""

        data = {"member_id": self.member.id, "book_id": self.book.id, "type": "issue"}

        response = self.client.post("/api/transactions/issue_book", json=data)
        self.assertEqual(response.status_code, 200)

        transaction = Transaction.query.first()
        self.assertEqual(transaction.member_id, self.member.id)
        self.assertEqual(transaction.book_id, self.book.id)
        self.assertEqual(transaction.type, "issue")
        self.assertEqual(transaction.date.date(), datetime.now().date())
        self.assertEqual(self.member.books_borrowed, 2)
        self.assertEqual(self.book.quantity, 4)

    def test_issue_book_on_invalid_data(self):
        """Test the issue book route with invalid data."""
        data = {"member_id": None, "book_id": 1, "type": "issue"}

        response = self.client.post("/api/transactions/issue_book", json=data)
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

        data = {"member_id": self.member.id, "book_id": self.book.id}

        response = self.client.post("/api/transactions/retrieve_book", json=data)
        self.assertEqual(response.status_code, 200)

        transaction = Transaction.query.filter_by(
            book_id=self.book.id, member_id=self.member.id, type="return"
        ).first()
        self.assertEqual(transaction.member_id, self.member.id)
        self.assertEqual(transaction.book_id, self.book.id)
        self.assertEqual(transaction.type, "return")
        self.assertEqual(transaction.date.date(), datetime.now().date())
        self.assertEqual(self.member.books_borrowed, 0)
        self.assertEqual(self.book.quantity, 6)

    def test_retrieve_book_on_invalid_data(self):
        """Test the retrieve book route with invalid data."""
        data = {"member_id": sys.maxsize, "book_id": None}

        response = self.client.post("/api/transactions/retrieve_book", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Validation failed", response.json["Error"])

    def test_retrieve_book_updates_member_debt_on_penalty(self):
        """Test the retrieve book route updates member debt on penalty."""

        member = Member(name="Wentworth Miller", debt=0, books_borrowed=0)

        book = Book(title="The Alchemist", author="Paulo Coelho", quantity=5)

        db.session.add_all([member, book])
        db.session.commit()

        # issue book to member and set date to 100 days ago
        transaction = Transaction(
            member_id=member.id,
            book_id=book.id,
            type=TransactionType.ISSUE,
            date=datetime.now() - timedelta(days=100),
        )

        db.session.add(transaction)
        db.session.commit()

        retrieved_member = db.session.get(Member, member.id)
        retrieved_book = db.session.get(Book, book.id)

        retrieved_member.books_borrowed += 1
        retrieved_book.quantity -= 1

        retrieved_transaction = db.session.get(Transaction, transaction.id)

        data = {
            "member_id": retrieved_transaction.member.id,
            "book_id": retrieved_transaction.book.id,
        }

        response = self.client.post("/api/transactions/retrieve_book", json=data)

        # fetch member from database
        member = db.session.get(Member, retrieved_transaction.member.id)

        self.assertEqual(self.book.quantity, 5)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(member.books_borrowed, 0)
        self.assertEqual(member.debt, 500)

    def test_penalty_update_on_retrieve_book(self):
        """Test the penalty update on retrieve book route."""

        member = Member(name="Wentworth Miller", debt=0, books_borrowed=0)

        book = Book(title="The Alchemist", author="Paulo Coelho", quantity=5)

        db.session.add_all([member, book])
        db.session.commit()

        # issue book to member and set date to 10 days ago
        transaction = Transaction(
            member_id=member.id,
            book_id=book.id,
            type=TransactionType.ISSUE,
            date=datetime.now() - timedelta(days=10),
        )

        db.session.add(transaction)
        db.session.commit()

        retrieved_member = db.session.get(Member, member.id)
        retrieved_book = db.session.get(Book, book.id)

        retrieved_member.books_borrowed += 1
        retrieved_book.quantity -= 1

        retrieved_transaction = db.session.get(Transaction, transaction.id)

        data = {
            "member_id": retrieved_transaction.member.id,
            "book_id": retrieved_transaction.book.id,
        }

        response = self.client.post("/api/transactions/retrieve_book", json=data)

        # fetch member from database
        member = db.session.get(Member, retrieved_transaction.member.id)

        self.assertEqual(self.book.quantity, 5)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(member.books_borrowed, 0)
        self.assertEqual(member.debt, 30)

    def test_get_transactions(self):
        """Test the get transactions route."""
        Transaction.query.delete()
        # Create a new book and member
        new_member = Member(name="Jane Doe", debt=0, books_borrowed=0)
        new_book = Book(title="1984", author="George Orwell", quantity=3)

        db.session.add(new_member)
        db.session.add(new_book)
        db.session.commit()

        # Issue the book to the member
        transaction = Transaction(member_id=1, book_id=1, type=TransactionType.ISSUE)
        db.session.add(transaction)
        db.session.commit()

        # Retrieve the transactions
        response = self.client.get("/api/transactions/get_transactions")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["transactions"]), 1)
