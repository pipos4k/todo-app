from repositories import todo_repository as repo
from datetime import datetime

VALID_STATUSES = ["ToDo", "InProgress", "Done"]
MAX_ID_GENERATION_ATTEMPTS = 1000
MAX_CREATE_RETRIES = 5


def get_todos(status=None, user_id=None, sort_by="id", sort_order="asc"):
    """Retrieve todos with optional filtering and sorting."""
    if status and not _is_valid_status(status):
        return None, "Invalid status."
    
    items = (repo.get_items_by_status(status, user_id, sort_by, sort_order) 
             if status 
             else repo.get_all_items(user_id, sort_by, sort_order))
    
    return items, None


def get_todo(item_id, user_id=None):
    """Retrieve a single todo by ID."""
    if not item_id:
        return None, "Item ID is required."
    
    item = repo.get_item_by_id(item_id, user_id)
    return (item, None) if item else (None, "Item not found")


def create_todo(title, description, status, user_id):
    """Create a new todo item with automatic ID generation and retry logic."""
    if not title or not title.strip():
        return None, "Title is required."
    
    if not user_id:
        return None, "User ID is required."
    
    status = status or "ToDo"
    
    if not _is_valid_status(status):
        return None, "Invalid status."
    
    timestamp = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    
    for attempt in range(MAX_CREATE_RETRIES):
        try:
            item_id = _generate_unique_id(user_id)
            if not item_id:
                return None, "Failed to generate unique ID."
            
            created_item = repo.create_item(
                item_id=item_id,
                title=title.strip(),
                description=description.strip() if description else "",
                status=status,
                timestamp=timestamp,
                user_id=user_id
            )
            return created_item, None
            
        except Exception as e:
            if _is_duplicate_key_error(e):
                if attempt < MAX_CREATE_RETRIES - 1:
                    print(f"Duplicate ID detected, retrying (attempt {attempt + 1}/{MAX_CREATE_RETRIES})")
                    continue
                return None, f"Could not generate unique ID after {MAX_CREATE_RETRIES} attempts."
            return None, f"Failed to create item: {str(e)}"
    
    return None, "Maximum retries exceeded."


def delete_todo(item_id, user_id=None):
    """Delete a todo item."""
    if not item_id:
        return None, "Item ID is required."
    
    item = repo.delete_item(item_id, user_id)
    return (item, None) if item else (None, "Item not found.")


def update_todo(item_id, title=None, description=None, status=None, user_id=None):
    """Update a todo item."""
    if not item_id:
        return None, "Item ID is required."
    
    if status and not _is_valid_status(status):
        return None, "Invalid status."
    
    if title is not None:
        title = title.strip()
        if not title:
            return None, "Title cannot be empty."
    
    if description is not None:
        description = description.strip()
    
    updated_item = repo.update_item(item_id, title, description, status, user_id)
    return (updated_item, None) if updated_item else (None, "Item not found.")


def _generate_unique_id(user_id):
    """Generate a globally unique item ID."""
    user_item_ids = repo.get_all_ids(user_id)
    existing_numbers = _extract_id_numbers(user_item_ids)
    
    next_number = max(existing_numbers) + 1 if existing_numbers else 1
    
    for attempt in range(MAX_ID_GENERATION_ATTEMPTS):
        proposed_id = f"item_{next_number + attempt}"
        if not repo.get_item_by_id(proposed_id, user_id=None):
            return proposed_id
    
    return None


def _extract_id_numbers(id_dicts):
    """Extract numeric parts from ID strings."""
    numbers = []
    for item in id_dicts:
        item_id = item.get("id", "")
        if "_" in item_id:
            try:
                numbers.append(int(item_id.split("_")[1]))
            except (IndexError, ValueError):
                continue
    return numbers


def _is_valid_status(status):
    """Check if status is valid."""
    return status in VALID_STATUSES


def _is_duplicate_key_error(exception):
    """Check if exception is a duplicate key violation."""
    error_message = str(exception).lower()
    return "uniqueviolation" in error_message or "duplicate key" in error_message
