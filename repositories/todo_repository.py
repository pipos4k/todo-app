from database.models import db, Item

def get_all_items(user_id=None, sort_by="id", sort_order="asc"):
    """
    Get all items, optionally filtered by user_id.
    Supports sorting by: id, title, status, timestamp
    
    Flask-SQLAlchemy provides Item.query directly!
    """
    query = Item.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    # Apply sorting
    sort_column = getattr(Item, sort_by, None)
    if sort_column:
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    else:
        # Default sort by id if invalid column
        query = query.order_by(Item.id.asc())
    
    items = query.all()
    return [item.to_dict() for item in items]

def get_items_by_status(status, user_id=None, sort_by="id", sort_order="asc"):
    """
    Get items by status, optionally filtered by user.
    Supports sorting by: id, title, status, timestamp
    """
    query = Item.query.filter_by(status=status)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    # Apply sorting
    sort_column = getattr(Item, sort_by, None)
    if sort_column:
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    else:
        # Default sort by id if invalid column
        query = query.order_by(Item.id.asc())
    
    items = query.all()
    return [item.to_dict() for item in items]

def get_item_by_id(item_id, user_id=None):
    """
    Get item by ID, optionally verifying it belongs to user.
    """
    query = Item.query.filter_by(id=item_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    item = query.first()
    return item.to_dict() if item else None

def get_all_ids(user_id=None):
    """Get all item IDs, optionally filtered by user"""
    query = Item.query.with_entities(Item.id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    ids = query.all()
    return [{'id': item_id[0]} for item_id in ids]

def create_item(item_id, title, description, status, timestamp, user_id):
    """
    Create a new item using ORM.
    """
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
        return item.to_dict()
    except Exception as e:
        db.session.rollback()
        raise e

def delete_item(item_id, user_id=None):
    """
    Delete an item using ORM.
    """
    query = Item.query.filter_by(id=item_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    item = query.first()
    
    if not item:
        return None
    
    item_dict = item.to_dict()
    db.session.delete(item)
    db.session.commit()
    return item_dict

def update_item(item_id, title=None, description=None, status=None, user_id=None):
    """
    Update an item using ORM.
    """
    query = Item.query.filter_by(id=item_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    item = query.first()
    
    if not item:
        return None
    
    if title is not None:
        item.title = title
    if description is not None:
        item.description = description
    if status is not None:
        item.status = status
    
    db.session.commit()
    return item.to_dict()
