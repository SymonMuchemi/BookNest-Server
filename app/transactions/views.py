from app import db
from app.transactions import transactions_bp
from flask import jsonify, request
from pydantic import ValidationError
from ..utils import TransactionType
from ..schema import TransactionSchema
from ..models import Transaction, Member, Book


@transactions_bp.route('/hello', methods=['GET'])
def hello_world():
    """Returns a hello string.

    Returns:
        str: A hello string.
    """
    return 'Hello from transactions.'


@transactions_bp.route('/create', methods=['POST', 'GET'])
def create_transaction():
    """Records a transaction and updates members.debt.

    Returns:
        dict: Response message.
    """
    data = request.json
    
    try:
        transaction_schema = TransactionSchema(**data)
        
        member_id = transaction_schema.member_id
        book_id = transaction_schema.book_id
        transaction_type = transaction_schema.type
        amount = transaction_schema.amount
        
        member = Member.query.get(member_id)
        book = Book.query.get(book_id)
        
        if member is None or book is None:
            return jsonify({
                'Message': 'Cannot find member or book details'
            }), 400
        
        if transaction_type == TransactionType.RETURN and member.debt > 0:
            member.debt -= amount
        if transaction_type == TransactionType.ISSUE and book.rental_fee > 0:
            if member.debt + book.rental_fee > 500:
                return jsonify({
                    'Error': "Member's debt will exceed ksh 500"
                }), 400

            member.debt += book.rental_fee

        transaction = Transaction(
            book_id=book_id,
            member_id=member_id,
            type=transaction_type,
            amount=amount,
            date=transaction_schema.date
        )

        db.session.add(member)
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'Message': 'Transaction recorded succefully',
            'transaction': transaction_schema.model_dump(),
        }), 201

    except ValidationError as e:
        return jsonify({
            'error': 'Validation failed',
            'details': e.errors()
        }), 400
