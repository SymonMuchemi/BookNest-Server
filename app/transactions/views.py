from app import db
from app.transactions import transactions_bp
from flask import jsonify


@transactions_bp.route('/hello', methods=['GET'])
def hello_world():
    """Returns a hello string.

    Returns:
        str: A hello string.
    """
    return 'Hello from transactions.'
