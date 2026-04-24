from database.models import db, User
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

ALLOWED_SORT_COLUMNS = ['id', 'email', 'created_at']


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:

    try:
        user = User.query.get(user_id)
        return user.to_dict() if user else None
    except Exception as e:
        logger.error(f"Error retrieving user by id {user_id}: {e}")
        return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:

    try:
        user = User.query.filter_by(email=email).first()
        return user.to_dict() if user else None
    except Exception as e: 
        logger.error(f"Error retrieving user by email {email}: {e}")      
        return None  


def get_user_with_password(email: str) -> Optional[Dict[str, Any]]:

    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            return None

        return {
            'id': user.id,
            'email': user.email,
            'password_hash': user.password_hash,
            'created_at': user.created_at
        }
    except Exception as e:
        logger.error(f"Error retrieving user with password for email: {email}: {e}")
        return None


def get_all_user_ids() -> List[Dict[str, str]]:

    try:
        users = User.query.with_entities(User.id).all()
        return [{'id': user_id[0]} for user_id in users]
    except Exception as e:
        logger.error(f"Error retrieving all user IDs: {e}")
        return []


def create_user(user_id: str, email: str, password_hash: str, created_at) -> Optional[Dict[str, Any]]:

    try:
        user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            created_at=created_at
        )
        db.session.add(user)
        db.session.commit()
        logger.info(f"Created new user with id {user_id}")
        return user.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating user {user_id}: {e}")
        return None


def update_user(user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:

    try:
        user = User.query.get(user_id)
        if not user:
             return None
         
        allowed_fields = {"email", "password_hash"}
        for field, value in updates.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        db.session.commit()
        logger.info(f"Updated user {user_id} with fields: {list(updates.keys())}")
        return user.to_dict()

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user {user_id}: {e}")
        return None


def delete_user(user_id: str) -> bool:

    try:
        user = User.query.get(user_id)
        if not user:
            return None
        
        db.session.delete(user)
        db.session.commit()
        logger.info(f"Deleted user {user_id}")
        return True
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting the user {user_id}: {e}")
        return False

def email_exists(email: str) -> bool:

    try:
        return User.query.filter_by(email=email).first() is not None
    except Exception as e:
        logger.error(f"Error cheching email existence for {email}: {e}")
        return False
