from repositories import user_repository as repo
from datetime import datetime
import bcrypt
import re

EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
MIN_PASSWORD_LENGTH = 6


def register_user(email, password):
    """Register a new user with validation."""
    if not email or not email.strip():
        return None, "Email is required."
    
    if not password:
        return None, "Password is required."
    
    email = email.strip().lower()
    
    if not _is_valid_email(email):
        return None, "Invalid email format."
    
    if not _is_valid_password(password):
        return None, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
    
    if repo.email_exists(email):
        return None, "Email already registered."
    
    user_id = _generate_unique_user_id()
    if not user_id:
        return None, "Failed to generate user ID."
    
    try:
        created_user = repo.create_user(
            user_id=user_id,
            email=email,
            password_hash=_hash_password(password),
            created_at=datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        )
        return created_user, None
    except Exception as e:
        return None, f"Failed to create user: {str(e)}"


def authenticate_user(email, password):
    """Authenticate user credentials."""
    if not email or not password:
        return None, "Email and password are required."
    
    email = email.strip().lower()
    
    user = repo.get_user_with_password(email)
    if not user:
        return None, "Invalid email or password."
    
    if not _verify_password(password, user["password_hash"]):
        return None, "Invalid email or password."
    
    return {
        "id": user["id"],
        "email": user["email"],
        "created_at": user["created_at"]
    }, None


def get_user(user_id):
    """Retrieve user by ID."""
    if not user_id:
        return None, "User ID is required."
    
    user = repo.get_user_by_id(user_id)
    return (user, None) if user else (None, "User not found")


def _generate_unique_user_id():
    """Generate unique user ID."""
    user_ids = repo.get_all_user_ids()
    existing_numbers = []
    
    for item in user_ids:
        user_id = item.get("id", "")
        if "_" in user_id:
            try:
                existing_numbers.append(int(user_id.split("_")[1]))
            except (IndexError, ValueError):
                continue
    
    next_number = max(existing_numbers) + 1 if existing_numbers else 1
    return f"user_{next_number}"


def _is_valid_email(email):
    """Validate email format using regex."""
    return bool(re.match(EMAIL_PATTERN, email))


def _is_valid_password(password):
    """Validate password meets minimum requirements."""
    return len(password) >= MIN_PASSWORD_LENGTH


def _hash_password(password):
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def _verify_password(password, password_hash):
    """Verify password matches hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
