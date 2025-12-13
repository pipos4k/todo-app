from flask import Flask, jsonify, request
from database import setup_database
from services import todo_service

application = Flask(__name__)

# Initialize database on startup
setup_database.init_db()

@application.route("/items", methods=["GET"])
def get_all_items():
    status = request.args.get("status")
    items, error = todo_service.get_todo_by_status_filter(status=status)

    if error:
        # items = todo_service.get_todo_by_status_filter()
        return jsonify({"success": True, "items": items}), 400
    
    return jsonify({"success": True, "items": items}), 200

@application.route("/items/<item_id>", methods=["GET"])
def search_item(item_id):
    item, error = todo_service.get_todo_by_id(item_id=item_id)

    if error:
        return jsonify({"success": False, "error": error}), 404
    return jsonify({"success": True, "item": item}), 200
 
@application.route("/post_item", methods=["POST"])
def create_item():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided."}), 400

    title = data.get("title")
    description = data.get("description")
    status = data.get("status")

    created_item, error = todo_service.create_todo_item(
        title = title,
        description = description,
        status = status,
        ) 
    
    if error:
        return jsonify({"success": False, "error": error}), 404

    return jsonify({"success": True, "item": created_item}), 201

@application.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    item, error = todo_service.delete_todo_item(item_id)

    if error:
        return jsonify({"success": False, "error": error}), 404
    
    return jsonify({"success": True, "message": f"Delete success{item}"}), 200

@application.route("/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "Not data provided."}), 400

    updated_item, error = todo_service.update_todo_item(
        item_id = item_id,
        title = data.get("title"),
        description = data.get("description"),
        status = data.get("status"),
    )

    if error:
        return jsonify({"success": False, "error": error}), 404
    
    return jsonify({
        "success": True,
        "message": "Item updated successfully",
        "item": updated_item
    }), 200

if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=5000)
    