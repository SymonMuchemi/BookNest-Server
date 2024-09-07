from app.books import books_bp

@books_bp.route('/hello', methods=['GET'])
def hello_world():
    return 'Hello world'
