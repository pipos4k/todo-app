from repositories import todo_repository as repo
from datetime import datetime

def get_todo_by_status_filter(status=None):
    if status:
        if not check_status_existence(status=status):
            return None, "Invalid status."    
    
        items = repo.get_items_by_status(status)
        return items, None
    else:
        items = repo.get_all_items()
        return items, None

def get_todo_by_id(item_id):
    item = repo.get_item_by_id(item_id)
    if not item:
        return None, "Item not found"
    return item, None

def create_todo_item(title, description, status):
    item_id = generate_new_todo_id()
    timestamp = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    if not check_status_existence(status=status):
        return None, "Invalid status."

    try:
        created_item = repo.create_item(
            item_id=item_id,
            title=title,
            description=description,
            status=status,
            timestamp=timestamp
        )
        return created_item, None
    except Exception as e:
        return None, f"Failed to create item: {str(e)}"

def generate_new_todo_id():
    ids = repo.get_all_ids()

    if ids:
        try:
            existing_ids = [int(item["id"].split("_")[1]) for item in ids]    
        except (IndexError, ValueError):             
            return None, f"Index or Value error:{IndexError} | {ValueError}"        

        if existing_ids:
            new_id = max(existing_ids)+1
        else:
            new_id = 1
    else:
        new_id =1

    return f"item_{new_id}"

def delete_todo_item(item_id):
    item = repo.delete_item(item_id)
    if not item:
        return None, "Item not found."
    return item, None

def update_todo_item(item_id, title=None, description=None, status=None):
    if not check_status_existence(status=status):
        return None, "Invalid status."
            
    updated_item = repo.update_item(item_id, title, description, status)

    if not updated_item:
        return None, "Item not found."
    
    return updated_item, None

def check_status_existence(status):
    valid_status = ["ToDo", "InProgress", "Done"]

    if status not in valid_status:
        return False
    else:
        return status