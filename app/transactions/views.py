from app import db
from app.transactions import transactions_bp
from datetime import datetime
from flask import jsonify, request
from pydantic import ValidationError
from ..utils import TransactionType, ALLOWED_BORROW_PERIOD
from ..schema import BookRequestSchema
from ..models import Transaction, Member, Book
from math import ceil

member_error_dict = {"Error": "Cannot get member!"}
book_error_dict = {"Error": "Cannot get book!"}
transcation_error_dict = {"Error": "Cannot complete transaction"}


@transactions_bp.route("/hello", methods=["GET"])
def hello_world():
    """Returns a hello string.

    Returns:
        str: A hello string.
    """
    return "Hello from transactions."


@transactions_bp.route("/issue_book", methods=["GET", "POST"])
def issue_book():
    """Issues a book to a member if the member is allowed to.

    Returns:
        dict: Dictionary response message.
    """
    data = request.json

    try:
        return_schema = BookRequestSchema(**data)

        member_id = return_schema.member_id
        book_id = return_schema.book_id

        member = db.session.get(Member, member_id)
        book = db.session.get(Book, book_id)

        if member is None:
            return member_error_dict, 400

        if member.books_borrowed >= 3:
            return jsonify({"Error": "Member cannot borrow more than 3 books!"}), 400

        if member.debt > 0:
            return jsonify({"Error": "Member must pay pending penalties!"}), 400

        if book is None:
            return book_error_dict, 400

        if book.quantity == 0:
            return jsonify({"Error": "Book not available"}), 400

        # search for existing transaction
        issue_record = Transaction.query.filter_by(
            book_id=book_id, member_id=member_id, type=TransactionType.ISSUE
        ).first()

        if issue_record is not None:
            return jsonify({"Error": "Book already issued to member"}), 400

        book.quantity -= 1
        member.books_borrowed += 1

        record = Transaction(
            book_id=book_id,
            member_id=member_id,
            type=TransactionType.ISSUE,
        )

        db.session.merge(book)
        db.session.merge(member)
        db.session.add(record)

        db.session.commit()

        return (
            jsonify(
                {
                    "Message": "Book issue recorded successfully",
                    "Transaction": return_schema.model_dump(),
                }
            ),
            201,
        )

    except ValidationError as e:
        return jsonify({"Error": "Validation failed", "Details": e.errors()}), 400


@transactions_bp.route("/retrieve_book", methods=["POST", "GET", "PUT"])
def retrieve_book():
    """Takes record of book returned.

    Returns:
        dict: Dictionary response message.
    """
    data = request.json

    try:
        request_schema = BookRequestSchema(**data)

        book_id = request_schema.book_id
        member_id = request_schema.member_id

        book_record = Transaction.query.filter_by(
            book_id=book_id, member_id=member_id, type=TransactionType.ISSUE
        ).first()

        if book_record is None:
            return jsonify({"Error": "Cannot retrieve book record."}), 400

        member = db.session.get(Member, member_id)
        book = db.session.get(Book, book_id)

        if member is None:
            return jsonify({"Error": "Cannot get member details from database!"}), 400

        if book is None:
            return ({"Error": "Connot retrieve book data from the database."}), 400

        date_of_issue = book_record.date

        # calculate charges
        difference = datetime.now() - date_of_issue
        days = difference.total_seconds() // 86400
        penalty_amount = 0
        if days > ALLOWED_BORROW_PERIOD:
            extra_time = days - ALLOWED_BORROW_PERIOD
            penalty_amount = extra_time * book.penalty_fee

            member.debt += penalty_amount
            if member.debt > 500:
                member.debt = 500

        book.quantity += 1
        member.books_borrowed -= 1

        transaction = Transaction(
            book_id=book_id,
            member_id=member_id,
            type=TransactionType.RETURN,
        )

        db.session.merge(book)
        db.session.merge(member)

        db.session.add(transaction)

        db.session.commit()

        return jsonify(
            {
                "Message": "Recorded return transaction successfully",
                "Penalty": penalty_amount,
                "Transaction": request_schema.model_dump(),
            }
        )

    except ValidationError as e:
        return jsonify({"Error": "Validation failed", "Details": e.errors()}), 400

    except Exception as e:
        return jsonify({"Message": "Cannot complete transaction", "Error": str(e)}), 400


@transactions_bp.route("/get_transactions", methods=["GET"])
def get_all_transactions():
    """Returns all transaction records in pagination.

    Returns:
        dict: Dictionary response message.
    """
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    try:
        transactions = Transaction.query.paginate(page=page, per_page=per_page)

        if transactions.total == 0:
            return jsonify({"Message": "No transactions found"}), 400

        total_pages = ceil(transactions.total / per_page)

        transactions_list = [
            {
                "id": transaction.id,
                "book_id": transaction.book_id,
                "book_title": transaction.book.title,
                "member_id": transaction.member_id,
                "member_name": transaction.member.name,
                "type": transaction.type,
                "date": transaction.date,
            }
            for transaction in transactions
        ]

        return jsonify(
            {
                "total_transactions": transactions.total,
                "total_pages": total_pages,
                "pages": transactions.pages,
                "current_page": page,
                "transactions": transactions_list,
                "per_page": per_page,
                "has_next": transactions.has_next,
                "has_prev": transactions.has_prev,
                "next_page": transactions.next_num if transactions.has_next else None,
                "prev_page": transactions.prev_num if transactions.has_prev else None,
            }
        )
    except Exception as e:
        return jsonify({"Error": str(e)}), 400
