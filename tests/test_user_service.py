import pytest
from unittest.mock import patch, MagicMock
from services import user_service


class TestUserRegistration:
    """Tests for user registration functionality."""
    
    def test_register_with_valid_data(self):
        """Should successfully register user with valid email and password."""
        with patch('services.user_service.repo') as mock_repo:
            mock_repo.email_exists.return_value = False
            mock_repo.get_all_user_ids.return_value = []
            mock_repo.create_user.return_value = {"id": "user_1", "email": "test@example.com"}
            
            user, error = user_service.register_user("test@example.com", "password123")
            
            assert error is None
            assert user is not None
            assert user["email"] == "test@example.com"
    
    def test_register_with_empty_email(self):
        """Should reject registration with empty email."""
        user, error = user_service.register_user("", "password123")
        
        assert user is None
        assert error == "Email is required."
    
    def test_register_with_invalid_email_format(self):
        """Should reject registration with invalid email format."""
        user, error = user_service.register_user("invalid-email", "password123")
        
        assert user is None
        assert error == "Invalid email format."
    
    def test_register_with_short_password(self):
        """Should reject registration with password shorter than minimum length."""
        user, error = user_service.register_user("test@example.com", "12345")
        
        assert user is None
        assert "at least" in error.lower()
    
    def test_register_with_existing_email(self):
        """Should reject registration with already registered email."""
        with patch('services.user_service.repo') as mock_repo:
            mock_repo.email_exists.return_value = True
            
            user, error = user_service.register_user("test@example.com", "password123")
            
            assert user is None
            assert error == "Email already registered."


class TestUserAuthentication:
    """Tests for user authentication functionality."""
    
    def test_authenticate_with_valid_credentials(self):
        """Should successfully authenticate with correct credentials."""
        with patch('services.user_service.repo') as mock_repo:
            hashed = user_service._hash_password("password123")
            mock_repo.get_user_with_password.return_value = {
                "id": "user_1",
                "email": "test@example.com",
                "password_hash": hashed,
                "created_at": "05/01/2026, 12:00:00"
            }
            
            user, error = user_service.authenticate_user("test@example.com", "password123")
            
            assert error is None
            assert user is not None
            assert user["email"] == "test@example.com"
            assert "password_hash" not in user
    
    def test_authenticate_with_wrong_password(self):
        """Should reject authentication with incorrect password."""
        with patch('services.user_service.repo') as mock_repo:
            hashed = user_service._hash_password("correctpassword")
            mock_repo.get_user_with_password.return_value = {
                "id": "user_1",
                "email": "test@example.com",
                "password_hash": hashed,
                "created_at": "05/01/2026, 12:00:00"
            }
            
            user, error = user_service.authenticate_user("test@example.com", "wrongpassword")
            
            assert user is None
            assert error == "Invalid email or password."
    
    def test_authenticate_with_nonexistent_email(self):
        """Should reject authentication for non-existent user."""
        with patch('services.user_service.repo') as mock_repo:
            mock_repo.get_user_with_password.return_value = None
            
            user, error = user_service.authenticate_user("nonexistent@example.com", "password123")
            
            assert user is None
            assert error == "Invalid email or password."
    
    def test_authenticate_with_empty_credentials(self):
        """Should reject authentication with empty credentials."""
        user, error = user_service.authenticate_user("", "")
        
        assert user is None
        assert error == "Email and password are required."


class TestEmailValidation:
    """Tests for email validation."""
    
    @pytest.mark.parametrize("email,expected", [
        ("test@example.com", True),
        ("user.name+tag@example.co.uk", True),
        ("invalid", False),
        ("@example.com", False),
        ("test@", False),
        ("test @example.com", False),
    ])
    def test_email_validation(self, email, expected):
        """Should correctly validate various email formats."""
        assert user_service._is_valid_email(email) == expected


class TestPasswordValidation:
    """Tests for password validation."""
    
    @pytest.mark.parametrize("password,expected", [
        ("password123", True),
        ("123456", True),
        ("12345", False),
        ("", False),
    ])
    def test_password_validation(self, password, expected):
        """Should correctly validate password length."""
        assert user_service._is_valid_password(password) == expected
