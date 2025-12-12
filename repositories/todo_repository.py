from database.setup_database import get_db_connection

def get_all_items():
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    db_connection.close()
    return [dict(row) for row in rows]

def get_items_by_status(status):
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM items WHERE status =?", (status,))
    rows = cursor.fetchall()
    db_connection.close()
    return [dict(row) for row in rows]

def get_item_by_id(item_id):
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    db_connection.close()
    return dict(row) if row else None

def get_all_ids():
    db_connection = get_db_connection()    
    cursor = db_connection.cursor()
    cursor.execute("SELECT id FROM items")
    ids = cursor.fetchall()
    db_connection.close()
    return [dict(row) for row in ids]

def create_item(item_id, title, description, status, timestamp):

    db_connection = get_db_connection()    
    cursor = db_connection.cursor()

    cursor.execute('''
        INSERT INTO items (id, title, description, status, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_id, title, description, status, timestamp))
    
    db_connection.commit()
    db_connection.close()
    return {"id": item_id, "title": title, "decription": description,
            "status": status, "timestamp": timestamp}

def delete_item(item_id):
    db_connection = get_db_connection()
    cursor = db_connection.cursor()

    # Check if item exists
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id, ))
    row = cursor.fetchone()

    if not row:
        return None # Item not found
    
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id, ))
    db_connection.commit()
    db_connection.close()

    return dict(row)

def update_item(item_id, title=None, description=None, status=None):

    db_connection = get_db_connection()
    cursor = db_connection.cursor()

    # Check if item exists
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))    
    row = cursor.fetchone()

    if not row:
        db_connection.close()
        return None # Item not found
    
    updates = []
    params = []

    if title is not None:
        updates.append("title = ?")
        params.append(title)

    if description is not None:
        updates.append("description = ?")
        params.append(description)

    if status is not None:
        updates.append("status = ?")
        params.append(status)

    if not updates:
        db_connection.close()
        return dict(row)
    
    params.append(item_id)

    query = f"UPDATE items SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    db_connection.commit()
    
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id, ))
    updated_item = cursor.fetchone()
    db_connection.close()

    return dict(updated_item)
