from flask import Flask, render_template, jsonify, request, redirect, url_for
import os, json

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
    return jsonify({
        "success": True,
        "count": len(data),
        "items": data
    }), 200

@application.route("/post_element", methods=["GET"])
def show_form():
    return render_template("post_element.html")

@application.route("/post_element", methods=["POST"])
def post_element():
    # request.get_json() 
    data = load_data()
    new_id = max([item["id"] for item in data], default=0) +1

    new_item = {
        "id": new_id,
        "name": "test"
    }

    data.append(new_item)
    save_data(data)

    return redirect(url_for("show_form"))

if __name__ == "__main__":
    application.run(debug=True, port=5000)