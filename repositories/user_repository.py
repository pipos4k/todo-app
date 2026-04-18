from database.models import db, User

ALLOWED_SORT_COLUMNS = ['id', 'email', 'created_at']


def get_user_by_id(user_id):
    
    user = User.query.filter_by(id=user_id).first()
    return user.to_dict() if user else None


def get_user_by_email(email):
    
    user = User.query.filter_by(email=email).first()
    return user.to_dict() if user else None


def get_user_with_password(email):

    user = User.query.filter_by(email=email).first()
    if not user:
        return None
    
    return {
        'id': user.id,
        'email': user.email,
        'password_hash': user.password_hash,
        'created_at': user.created_at
    }


def get_all_user_ids():

    users = User.query.with_entities(User.id).all()
    return [{'id': user_id[0]} for user_id in users]


def create_user(user_id, email, password_hash, created_at):

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


def email_exists(email):
    return User.query.filter_by(email=email).count() > 0
