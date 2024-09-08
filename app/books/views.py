from flask import request, jsonify
from pydantic import ValidationError
from ..models import Book
from ..schema import BookSchema
from app import db
from app.books import books_bp


@books_bp.route('/hello', methods=['GET'])
def hello_world():
    """return hello world

    Returns:
        str: 'Hello world'
    """
    return 'Hello world'


@books_bp.route('/create_book', methods=['POST'])
def create_book():
    """creates a book instance and stores to database.

    Returns:
        dict: dictionary containing status message.
    """
    try:
        book_data = request.json
        
        book_schema = BookSchema(**book_data)
        
        book = Book(
            name=book_schema.name,
            author=book_schema.author,
            count=book_schema.count,
            image_url=book_schema.image_url,
            rental_fee=book_schema.rental_fee
        )
        # add book data to database
        db.session.add(book)
        db.session.commit()
        
        return jsonify({
            'message': 'Book created succesfully',
            'book': book_schema.model_dump()
        })
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation failed',
            'details': e.errors()
        }), 400
