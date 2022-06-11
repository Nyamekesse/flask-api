
import os
from shutil import ExecError
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Book, db

BOOKS_PER_SHELF = 8


def paginate_books(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    books = [book.format() for book in selection]
    current_books = books[start, end]

    return current_books


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

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
            abort(404)

    # delete a book route
    @app.route('/books/<int:book_id>', methods=['DELETE'])
    def deleteBook(book_id):
        try:
            book = Book.query.filter(Book.id == book_id)
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
            abort(e)

    # create new book route
    @app.route('/books/newbook', methods=['POST'])
    def createNewBook():
        body = request.get_json()

        try:
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
            abort(422)

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
