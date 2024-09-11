from app import db
from app.transactions import transactions_bp
from datetime import datetime
from flask import jsonify, request
from pydantic import ValidationError
from ..utils import TransactionType, ALLOWED_BORROW_PERIOD
from ..schema import TransactionSchema, BookRequestSchema
from ..models import Transaction, Member, Book

member_error_dict = {
                'Error': 'Cannot get member!'
            }


@transactions_bp.route('/hello', methods=['GET'])
def hello_world():
    """Returns a hello string.

    Returns:
        str: A hello string.
    """
    return 'Hello from transactions.'


# @transactions_bp.route('/create', methods=['POST', 'GET'])
# def create_transaction():
#     """Records a transaction and updates members.debt.

#     Returns:
#         dict: Response message.
#     """
#     data = request.json
    
#     try:
#         transaction_schema = TransactionSchema(**data)
        
#         member_id = transaction_schema.member_id
#         book_id = transaction_schema.book_id
#         transaction_type = transaction_schema.type
#         amount = transaction_schema.amount
        
#         member = Member.query.get(member_id)
#         book = Book.query.get(book_id)
        
#         if member is None or book is None:
#             return jsonify({
#                 'Message': 'Cannot find member or book details'
#             }), 400
        
#         if transaction_type == TransactionType.RETURN and member.debt > 0:
#             member.debt -= amount
#         if transaction_type == TransactionType.ISSUE and book.rental_fee > 0:
#             if member.debt + book.rental_fee > 500:
#                 return jsonify({
#                     'Error': "Member's debt will exceed ksh 500"
#                 }), 400

#             member.debt += book.rental_fee

#         transaction = Transaction(
#             book_id=book_id,
#             member_id=member_id,
#             type=transaction_type,
#             amount=amount,
#             date=transaction_schema.date
#         )

#         db.session.add(member)
#         db.session.add(transaction)
#         db.session.commit()
        
#         return jsonify({
#             'Message': 'Transaction recorded succefully',
#             'transaction': transaction_schema.model_dump(),
#         }), 201

#     except ValidationError as e:
#         return jsonify({
#             'Error': 'Validation failed',
#             'Details': e.errors()
#         }), 400


@transactions_bp.route('/issue_book', methods=['GET', 'POST'])
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
            
        # member = Member.query.get(member_id)
        member = db.session.get(Member, member_id)
        # book = Book.query.get(book_id)
        book = db.session.get(Book, book_id)
        
        if member is None:
            return member_error_dict, 400
        
        if member.books_borrowed >= 3:
            return jsonify({
                'Error': 'Member cannot borrow more than 3 books!'
            }), 400
            
        if book.quantity == 0:
            return jsonify({
                'Error': 'Book not available'
            }), 400
        
        # add a book to the member object
        member.books_borrowed += 1
        book.quantity -= 1
        
        transaction = Transaction(
            book_id = return_schema.book_id,
            member_id = return_schema.member_id,
            type = TransactionType.ISSUE,
        )
        
        db.session.add(member)
        db.session.add(book)
        db.session.add(transaction)
        
        db.session.commit()
        
        return jsonify({
            'Message': 'Book issue recorded successfully',
            'Transaction': return_schema.model_dump()
        })
        
    except ValidationError as e:
        return jsonify({
            'Error': 'Validation failed',
            'Details': e.errors()
        }), 400


@transactions_bp.route('/retrieve_book', methods=['POST', 'GET', 'PUT'])
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
            book_id=book_id,
            member_id=member_id,
            type=TransactionType.ISSUE
            ).first()
        
        if book_record is None:
            return jsonify({
                "Error": 'Cannot retrieve book record.'
            }), 400
                
        # member = Member.query.get(member_id)
        member = db.session.get(Member, member_id)
        # book = Book.query.get(book_id)
        book = db.session.get(Book, book_id)
        
        if member is None:
            return jsonify({
                'Error': 'Cannot get member details from database!'
            }), 400

        if member.debt > 0:
            return jsonify({
                'Error': 'Member must pay pending penalties!'
            }), 400
            
        if book is None:
            return ({
                'Error': 'Connot retrieve book data from the database.'
            }), 400
            
        date_of_issue = book_record.date
        
        # calculate charges
        difference = datetime.now() - date_of_issue
        extra_time = difference.days - ALLOWED_BORROW_PERIOD
        penalty_amount = extra_time * book.penalty_fee
        
        member.debt += penalty_amount
        if member.debt > 500:
            member.debt = 500
        
        book.quantity += 1
        member.books_borrowed -= 1
        
        transaction = Transaction(
                book_id = book_id,
                member_id = member_id,
                type = TransactionType.RETURN,
            )
        
        db.session.merge(book)
        db.session.merge(member)
        
        db.session.add(transaction)
        
        db.session.commit()
        
        return jsonify({
            'Message': 'Recorded return transaction successfully',
            'Transaction': request_schema.model_dump()
        })
        
    except ValidationError as e:
        return jsonify({
            'Error': 'Validation failed',
            'Details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'Message': 'Cannot complete transaction',
            'Error': str(e)
        }), 400
