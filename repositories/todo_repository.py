from database.models import db, Item

ALLOWED_SORT_COLUMNS = ['id', 'title', 'status', 'timestamp']

def get_all_items(user_id=None, sort_by="id", sort_order="asc"):

    query = Item.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    query = _apply_sorting(query, sort_by, sort_order)
    return [item.to_dict() for item in query.all()]


def get_items_by_status(status, user_id=None, sort_by="id", sort_order="asc"):

    query = Item.query.filter_by(status=status)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    query = _apply_sorting(query, sort_by, sort_order)
    return [item.to_dict() for item in query.all()]


def get_item_by_id(item_id, user_id=None):

    query = Item.query.filter_by(id=item_id)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    item = query.first()
    return item.to_dict() if item else None


def get_all_ids(user_id=None):

    query = Item.query.with_entities(Item.id)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    return [{'id': item_id[0]} for item_id in query.all()]


def create_item(item_id, title, description, status, timestamp, user_id):
    
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


def _apply_sorting(query, sort_by, sort_order):

    if sort_by not in ALLOWED_SORT_COLUMNS:
        sort_by = "id"
    
    sort_column = getattr(Item, sort_by)
    
    if sort_order.lower() == "desc":
        return query.order_by(sort_column.desc())
    return query.order_by(sort_column.asc())
