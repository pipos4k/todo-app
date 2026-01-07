from repositories import todo_repository as repo
from datetime import datetime

def get_todo_by_status_filter(status=None, user_id=None, sort_by="id", sort_order="asc"):
    """
    Get todos filtered by status, for a specific user.
    Now items are user-specific!
    Supports sorting by: id, title, status, timestamp
    """
    if status:
        if not check_status_existence(status=status):
            return None, "Invalid status."    
    
        items = repo.get_items_by_status(status, user_id=user_id, sort_by=sort_by, sort_order=sort_order)
        return items, None
    else:
        items = repo.get_all_items(user_id=user_id, sort_by=sort_by, sort_order=sort_order)
        return items, None

def get_todo_by_id(item_id, user_id=None):
    """
    Get todo by ID, verifying it belongs to the user.
    """
    item = repo.get_item_by_id(item_id, user_id=user_id)
    if not item:
        return None, "Item not found"
    return item, None

def create_todo_item(title, description, status, user_id):
    """
    Create a new todo item for a specific user.
    user_id is now required - items belong to users!
    Handles duplicate ID errors by retrying with a new ID.
    """
    # Default status if not provided
    if not status:
        status = "ToDo"

    if not check_status_existence(status=status):
        return None, "Invalid status."

    timestamp = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    
    # Retry up to 5 times if we get a duplicate ID error
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # Generate new ID
            item_id_result = generate_new_todo_id(user_id=user_id)
            
            # Check if ID generation returned an error tuple
            if isinstance(item_id_result, tuple) and item_id_result[0] is None:
                return None, item_id_result[1] if len(item_id_result) > 1 else "Failed to generate item ID"
            
            item_id = item_id_result
            
            # Try to create the item
            created_item = repo.create_item(
                item_id=item_id,
                title=title,
                description=description,
                status=status,
                timestamp=timestamp,
                user_id=user_id
            )
            return created_item, None
            
        except Exception as e:
            error_str = str(e)
            # Check if it's a duplicate key error
            if "UniqueViolation" in error_str or "duplicate key" in error_str.lower():
                if attempt < max_retries - 1:
                    # Retry with a new ID
                    print(f"Duplicate ID detected, retrying with new ID (attempt {attempt + 1}/{max_retries})...")
                    continue
                else:
                    return None, f"Failed to create item: Could not generate unique ID after {max_retries} attempts. {error_str}"
            else:
                # Some other error, return it
                return None, f"Failed to create item: {error_str}"
    
    return None, "Failed to create item: Maximum retries exceeded"

def generate_new_todo_id(user_id=None):
    """
    Generate a new todo ID that is globally unique.
    Item IDs are globally unique (primary key), not per-user.
    Returns a string ID or raises an exception on error.
    Ensures the ID is unique by checking if it exists globally.
    """
    try:
        # Get all IDs for this user to find the highest number
        user_ids = repo.get_all_ids(user_id=user_id)
        existing_id_numbers = []

        if user_ids:
            for item in user_ids:
                item_id = item.get("id", "")
                if item_id and "_" in item_id:
                    try:
                        num = int(item_id.split("_")[1])
                        existing_id_numbers.append(num)
                    except (IndexError, ValueError):
                        # Skip invalid IDs
                        continue

        # Start with the next number after the user's highest, or 1 if no items
        if existing_id_numbers:
            new_id = max(existing_id_numbers) + 1
        else:
            new_id = 1

        # Check globally if the ID exists (IDs are globally unique, not per-user)
        # Keep incrementing until we find an ID that doesn't exist globally
        proposed_id = f"item_{new_id}"
        existing_item = repo.get_item_by_id(proposed_id, user_id=None)  # Check globally, not per-user
        
        # If ID exists globally, keep incrementing until we find one that doesn't
        max_attempts = 1000  # Safety limit to prevent infinite loops
        attempts = 0
        while existing_item and attempts < max_attempts:
            new_id += 1
            proposed_id = f"item_{new_id}"
            existing_item = repo.get_item_by_id(proposed_id, user_id=None)  # Check globally
            attempts += 1

        if attempts >= max_attempts:
            raise ValueError("Could not generate a unique item ID after many attempts")

        return proposed_id
    except Exception as e:
        # Return error tuple for backward compatibility
        return None, f"Failed to generate item ID: {str(e)}"

def delete_todo_item(item_id, user_id=None):
    """
    Delete a todo item, verifying it belongs to the user.
    """
    item = repo.delete_item(item_id, user_id=user_id)
    if not item:
        return None, "Item not found."
    return item, None

def update_todo_item(item_id, title=None, description=None, status=None, user_id=None):
    """
    Update a todo item, verifying it belongs to the user.
    """
    if status and not check_status_existence(status=status):
        return None, "Invalid status."
            
    updated_item = repo.update_item(item_id, title, description, status, user_id=user_id)

    if not updated_item:
        return None, "Item not found."
    
    return updated_item, None

def check_status_existence(status):
    valid_status = ["ToDo", "InProgress", "Done"]

    if status not in valid_status:
        return False
    else:
        return status
