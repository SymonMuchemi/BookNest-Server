from flask import jsonify
from app.books import books_bp


@books_bp.app_errorhandler(404)
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


@books_bp.app_errorhandler(500)
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
