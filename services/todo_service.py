from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any, List
import uuid
import logging

from repositories import todo_repository as repo

logger = logging.getLogger(__name__)

VALID_STATUSES = frozenset(["ToDo", "InProgress", "Done"])

def get_todos(status: Optional[str]= None,
                user_id: Optional[str]= None, 
                sort_by: str= "id",
                sort_order: str= "asc") -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    try:
        if status and not _is_valid_status(status):
            return None, "Invalid status."

        if status:
            items = repo.get_items_by_status(status, user_id, sort_by, sort_order)
        else: 
            items = repo.get_all_items(user_id, sort_by, sort_order)

        return items, None

    except Exception as e:
        logger.error(f"Error in get_todos: {str(e)}")
        return None, f"Error to retrieve items: {str(e)}"


def get_todo(item_id: str,
            user_id: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:

    try:
        if not item_id or not item_id.strip():
            return None, "Item ID is required."

        item_id = item_id.strip()        
        item = repo.get_item_by_id(item_id, user_id)

        return (item, None) if item else (None, "Item not found")

    except Exception as e:
        logger.error(f"Error in get_todo {str(e)}")
        return None, f"Error to get the item: {str(e)}"

def create_todo(title: str, 
                description: Optional[str],
                status: Optional[str],
                user_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:

    try:
        if not title or not title.strip():
            return None, "Title is required."

        if not user_id:
            return None, "User ID is required."

        if status is not None and not _is_valid_status(status):
            return None, "Invalid status."

        todo_id = str(uuid.uuid4())
        title = title.strip()
        description=description.strip() if description else ""
        status=status or "ToDo"
        timestamp = datetime.now(timezone.utc)

        created_item = repo.create_item(
            item_id=todo_id,
            title=title,
            description=description,
            status=status,
            timestamp=timestamp,
            user_id=user_id
        )
        
        logger.info(f"Created todo item {todo_id} for user {user_id}")
        return created_item, None

    except Exception as e:
        logger.error(f"Error in create_todo: {str(e)}")
        return None, f"Failed to create item: {str(e)}"


def delete_todo(item_id: str,
                user_id: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:

    try:
        if not item_id or not item_id.strip():
            return None, "Item ID is required."

        item = repo.delete_item(item_id, user_id)
        return (item, None) if item else (None, "Item not found.")
    
    except Exception as e:
        logger.error(f"Error in delete_todo: {str(e)}")
        return None, f"Failed to delete item: {str(e)}"


def update_todo(item_id: str,
                title: Optional[str] = None, 
                description: Optional[str] = None,
                status: Optional[str] = None, 
                user_id: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:

    try:

        if not item_id or not item_id.strip():
            return None, "Item ID is required."

        if not _is_valid_status(status) and status != None:
            return None, "Invalid status."

        if title is not None:
            title = title.strip()
            if not title:
                return None, "Title cannot be empty."

        if description is not None:
            description = description.strip()

        updated_item = repo.update_item(item_id, title, description, status, user_id)
        return (updated_item, None) if updated_item else (None, "Item not found.")
    
    except Exception as e:
        logger.error(f"Error in update_todo: {str(e)}")
        return None, f"Failed to update item: {str(e)}"


def _is_valid_status(status: str) -> bool:

    return status in VALID_STATUSES
