from database.models import db, User

def get_user_by_id(user_id):
    """
    Get user by ID using SQLAlchemy ORM.
    
    Flask-SQLAlchemy provides User.query directly - no need for session!
    """
    user = User.query.filter_by(id=user_id).first()
    return user.to_dict() if user else None

def get_user_by_email(email):
    """Get user by email using ORM"""
    user = User.query.filter_by(email=email).first()
    return user.to_dict() if user else None

def get_user_by_email_with_password(email):
    """Get user by email including password hash (for authentication)"""
    user = User.query.filter_by(email=email).first()
    if user:
        return {
            'id': user.id,
            'email': user.email,
            'password_hash': user.password_hash,
            'created_at': user.created_at
        }
    return None

def get_all_user_ids():
    """Get all user IDs using ORM"""
    users = User.query.with_entities(User.id).all()
    return [{'id': user_id[0]} for user_id in users]

def create_user(user_id, email, password_hash, created_at):
    """
    Create a new user using ORM.
    
    Flask-SQLAlchemy provides db.session directly!
    """
    try:
        user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            created_at=created_at
        )
        db.session.add(user)
        db.session.commit()
        return user.to_dict()
    except Exception as e:
        db.session.rollback()
        raise e

def check_email_exists(email):
    """Check if email exists using ORM"""
    count = User.query.filter_by(email=email).count()
    return count > 0
