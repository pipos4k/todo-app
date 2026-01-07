from repositories import user_repository as repo
from datetime import datetime
import bcrypt
import re

def generate_new_user_id():
    ids = repo.get_all_user_ids()

    if ids:
        try:
            existing_ids = [int(item["id"].split("_")[1]) for item in ids]    
        except (IndexError, ValueError):             
            return None, f"Index or Value error:{IndexError} | {ValueError}"        

        if existing_ids:
            new_id = max(existing_ids) + 1
        else:
            new_id = 1
    else:
        new_id = 1

    return f"user_{new_id}"

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password (at least 6 characters)"""
    if not password:
        return False
    return len(password) >= 6

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def register_user(email, password):
    """Register a new user"""
    # Validate email
    if not validate_email(email):
        return None, "Invalid email format."
    
    # Validate password
    if not validate_password(password):
        return None, "Password must be at least 6 characters long."
    
    # Check if email already exists
    if repo.check_email_exists(email):
        return None, "Email already registered."
    
    # Generate unique user ID
    user_id = generate_new_user_id()
    if not user_id:
        return None, "Failed to generate user ID."
    
    # Hash password
    password_hash = hash_password(password)
    timestamp = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    
    try:
        created_user = repo.create_user(
            user_id=user_id,
            email=email,
            password_hash=password_hash,
            created_at=timestamp
        )
        return created_user, None
    except Exception as e:
        return None, f"Failed to create user: {str(e)}"

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    if not email or not password:
        return None, "Email and password are required."
    
    # Get user by email (with password hash for verification)
    user = repo.get_user_by_email_with_password(email)
    if not user:
        return None, "Invalid email or password."
    
    # Verify password
    if not verify_password(password, user["password_hash"]):
        return None, "Invalid email or password."
    
    # Return user without password hash
    return {"id": user["id"], "email": user["email"], "created_at": user["created_at"]}, None

def get_user_by_id(user_id):
    """Get user by ID"""
    user = repo.get_user_by_id(user_id)
    if not user:
        return None, "User not found"
    return user, None
