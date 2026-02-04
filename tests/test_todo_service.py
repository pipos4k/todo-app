import pytest
from unittest.mock import patch, MagicMock
from services import todo_service


class TestTodoCreation:
    """Tests for todo creation functionality."""
    
    def test_create_with_valid_data(self):
        """Should successfully create todo with valid data."""
        with patch('services.todo_service.repo') as mock_repo:
            mock_repo.get_all_ids.return_value = []
            mock_repo.get_item_by_id.return_value = None
            mock_repo.create_item.return_value = {
                "id": "item_1",
                "title": "Test Task",
                "status": "ToDo"
            }
            
            item, error = todo_service.create_todo("Test Task", "Description", "ToDo", "user_1")
            
            assert error is None
            assert item is not None
            assert item["title"] == "Test Task"
    
    def test_create_with_empty_title(self):
        """Should reject creation with empty title."""
        item, error = todo_service.create_todo("", "Description", "ToDo", "user_1")
        
        assert item is None
        assert error == "Title is required."
    
    def test_create_with_whitespace_title(self):
        """Should reject creation with whitespace-only title."""
        item, error = todo_service.create_todo("   ", "Description", "ToDo", "user_1")
        
        assert item is None
        assert error == "Title is required."
    
    def test_create_with_invalid_status(self):
        """Should reject creation with invalid status."""
        item, error = todo_service.create_todo("Test Task", "Description", "InvalidStatus", "user_1")
        
        assert item is None
        assert error == "Invalid status."
    
    def test_create_without_user_id(self):
        """Should reject creation without user ID."""
        item, error = todo_service.create_todo("Test Task", "Description", "ToDo", None)
        
        assert item is None
        assert error == "User ID is required."
    
    def test_create_with_default_status(self):
        """Should use default status when not provided."""
        with patch('services.todo_service.repo') as mock_repo:
            mock_repo.get_all_ids.return_value = []
            mock_repo.get_item_by_id.return_value = None
            mock_repo.create_item.return_value = {
                "id": "item_1",
                "title": "Test Task",
                "status": "ToDo"
            }
            
            item, error = todo_service.create_todo("Test Task", "Description", None, "user_1")
            
            assert error is None
            mock_repo.create_item.assert_called_once()
            call_args = mock_repo.create_item.call_args[1]
            assert call_args["status"] == "ToDo"


class TestTodoRetrieval:
    """Tests for todo retrieval functionality."""
    
    def test_get_todo_by_id(self):
        """Should retrieve todo by ID."""
        with patch('services.todo_service.repo') as mock_repo:
            mock_repo.get_item_by_id.return_value = {
                "id": "item_1",
                "title": "Test Task"
            }
            
            item, error = todo_service.get_todo("item_1", "user_1")
            
            assert error is None
            assert item is not None
    
    def test_get_nonexistent_todo(self):
        """Should handle retrieval of non-existent todo."""
        with patch('services.todo_service.repo') as mock_repo:
            mock_repo.get_item_by_id.return_value = None
            
            item, error = todo_service.get_todo("item_999", "user_1")
            
            assert item is None
            assert error == "Item not found"
    
    def test_get_todo_without_id(self):
        """Should reject retrieval without item ID."""
        item, error = todo_service.get_todo(None, "user_1")
        
        assert item is None
        assert error == "Item ID is required."


class TestTodoUpdate:
    """Tests for todo update functionality."""
    
    def test_update_with_valid_data(self):
        """Should successfully update todo."""
        with patch('services.todo_service.repo') as mock_repo:
            mock_repo.update_item.return_value = {
                "id": "item_1",
                "title": "Updated Task"
            }
            
            item, error = todo_service.update_todo("item_1", "Updated Task", None, None, "user_1")
            
            assert error is None
            assert item is not None
    
    def test_update_with_empty_title(self):
        """Should reject update with empty title."""
        item, error = todo_service.update_todo("item_1", "   ", None, None, "user_1")
        
        assert item is None
        assert error == "Title cannot be empty."
    
    def test_update_with_invalid_status(self):
        """Should reject update with invalid status."""
        item, error = todo_service.update_todo("item_1", None, None, "InvalidStatus", "user_1")
        
        assert item is None
        assert error == "Invalid status."
    
    def test_update_nonexistent_todo(self):
        """Should handle update of non-existent todo."""
        with patch('services.todo_service.repo') as mock_repo:
            mock_repo.update_item.return_value = None
            
            item, error = todo_service.update_todo("item_999", "Updated", None, None, "user_1")
            
            assert item is None
            assert error == "Item not found."


class TestTodoDeletion:
    """Tests for todo deletion functionality."""
    
    def test_delete_existing_todo(self):
        """Should successfully delete existing todo."""
        with patch('services.todo_service.repo') as mock_repo:
            mock_repo.delete_item.return_value = {"id": "item_1"}
            
            item, error = todo_service.delete_todo("item_1", "user_1")
            
            assert error is None
            assert item is not None
    
    def test_delete_nonexistent_todo(self):
        """Should handle deletion of non-existent todo."""
        with patch('services.todo_service.repo') as mock_repo:
            mock_repo.delete_item.return_value = None
            
            item, error = todo_service.delete_todo("item_999", "user_1")
            
            assert item is None
            assert error == "Item not found."
    
    def test_delete_without_id(self):
        """Should reject deletion without item ID."""
        item, error = todo_service.delete_todo(None, "user_1")
        
        assert item is None
        assert error == "Item ID is required."


class TestStatusValidation:
    """Tests for status validation."""
    
    @pytest.mark.parametrize("status,expected", [
        ("ToDo", True),
        ("InProgress", True),
        ("Done", True),
        ("Invalid", False),
        ("todo", False),
        ("", False),
    ])
    def test_status_validation(self, status, expected):
        """Should correctly validate todo status."""
        assert todo_service._is_valid_status(status) == expected


class TestIdGeneration:
    """Tests for ID generation functionality."""
    
    def test_generate_first_id(self):
        """Should generate item_1 for first item."""
        with patch('services.todo_service.repo') as mock_repo:
            mock_repo.get_all_ids.return_value = []
            mock_repo.get_item_by_id.return_value = None
            
            item_id = todo_service._generate_unique_id("user_1")
            
            assert item_id == "item_1"
    
    def test_generate_incremental_id(self):
        """Should generate next sequential ID."""
        with patch('services.todo_service.repo') as mock_repo:
            mock_repo.get_all_ids.return_value = [
                {"id": "item_1"},
                {"id": "item_2"}
            ]
            mock_repo.get_item_by_id.return_value = None
            
            item_id = todo_service._generate_unique_id("user_1")
            
            assert item_id == "item_3"
    
    def test_generate_id_skips_existing(self):
        """Should skip existing IDs when generating new ID."""
        with patch('services.todo_service.repo') as mock_repo:
            mock_repo.get_all_ids.return_value = [{"id": "item_1"}]
            
            call_count = [0]
            def mock_get_item(item_id, user_id):
                call_count[0] += 1
                return {"id": item_id} if call_count[0] == 1 else None
            
            mock_repo.get_item_by_id.side_effect = mock_get_item
            
            item_id = todo_service._generate_unique_id("user_1")
            
            assert item_id == "item_3"
