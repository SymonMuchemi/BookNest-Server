from app import db
from app.books import books_bp
from flask import request, jsonify
from ..schema import BookSchema
from ..models import Book, Transaction

from math import ceil
from pydantic import ValidationError

book_error_dict = {"Error": "Could not find book"}


@books_bp.route("/hello", methods=["GET"])
def hello_world():
    """return hello world

    Returns:
        str: 'Hello world'
    """
    return "Hello world"


@books_bp.route("/create", methods=["POST"])
def create_book():
    """creates a book instance and stores to database.

    Returns:
        dict: dictionary containing status message.
    """
    try:
        book_data = request.get_json()

        book_schema = BookSchema(**book_data)

        book = Book(
            title=book_schema.title.lower(),
            author=book_schema.author.lower(),
            quantity=book_schema.quantity,
            penalty_fee=book_schema.penalty_fee,
        )
        # add book data to database
        db.session.add(book)
        db.session.commit()

        return (
            jsonify(
                {
                    "Message": "Book created succesfully",
                    "book": book_schema.model_dump(),
                }
            ),
            201,
        )

    except ValidationError as e:
        return jsonify({"Error": "Validation failed", "Details": e.errors()}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"Error": str(e)}), 500


@books_bp.route("/get_by_title/<string:string>", methods=["GET"])
def get_by_title(string):
    """Gets books with a given title (in pages).

    Args:
        title (str): The title of the book.

    Returns:
        list: a list of all books with the given title.
    """
    query_title = string.lower().replace("_", " ")

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    books = Book.query.filter(Book.title.like(f"%{query_title}%")).paginate(
        page=page, per_page=per_page
    )

    if books.total == 0:
        return book_error_dict, 400

    total_pages = ceil(books.total / per_page)

    books_list = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "quantity": book.quantity,
            "penalty_fee": book.penalty_fee,
        }
        for book in books
    ]

    return (
        jsonify(
            {
                "total_books": books.total,
                "total_pages": total_pages,
                "pages": books.pages,
                "current_page": page,
                "books": books_list,
                "per_page": per_page,
                "has_next": books.has_next,
                "has_prev": books.has_prev,
                "next_page": books.next_num if books.has_next else None,
                "prev_page": books.prev_num if books.has_prev else None,
            }
        ),
        200,
    )


@books_bp.route("/get_by_author/<string:string>")
def get_by_author(string):
    """Gets a list of books from an author (in pages).

    Args:
        title (str): title of the author.

    Returns:
        list: List of books.
    """
    query_author = string.lower().replace("_", " ")

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    books = Book.query.filter(Book.author.like(f"%{query_author}%")).paginate(
        page=page, per_page=per_page
    )

    if books.total == 0:
        return book_error_dict, 400

    total_pages = ceil(books.total / per_page)

    books_list = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "quantity": book.quantity,
            "penalty_fee": book.penalty_fee,
        }
        for book in books
    ]

    return (
        jsonify(
            {
                "total_books": books.total,
                "total_pages": total_pages,
                "pages": books.pages,
                "current_page": page,
                "books": books_list,
                "per_page": per_page,
                "has_next": books.has_next,
                "has_prev": books.has_prev,
                "next_page": books.next_num if books.has_next else None,
                "prev_page": books.prev_num if books.has_prev else None,
            }
        ),
        200,
    )


@books_bp.route("/update/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    """Updates the details of a book object.

    Args:
        book_id (int): The book's id.

    Returns:
        dict: Response message.
    """
    book_data = request.json

    book = db.session.get(Book, book_id)

    if book is None:
        return book_error_dict, 400

    try:
        book_schema = BookSchema(**book_data)

        book.title = book_schema.title
        book.author = book_schema.author
        book.quantity = book_schema.quantity
        book.penalty_fee = book_schema.penalty_fee

        db.session.commit()

        return (
            jsonify(
                {
                    "Message": "Book updated successfully",
                    "New book": book_schema.model_dump(),
                }
            ),
            200,
        )

    except ValidationError as e:
        return jsonify({"Error": "Validation failed.", "Details": e.errors()}), 400


@books_bp.route("/delete/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    """Deletes a book.

    Args:
        book_id (int): Id of book to delete.

    Returns:
        dict: Response message.
    """
    try:
        book_to_delete = db.session.get(Book, book_id)

        if book_to_delete is None:
            return book_error_dict, 400

        pending_transaction = Transaction.query.filter_by(
            book_id=book_id, type="issue"
        ).first()

        if pending_transaction is not None:
            return jsonify({"Error": "Book has pending transactions"}), 400

        db.session.delete(book_to_delete)
        db.session.commit()

        return jsonify({"Message": "Deletion succesfull!"}), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({"Error": str(e)}), 500


@books_bp.route("/get_books", methods=["GET"])
def get_books():
    """Gets book objects in pages.

    Returns:
        dict: Pagination object with book data as list.
    """
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    books = Book.query.paginate(page=page, per_page=per_page)

    total_pages = ceil(books.total / per_page)

    books_list = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "quantity": book.quantity,
            "penalty_fee": book.penalty_fee,
        }
        for book in books
    ]

    return (
        jsonify(
            {
                "total_books": books.total,
                "total_pages": total_pages,
                "pages": books.pages,
                "current_page": page,
                "books": books_list,
                "per_page": per_page,
                "has_next": books.has_next,
                "has_prev": books.has_prev,
                "next_page": books.next_num if books.has_next else None,
                "prev_page": books.prev_num if books.has_prev else None,
            }
        ),
        200,
    )


@books_bp.route("/get_by_id/<int:book_id>", methods=["GET"])
def get_by_id(book_id):
    """Gets a book by its id.

    Args:
        book_id (int): The book's id.

    Returns:
        dict: The book data.
    """
    book = db.session.get(Book, book_id)

    if book is None:
        return book_error_dict, 400

    return (
        jsonify(
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "quantity": book.quantity,
                "penalty_fee": book.penalty_fee,
            }
        ),
        200,
    )
