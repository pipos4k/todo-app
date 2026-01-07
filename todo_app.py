from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from database import setup_database
from services import todo_service
from services import user_service
import os
import traceback

application = Flask(__name__)
CORS(application)  # Enable CORS for all routes

# Initialize database with SQLAlchemy
setup_database.init_db(application)

@application.route("/")
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

def get_user_id_from_request():
    """
    Helper function to get user_id from request.
    In a production app, you'd use sessions or JWT tokens.
    For now, we'll get it from the request headers or body.
    """
    # Try to get from headers first
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        # Try to get from request body
        data = request.get_json() or {}
        user_id = data.get('user_id')
    return user_id

@application.route("/items", methods=["GET"])
def get_all_items():
    """
    Get all items for the authenticated user.
    Now items are user-specific!
    Supports sorting by: id, title, status, timestamp
    """
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({"success": False, "error": "User authentication required. Please login."}), 401
    
    status = request.args.get("status")
    sort_by = request.args.get("sort_by", "id")  # Default sort by id
    sort_order = request.args.get("sort_order", "asc")  # Default ascending
    
    items, error = todo_service.get_todo_by_status_filter(
        status=status, 
        user_id=user_id,
        sort_by=sort_by,
        sort_order=sort_order
    )

    if error:
        return jsonify({"success": False, "error": error}), 400
    
    return jsonify({"success": True, "items": items}), 200

@application.route("/items/<item_id>", methods=["GET"])
def search_item(item_id):
    """
    Get a specific item, verifying it belongs to the user.
    """
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({"success": False, "error": "User authentication required. Please login."}), 401
    
    item, error = todo_service.get_todo_by_id(item_id=item_id, user_id=user_id)

    if error:
        return jsonify({"success": False, "error": error}), 404
    return jsonify({"success": True, "item": item}), 200
 
@application.route("/post_item", methods=["POST"])
def create_item():
    """
    Create a new item for the authenticated user.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided."}), 400

        user_id = get_user_id_from_request()
        
        if not user_id:
            return jsonify({"success": False, "error": "User authentication required. Please login."}), 401

        title = data.get("title")
        description = data.get("description")
        status = data.get("status") or "ToDo"  # Default to "ToDo" if not provided

        created_item, error = todo_service.create_todo_item(
            title=title,
            description=description,
            status=status,
            user_id=user_id
        ) 
        
        if error:
            return jsonify({"success": False, "error": error}), 400

        return jsonify({"success": True, "item": created_item}), 201
    except Exception as e:
        print(f"Error in create_item route: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@application.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    """
    Delete an item, verifying it belongs to the user.
    """
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({"success": False, "error": "User authentication required. Please login."}), 401
    
    item, error = todo_service.delete_todo_item(item_id, user_id=user_id)

    if error:
        return jsonify({"success": False, "error": error}), 404
    
    return jsonify({"success": True, "message": f"Delete success", "item": item}), 200

@application.route("/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    """
    Update an item, verifying it belongs to the user.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided."}), 400

        user_id = get_user_id_from_request()
        
        if not user_id:
            return jsonify({"success": False, "error": "User authentication required. Please login."}), 401

        updated_item, error = todo_service.update_todo_item(
            item_id=item_id,
            title=data.get("title"),
            description=data.get("description"),
            status=data.get("status"),
            user_id=user_id
        )

        if error:
            return jsonify({"success": False, "error": error}), 404
        
        return jsonify({
            "success": True,
            "message": "Item updated successfully",
            "item": updated_item
        }), 200
    except Exception as e:
        print(f"Error in update_item route: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@application.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided."}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required."}), 400

        created_user, error = user_service.register_user(
            email=email,
            password=password
        )
        
        if error:
            return jsonify({"success": False, "error": error}), 400

        return jsonify({"success": True, "user": created_user}), 201
    except Exception as e:
        print(f"Error in register route: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@application.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided."}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required."}), 400

        user, error = user_service.authenticate_user(
            email=email,
            password=password
        )
        
        if error:
            return jsonify({"success": False, "error": error}), 401

        return jsonify({"success": True, "user": user}), 200
    except Exception as e:
        print(f"Error in login route: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@application.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user, error = user_service.get_user_by_id(user_id=user_id)

    if error:
        return jsonify({"success": False, "error": error}), 404
    return jsonify({"success": True, "user": user}), 200

if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=5000)
