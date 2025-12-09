from flask import Flask, render_template, jsonify, request, redirect, url_for
from database import setup_database
from services import todo_service

application = Flask(__name__)

# Initialize database on startup
setup_database.init_db()

@application.route("/")
def home_page():
    return render_template("index.html")

@application.route("/items", methods=["GET"])
def get_all_items():
    status = request.args.get("status")
    items, error = todo_service.get_todo_by_status_filter(status=status)

    if error:
        items = todo_service.get_todo_by_status_filter()
        return jsonify({"success": True, "items": items}), 200
    
    return jsonify({"success": True, "items": items}), 200

@application.route("/items/<item_id>", methods=["GET"])
def search_item(item_id):
    item, error = todo_service.get_todo_by_id(item_id=item_id)
    if error:
        return jsonify({"success": False, "error": error}), 404
    return jsonify({"success": True, "item": item}), 200
 
@application.route("/post_item", methods=["GET", "POST"])
def create_item():
    if request.method == "GET":
        return render_template("post_item.html")

    title = request.form.get("title")
    description = request.form.get("description")
    status = request.form.get("status")

    created_item, error = todo_service.create_todo_item(
        title=title,
        description=description,
        status=status,
        ) 
    
    if error:
        return jsonify({"success": False, "error": error}), 404

    return redirect(url_for("create_item"))

if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=5000)