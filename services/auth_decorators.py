from functools import wraps
from flask import request, jsonify
import jwt
import logging
import os

from services import user_service

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.error("Error with authorization header!")
            return jsonify({"message:": "Authorization header is missing!"}), 401
        
        parts = auth_header.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            logger.error("Error with token format. Expected 'Bearer <token>.")
            return jsonify({"message": "Invalid token format. Expected 'Bearer <token>'."}), 401
        
        token = parts[1]
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)

            current_user_id = data["user_id"]
            current_user_id, error = user_service.get_user(current_user_id)

            if error or not current_user_id:
                logger.error("")
                return jsonify({"message": "Invalid token: user not found!"}), 401
                        
        except jwt.ExpiredSignatureError:
            logger.error(f"Token has expired: {jwt.ExpiredSignatureError}")
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            logger.error(f"Token is invalid {jwt.InvalidTokenError}")
            return jsonify({"message": "Token is invalid!"}), 401
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return jsonify({'message': 'Token validation failed!'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated