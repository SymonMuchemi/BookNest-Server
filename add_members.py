#!/usr/bin/env python
from app import db, create_app
from app.models import Member
from scripts.data import generate_name

app = create_app()


def add_members():
    with app.app_context():
        for _ in range(15):
            member = Member(name=generate_name(), debt=0, books_borrowed=0)
            db.session.add(member)

        db.session.commit()


if __name__ == "__main__":
    add_members()
