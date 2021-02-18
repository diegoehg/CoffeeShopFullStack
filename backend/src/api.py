import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

## ROUTES
@app.route('/drinks')
def get_drinks():
    return jsonify({
        "success": True,
        "drinks": [d.short() for d in Drink.query.all()]
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    return jsonify({
        "success": True,
        "drinks": [d.long() for d in Drink.query.all()]
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    data = request.get_json()
    
    try:
        d = Drink(
                title=data['title'],
                recipe=json.dumps(data['recipe'])
        )
        d.insert()

        return jsonify({
            "success": True,
            "drinks": [d.long()]
        })

    except:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):

    d = Drink.query.get_or_404(drink_id)
    data = request.get_json()

    try:
        d.title = data['title']
        d.update()

        return jsonify({
            "success": True,
            "drinks": [d.long()]
        })

    except:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    d = Drink.query.get_or_404(drink_id)

    try:
        d.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        })

    except:
        abort(422)


## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error_handler(e):
    return jsonify({
        "success": False,
        "error": e.status_code,
        "message": e.error
    }), e.status_code
