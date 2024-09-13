from app import db, create_app
from app.models import Book, Member, Transaction
from scripts.data import generate_name, generate_title

app = create_app()

def add_data():
    with app.app_context():
        for _ in range(100):
            book = Book(
                title=generate_title(),
                author=generate_name(),
                quantity=10
            )
            db.session.add(book)

        for _ in range(10):
            member = Member(
                name=generate_name(),
                debt=0,
                books_borrowed=0
            )
            db.session.add(member)

        db.session.commit()

if __name__ == '__main__':
    add_data()
