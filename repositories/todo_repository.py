from database.models import db, Item
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

ALLOWED_SORT_COLUMNS = ["id", "title", "status", "timestamp"]


def get_all_items(user_id: Optional[str] = None, 
                  sort_by: str = "id", 
                  sort_order: str = "asc") -> List[Dict[str, Any]]:
    
    try: 
        item = Item.query
        
        if user_id:
            item = item.filter_by(user_id=user_id)
        
        item = _apply_sorting(item, sort_by, sort_order)
        return [item.to_dict() for item in item.all()]
    except Exception as e:
        logger.error(f"Error retrieving all items for {user_id}: {e}")
        return []


def get_items_by_status(status: str,
                        user_id: Optional[str] = None,
                        sort_by: str = "id",
                        sort_order: str = "asc") -> List[Dict[str, Any]]:

    try:
        item = Item.query.filter_by(status=status)

        if user_id:
            item = item.filter_by(user_id=user_id)

        item = _apply_sorting(item, sort_by, sort_order)
        return [item.to_dict() for item in item.all()]
    except Exception as e:
        logger.error(f"Error retrieving items by status: {status} for user {user_id}: {e}")
        return []


def get_item_by_id(item_id: str,
                    user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:

    try:
        item = Item.query.get(item_id)

        if item and user_id and item.user_id != user_id:
            return None

        return item.to_dict() if item else None
    except Exception as e:
        logger.error(f"Error retrieving item by id: {item_id} for user {user_id}: {e}")
        return None


def get_all_ids(user_id: Optional[str] = None) -> List[Dict[str, str]]:
    try:
        item = Item.query.with_entities(Item.id)

        if user_id:
            item = item.filter_by(user_id=user_id)

        return [{"id": item_id[0]} for item_id in item.all()]
    except Exception as e:
        logger.error(f"Error retrieving all item IDs for user {user_id}: {e}")
        return []

def create_item(item_id: str,
                title: str, 
                description: str, 
                status: str, 
                timestamp, 
                user_id: str) -> Optional[Dict[str, Any]]:
    
    try:
        item = Item(
            id=item_id,
            title=title,
            description=description,
            status=status,
            timestamp=timestamp,
            user_id=user_id
        )
        db.session.add(item)
        db.session.commit()
        logger.info(f"Created new item {item_id} for user {user_id}")
        return item.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating item {item_id} for user {user_id}: {e}")
        return None


def delete_item(item_id: str, 
                user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        item = Item.query.get(item_id)

        if not item or (user_id and item.user_id != user_id):
            return None
        
        item_dict = item.to_dict()
        db.session.delete(item)
        db.session.commit()
        logger.info(f"Deleted item {item_id} for user {user_id}")
        return item_dict
    except Exception as e:
        logger.error(f"Error deleting item {item_id} for user {user_id}: {e}")
        return None

def update_item(item_id: str, 
                title: Optional[str] = None, 
                description: Optional[str] = None, 
                status: Optional[str] = None, 
                user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        item = Item.query.get(item_id)

        if not item or (user_id and item.user_id != user_id):
            return None
                
        updates = [("title", title),
                ("description", description),
                ("status", status)]
        
        for field, value in updates:
            if value is not None:
                logger.info("Try to update item.....")
                setattr(item, field, value)

        db.session.commit()
        logger.info(f"Updated item {item_id} for user {user_id}")
        return item.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating item {item_id} for user {user_id}: {e}")
        return None


def _apply_sorting(item, sort_by: str, sort_order: str):

    if sort_by not in ALLOWED_SORT_COLUMNS:
        sort_by = "id"
    
    sort_column = getattr(Item, sort_by)
    
    if sort_order.lower() == "desc":
        return item.order_by(sort_column.desc())
    return item.order_by(sort_column.asc())
