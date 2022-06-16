
from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from models import setup_db, Book

BOOKS_PER_SHELF = 8


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    def paginate_books(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * BOOKS_PER_SHELF
        end = start + BOOKS_PER_SHELF

        books = [book.format() for book in selection]
        current_books = books[start:end]

        return current_books
    # CORS Headers

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # get all books route
    @app.route('/books', methods=['GET'])
    def get_allBooks():
        selection = Book.query.order_by(Book.id).all()
        current_books = paginate_books(request, selection)

        if len(current_books) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'books': current_books,
                'total_books': len(Book.query.all())
            })

    # update book route
    @app.route('/books/<int:book_id>', methods=['PATCH'])
    def update_rating(book_id):

        body = request.get_json()
        print(body)
        try:
            book = Book.query.filter(Book.id == book_id).one_or_none()
            if book == None:
                abort(404)
            if 'rating' in body:
                book.rating = int(body.get('rating'))
            book.update()

            return jsonify({
                'success': True,
                'id': book.id
            })
        except:
            abort(400)

    # delete a book route
    @app.route('/books/<int:book_id>', methods=['DELETE'])
    def deleteBook(book_id):
        try:
            book = Book.query.filter(Book.id == book_id).one_or_none()
            print(book)
            if book == None:
                abort(404)
            else:
                book.delete()
                selection = Book.query.order_by(Book.id).all()
                current_books = paginate_books(request, selection)
                return jsonify({
                    'success': True,
                    'deleted': book_id,
                    'books': current_books,
                    'total_books': len(Book.query.all())
                })
        except Exception as e:
            abort(422)

    # create new book route
    @app.route('/books', methods=['POST'])
    def createNewBook():
        body = request.get_json()
        search = body.get('search')
        try:
            if search:
                selection = Book.query.order_by(Book.id).filter(
                    Book.title.ilike(f'%{search}%'))
                current_books = paginate_books(request, selection)

                return jsonify({'success': True, 'books': current_books, 'total_books': len(selection.all())})
            else:

                newBook = Book(title=body.get('title'), author=body.get('author'),
                               rating=body.get('rating'))
                newBook.insert()
                selection = Book.query.order_by(Book.id).all()
                current_books = paginate_books(request, selection)
                return jsonify({
                    'success': True,
                    'created': newBook.id,
                    'books': current_books,
                    'total_books': len(Book.query.all())
                })
        except:
            abort(405)

    # error handlers

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405
    return app
