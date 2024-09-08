from app import db
from app.books import books_bp
from flask import request, jsonify
from ..schema import BookSchema
from ..models import Book

from math import ceil
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

book_error_dict = {
    'Error': 'Could not find book'
}


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
            quantity=book_schema.quantity,
            image_url=book_schema.image_url,
            rental_fee=book_schema.rental_fee
        )
        # add book data to database
        db.session.add(book)
        db.session.commit()
        
        return jsonify({
            'message': 'Book created succesfully',
            'book': book_schema.model_dump()
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation failed',
            'details': e.errors()
        }), 400

    except IntegrityError as e:
        return jsonify({
            'Error': 'Name already exists'
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
            'quantity': book.quantity,
            'rental_fee': book.rental_fee
        } for book in books])
    
    return book_error_dict, 400


@books_bp.route('/get_by_author/<string:name>')
def get_by_author(name):
    """Gets a list of books from an author.

    Args:
        name (str): Name of the author.

    Returns:
        list: List of books.
    """
    query_author = name.lower().replace('_', ' ')
    
    books = Book.query.filter_by(author=query_author).all()
    
    if len(books) > 0:
        return jsonify([{
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'image_url': book.image_url,
            'quantity': book.quantity,
            'rental_fee': book.rental_fee
        } for book in books])
    
    return book_error_dict, 400


@books_bp.route('/update/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Updates the details of a book object.

    Args:
        book_id (int): The book's id.

    Returns:
        dict: Response message.
    """
    book_data = request.json
    
    book = Book.query.get(book_id)

    if book is None:
        return book_error_dict, 400
    
    try:
        book_schema = BookSchema(**book_data)
        
        book.name = book_schema.name
        book.author = book_schema.author
        book.image_url = book_schema.image_url
        book.quantity = book_schema.quantity
        book.rental_fee = book_schema.rental_fee
        
        db.session.commit()
        
        return jsonify({
            "Message": "Book update successfully",
            "New book": book_schema.model_dump()
        })

    except ValidationError as e:
        return jsonify({
            'Error': 'Cannot update book',
            'Details': e.errors()
        }), 400


@books_bp.route('/delete/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book_to_delete = Book.query.get(book_id)
    
    if book_to_delete is None:
        return book_error_dict, 400
    
    db.session.delete(book_to_delete)
    db.session.commit()
    
    return jsonify({
        "Message": "Deletion successfull!"
    }), 200


@books_bp.route('/get_books', methods=['GET'])
def get_books():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    
    books = Book.query.paginate(page=page, per_page=per_page)
    
    total_pages = ceil(books.total / per_page)
    
    books_list = [{
        'id': book.id,
        'name': book.name,
        'author': book.author,
        'image_url': book.image_url,
        'quantity': book.quantity,
        'rental_fee': book.rental_fee
    } for book in books]
    
    return jsonify({
        'total_books': books.total,
        'total_pages': total_pages,
        'pages': books.pages,
        'current_page': page,
        'books': books_list,
        'per_page': per_page,
        'has_next': books.has_next,
        'has_prev': books.has_prev,
        'next_page': books.next_num if books.has_next else None,
        'prev_page': books.prev_num if books.has_prev else None
    }), 200
