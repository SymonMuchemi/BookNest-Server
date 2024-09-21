#!/usr/bin/env python
from app import db, create_app
from app.models import Book
from scripts.data import generate_name, generate_title

app = create_app()


def add_books():
    with app.app_context():
        for _ in range(100):
            book = Book(title=generate_title(), author=generate_name(), quantity=10)
            db.session.add(book)

        db.session.commit()


if __name__ == "__main__":
    add_books()
