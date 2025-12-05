from flask import Flask, render_template, jsonify, request, redirect, url_for
import os, sqlite3
from datetime import datetime

DB_PATH = "/data/todo.db"
application = Flask(__name__)

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    db_connection = sqlite3.connect(DB_PATH)
    cursor = db_connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            timestamp TEXT
        )
    ''')
    db_connection.commit()
    db_connection.close()

def get_db_connection():
    db_connection = sqlite3.connect(DB_PATH)
    db_connection.row_factory = sqlite3.Row
    return db_connection

# Initialize database on startup
init_db()

@application.route("/")
def home_page():
    return render_template("index.html")

@application.route("/items", methods=["GET"])
def get_data():
    status = request.args.get("status")

    db_connection = get_db_connection()
    cursor = db_connection.cursor()

    if status:
        valid_statuses = ["ToDo", "InProgress", "Done"]

        if status not in valid_statuses:
            db_connection.close()

            return jsonify({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            }), 400
        
        cursor.execute("SELECT * FROM items WHERE status = ?", (status,))
    else:
        cursor.execute("SELECT * FROM items")

    rows = cursor.fetchall()
    items = [dict(row) for row in rows]
    db_connection.close()

    return render_template("view_items.html", items=items)

@application.route("/items/<item_id>", methods=["GET"])
def search_item(item_id):
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id, ))
    row = cursor.fetchone()
    db_connection.close()

    if row:
        return jsonify({
            "success": True,
            "item": dict(row)
        }), 200
    else: 
        return jsonify({
            "success": False,
            "item": f"Item with {item_id} not found."
        }), 404 
 
@application.route("/post_element", methods=["GET"])
def show_form():
    return render_template("post_element.html")
# 
@application.route("/post_element", methods=["POST"])
def create_data():
    title = request.form.get("entry1")
    description = request.form.get("entry2")
    status = request.form.get("entry3")
    timestamp = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
 
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("SELECT id FROM items")
    ids = cursor.fetchall()

    if ids:
        existing_id = [int(item["id"].split("_")[1]) for item in ids]
        new_number_id = max(existing_id)+1
    else:
        new_number_id = 1
 
    new_id = f"item_{new_number_id}"
 
    cursor.execute('''
        INSERT INTO items (id, title, description, status, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (new_id, title, description, status, timestamp))

    db_connection.commit()
    db_connection.close()
    
    return redirect(url_for("show_form"))

@application.route("/delete/<item_id>", methods=["POST"])
def delete_item(item_id):
    try:
        db_connection = get_db_connection()
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        db_connection.commit()
    except Exception as e: 
        print(f"Error deleting item: {e}")
    finally:
        db_connection.close()

    return redirect(url_for("show_form"))

if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=5000)