from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Dict, Any
import jwt
import bcrypt
import re
import logging
import uuid
import os 

from repositories import user_repository as repo

logger = logging.getLogger(__name__)
 
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
MIN_PASSWORD_LENGTH = 2

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def register_user(email: str,
                  password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    
    try:
        normalized_email, error = _check_email_validation(email)
        if error:
            return None, error

        if not password:
            return None, "Password is required."

        if not _is_valid_password(password):
            return None, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."

        email = normalized_email
        user_id = str(uuid.uuid4())        
        password = _hash_password(password)
        created_at = datetime.now(timezone.utc)

        created_user = repo.create_user(
            user_id=user_id,
            email=email,
            password_hash=password,
            created_at=created_at
        )
        logger.info(f"New user registered: {email}")
        return created_user, None
    
    except Exception as e:
        logger.error(f"Error in register_user for email '{email}': {str(e)}")
        return None, f"Failed to register user: {str(e)}"


def authenticate_user(email: str, 
                      password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        if not email or not password:
            return None, "Email and password are required."

        email = email.strip().lower()
        user = repo.get_user_with_password(email)

        if not user:
            logger.warning(f"Authentication failed. no user: {email}")
            return None, "Invalid email or password."

        if not _verify_password(password, user["password_hash"]):
            return None, "Invalid email or password."

        token_payload = {
            "user_id": user["id"],
            "exp": datetime.now(timezone.utc) + timedelta(hours= JWT_EXPIRATION_HOURS)
        }
        
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        logger.info(f"User authenticated successfully: {email}")

        return {
            "user info":{
                "id": user["id"],
                "email": user["email"]
            },
            "token": token
        }, None
        
    except Exception as e:
        logger.error(f"Error in authenticate_user for email: '{email}': {str(e)}")
        return None, f"Failed to authenticate user: {str(e)}"


def get_user(user_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:

    try:
        if not user_id:
            return None, "User ID is required."

        user = repo.get_user_by_id(user_id)

        return (user, None) if user else (None, "User not found")
    
    except Exception as e: 
        logger.error(f"Error in get_user for user_id '{user_id}': {str(e)}")
        return None, f"Failed to get user: {str(e)}"


def _check_email_validation(email: str) -> Tuple[Optional[str], Optional[str]]:

    if not email or not email.strip():
        return None, "Email is required."
    
    normalized_email = email.strip().lower()        
    
    if not bool(re.match(EMAIL_PATTERN, normalized_email)):
        return None, "Invalid email format."    
    
    if repo.email_exists(normalized_email):
        return None, "Email already registered."
    
    return normalized_email, None
    

def _is_valid_password(password: str) -> bool:
    
    return len(password) >= MIN_PASSWORD_LENGTH


def _hash_password(password: str) -> str:
    
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def _verify_password(password: str, password_hash: str) -> bool:
    
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
