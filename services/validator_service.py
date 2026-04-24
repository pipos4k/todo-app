from typing import Dict, Any, Set, Optional
import logging

logger = logging.getLogger(__name__)


def validate_fields(data: Dict[str, Any],
                    allowed_fields: Set[str]) -> Optional[str]:

    if not isinstance(data, dict):
        return "Data must be a dictionary."
    unexpected_fields = set(data.keys()) - allowed_fields

    if unexpected_fields:
        return f"Unexpected field(s): {', '.join(sorted(unexpected_fields))}. Allowed fields are: {', '.join(sorted(allowed_fields))}"
    
    return None


def validate_user_registration_data(data: Dict[str, Any]) -> Optional[str]:

    allowed_fields = {"email", "password"}
    return validate_fields(data, allowed_fields)

def validate_user_login_data(data: Dict[str, Any]) -> Optional[str]:

    allowed_fields = {"email", "password"}  
    return validate_fields(data, allowed_fields)


def validate_todo_item_data(data: Dict[str, Any], is_update: bool = False) -> Optional[str]:
  
    allowed_fields = {"title", "description", "status"}
    
    unexpected_error = validate_fields(data, allowed_fields)
    if unexpected_error:
        return unexpected_error
    
    if not is_update:
        if "title" not in data or not data["title"] or not isinstance(data["title"], str):
            return "Title is required and must be a non-empty string."
        
        if not data["title"].strip():
            return "Title cannot be empty or just whitespace."
    
    if "status" in data and data["status"] is not None:
        valid_statuses = {'ToDo', 'InProgress', 'Done'}
        if data["status"] not in valid_statuses:
            return f"Status must be one of: {', '.join(valid_statuses)}"
    
    return None