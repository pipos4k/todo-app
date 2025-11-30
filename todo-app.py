from flask import Flask, render_template, jsonify, request, redirect, url_for
import os, json
from datetime import datetime

DATA_FILE = "data.json"
application = Flask(__name__)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=2)

@application.route("/")
def home_page():
    return render_template("index.html")

@application.route("/items", methods=["GET"])
def get_data():
    data = load_data()    

    status = request.args.get("status")

    if status:
        valid_statuses = ["ToDo", "InProgress", "Done"]

        if status not in valid_statuses:
            return jsonify({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            }), 400
        
        filitere_items = [item for item in data if item["status"] == status]

        return jsonify({
            "success": True,
            "count": len(filitere_items),
            "status": status,
            "items": filitere_items
        }), 200

    return jsonify({
        "success": True,
        "count": len(data),
        "items": data
    }), 200

@application.route("/items/<item_id>", methods=["GET"])
def search_item(item_id):
    data = load_data()
    item = next((item for item in data if item["id"] == item_id), None)

    if item:
        return jsonify({
            "success": True,
            "item": item
        }), 200
    else: 
        return jsonify({
            "success": False,
            "item": f"Item with {item_id} not found."
        }), 404 

@application.route("/post_element", methods=["GET"])
def show_form():
    return render_template("post_element.html")

@application.route("/post_element", methods=["POST"])
def create_data():
    title = request.form.get("entry1")
    description = request.form.get("entry2")
    status = request.form.get("entry3")
    timestamp = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    data = load_data()

    if data:
        existing_id = [int(item["id"].split("_")[1]) for item in data]
        new_number_id = max(existing_id)+1
    else:
        new_number_id = 1

    new_id = f"item_{new_number_id}"

    new_item = {
        "id": new_id,
        "title": title,
        "description": description,
        "status": status,
        "time": timestamp,
    }

    data.append(new_item)
    save_data(data)

    return redirect(url_for("show_form"))

@application.route("/delete/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    data = load_data()

    index_item = (item for item in data if item["id"] == item_id)

    data.remove(index_item)
    save_data(data)

    return redirect(url_for("show_form"))

if __name__ == "__main__":
    application.run(debug=True, port=5001)