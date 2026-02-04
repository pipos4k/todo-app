from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from database import setup_database
from services import todo_service, user_service
import os
import traceback

application = Flask(__name__)
CORS(application)

setup_database.init_db(application)


@application.route("/")
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')


@application.route("/items", methods=["GET"])
def get_items():
    try:
        user_id = _extract_user_id()
        if not user_id:
            return _unauthorized_response()
        
        items, error = todo_service.get_todos(
            status=request.args.get("status"),
            user_id=user_id,
            sort_by=request.args.get("sort_by", "id"),
            sort_order=request.args.get("sort_order", "asc")
        )
        
        return _success_response({"items": items}) if not error else _error_response(error)
    except Exception as e:
        return _handle_exception(e, "get_items")


@application.route("/items/<item_id>", methods=["GET"])
def get_item(item_id):
    try:
        user_id = _extract_user_id()
        if not user_id:
            return _unauthorized_response()
        
        item, error = todo_service.get_todo(item_id, user_id)
        
        return (_success_response({"item": item}) if not error 
                else _error_response(error, 404))
    except Exception as e:
        return _handle_exception(e, "get_item")


@application.route("/post_item", methods=["POST"])
def create_item():
    try:
        user_id = _extract_user_id()
        if not user_id:
            return _unauthorized_response()
        
        data = request.get_json()
        if not data:
            return _error_response("No data provided.")
        
        created_item, error = todo_service.create_todo(
            title=data.get("title"),
            description=data.get("description"),
            status=data.get("status"),
            user_id=user_id
        )
        
        return (_success_response({"item": created_item}, 201) if not error 
                else _error_response(error))
    except Exception as e:
        return _handle_exception(e, "create_item")


@application.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    try:
        user_id = _extract_user_id()
        if not user_id:
            return _unauthorized_response()
        
        item, error = todo_service.delete_todo(item_id, user_id)
        
        return (_success_response({"message": "Item deleted", "item": item}) if not error 
                else _error_response(error, 404))
    except Exception as e:
        return _handle_exception(e, "delete_item")


@application.route("/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    try:
        user_id = _extract_user_id()
        if not user_id:
            return _unauthorized_response()
        
        data = request.get_json()
        if not data:
            return _error_response("No data provided.")
        
        updated_item, error = todo_service.update_todo(
            item_id=item_id,
            title=data.get("title"),
            description=data.get("description"),
            status=data.get("status"),
            user_id=user_id
        )
        
        return (_success_response({"message": "Item updated", "item": updated_item}) if not error 
                else _error_response(error, 404))
    except Exception as e:
        return _handle_exception(e, "update_item")


@application.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data:
            return _error_response("No data provided.")
        
        created_user, error = user_service.register_user(
            email=data.get("email"),
            password=data.get("password")
        )
        
        return (_success_response({"user": created_user}, 201) if not error 
                else _error_response(error))
    except Exception as e:
        return _handle_exception(e, "register")


@application.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if not data:
            return _error_response("No data provided.")
        
        user, error = user_service.authenticate_user(
            email=data.get("email"),
            password=data.get("password")
        )
        
        return (_success_response({"user": user}) if not error 
                else _error_response(error, 401))
    except Exception as e:
        return _handle_exception(e, "login")


@application.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user, error = user_service.get_user(user_id)
        
        return (_success_response({"user": user}) if not error 
                else _error_response(error, 404))
    except Exception as e:
        return _handle_exception(e, "get_user")


def _extract_user_id():
    """Extract user ID from request headers or body."""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        data = request.get_json() or {}
        user_id = data.get('user_id')
    return user_id


def _success_response(data, status_code=200):
    """Create standardized success response."""
    return jsonify({"success": True, **data}), status_code


def _error_response(error_message, status_code=400):
    """Create standardized error response."""
    return jsonify({"success": False, "error": error_message}), status_code


def _unauthorized_response():
    """Create unauthorized response."""
    return _error_response("User authentication required. Please login.", 401)


def _handle_exception(exception, route_name):
    """Handle and log exceptions."""
    print(f"Error in {route_name} route: {str(exception)}")
    print(traceback.format_exc())
    return _error_response(f"Server error: {str(exception)}", 500)


if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=5000)
