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


@books_bp.route('/create', methods=['POST'])
def create_book():
    """creates a book instance and stores to database.

    Returns:
        dict: dictionary containing status message.
    """
    try:
        book_data = request.json
        
        book_schema = BookSchema(**book_data)
        
        book = Book(
            name=book_schema.name.lower(),
            author=book_schema.author.lower(),
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


@books_bp.route('/get_by_name/<string:name>', methods=['GET'])
def get_by_name(name):
    """Gets books with a given name.

    Args:
        name (str): The name of the book.

    Returns:
        list: a list of all books with the given name.
    """
    query_name = name.lower().replace('_', ' ')
    
    books = Book.query.filter_by(name=query_name).all()
    
    if len(books) > 0:
        return jsonify([{
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'image_url': book.image_url,
            'count': book.count,
            'rental_fee': book.rental_fee
        } for book in books])
    
    else:
        return jsonify({
            'Error': 'Could not find book'
        }), 400


@books_bp.route('/get_by_author/<string:name>')
def get_by_author(name):
    query_author = name.lower().replace('_', ' ')
    
    books = Book.query.filter_by(author=query_author).all()
    
    if len(books) > 0:
        return jsonify([{
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'image_url': book.image_url,
            'count': book.count,
            'rental_fee': book.rental_fee
        } for book in books])
    
    return jsonify({
        'Error': 'Could not find book'
    }), 400
