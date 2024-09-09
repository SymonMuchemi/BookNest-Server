from flask import jsonify
from app.transactions import transactions_bp


@transactions_bp.app_errorhandler(404)
def bad_request(e):
    """Handle request not found errors.

    Args:
        e (exception): and exception object.

    Returns:
        json: Error message
    """
    return jsonify({
        "Error": "Page not found"
    }), 404


@transactions_bp.app_errorhandler(500)
def bad_request(e):
    """Handle request not found errors.

    Args:
        e (exception): and exception object.

    Returns:
        json: Error message
    """
    return jsonify({
        "Error": "Internal Server Error"
    }), 500
