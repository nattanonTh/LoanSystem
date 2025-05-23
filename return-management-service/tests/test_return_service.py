import pytest
from unittest.mock import patch, MagicMock # Using unittest.mock for patching database calls
from src import return_service # The module we're testing
from src import database # To potentially mock its methods

# Test data
TEST_ORDER_ID_SVC = "order_svc_123"
TEST_USER_ID_SVC = "user_svc_456"
TEST_PRODUCT_ID_SVC = "product_svc_789"
TEST_REASON_SVC = "Test reason - service"
TEST_RETURN_ID_SVC = "return_svc_001"

@patch('src.return_service.database') # Patch the database module used by return_service
def test_initiate_return_process_success(mock_db_ops):
    """Test successful initiation of a return process."""
    mock_db_ops.create_return_request.return_value = {
        'return_id': TEST_RETURN_ID_SVC,
        'order_id': TEST_ORDER_ID_SVC,
        'user_id': TEST_USER_ID_SVC,
        'product_id': TEST_PRODUCT_ID_SVC,
        'reason': TEST_REASON_SVC,
        'status': 'REQUESTED',
        'created_at': 1234567890,
        'updated_at': 1234567890
    }
    
    result = return_service.initiate_return_process(
        order_id=TEST_ORDER_ID_SVC,
        user_id=TEST_USER_ID_SVC,
        product_id=TEST_PRODUCT_ID_SVC,
        reason=TEST_REASON_SVC
    )
    
    mock_db_ops.create_return_request.assert_called_once_with(
        order_id=TEST_ORDER_ID_SVC,
        user_id=TEST_USER_ID_SVC,
        product_id=TEST_PRODUCT_ID_SVC,
        reason=TEST_REASON_SVC
    )
    assert result is not None
    assert result['return_id'] == TEST_RETURN_ID_SVC
    assert result['status'] == 'REQUESTED'

@patch('src.return_service.database')
def test_initiate_return_process_missing_fields(mock_db_ops):
    """Test initiate return process with missing required fields."""
    with pytest.raises(ValueError, match="Order ID, User ID, Product ID, and Reason are required."):
        return_service.initiate_return_process(None, TEST_USER_ID_SVC, TEST_PRODUCT_ID_SVC, TEST_REASON_SVC)
    
    mock_db_ops.create_return_request.assert_not_called()

@patch('src.return_service.database')
def test_get_return_details_success(mock_db_ops):
    """Test getting return details successfully."""
    mock_db_ops.get_return_request_by_id.return_value = {
        'return_id': TEST_RETURN_ID_SVC, 'status': 'REQUESTED' # other fields...
    }
    
    result = return_service.get_return_details(TEST_RETURN_ID_SVC)
    
    mock_db_ops.get_return_request_by_id.assert_called_once_with(TEST_RETURN_ID_SVC)
    assert result is not None
    assert result['return_id'] == TEST_RETURN_ID_SVC

@patch('src.return_service.database')
def test_get_return_details_not_found(mock_db_ops):
    """Test getting details for a non-existent return."""
    mock_db_ops.get_return_request_by_id.return_value = None
    
    result = return_service.get_return_details("non_existent_id")
    
    mock_db_ops.get_return_request_by_id.assert_called_once_with("non_existent_id")
    assert result is None

def test_get_return_details_no_id(): # Changed from method to function
    with pytest.raises(ValueError, match="Return ID is required."):
        return_service.get_return_details(None)
    with pytest.raises(ValueError, match="Return ID is required."):
        return_service.get_return_details("")


@patch('src.return_service.database')
def test_update_return_info_success(mock_db_ops):
    """Test successfully updating return information."""
    mock_db_ops.update_return_request_status.return_value = {
        'return_id': TEST_RETURN_ID_SVC, 'status': 'APPROVED', 'notes': 'Updated'
    }
    
    result = return_service.update_return_info(TEST_RETURN_ID_SVC, status='APPROVED', notes='Updated')
    
    mock_db_ops.update_return_request_status.assert_called_once_with(
        TEST_RETURN_ID_SVC, 'APPROVED', notes='Updated'
    )
    assert result is not None
    assert result['status'] == 'APPROVED'
    assert result['notes'] == 'Updated'

@patch('src.return_service.database')
def test_update_return_info_not_found(mock_db_ops):
    """Test updating info for a non-existent return."""
    mock_db_ops.update_return_request_status.return_value = None # Simulate DB layer returning None for not found
    
    result = return_service.update_return_info("non_existent_id", status='APPROVED')
    
    assert result is None

def test_update_return_info_no_id(): # Changed from method to function
    with pytest.raises(ValueError, match="Return ID is required."):
        return_service.update_return_info(None, status="APPROVED")

def test_update_return_info_no_updates_provided(): # Changed from method to function
    # This test depends on whether you want it to fetch the item or raise error/return None
    # Current implementation in return_service.py fetches the item.
    with patch('src.return_service.database.get_return_request_by_id') as mock_get:
        mock_get.return_value = {'return_id': TEST_RETURN_ID_SVC, 'status': 'EXISTING'}
        result = return_service.update_return_info(TEST_RETURN_ID_SVC) # No status or other_updates
        mock_get.assert_called_once_with(TEST_RETURN_ID_SVC)
        assert result['status'] == 'EXISTING'


@patch('src.return_service.database')
def test_get_all_returns_success(mock_db_ops):
    """Test successfully getting all returns."""
    mock_db_ops.list_return_requests.return_value = {
        'items': [{'return_id': 'ret1'}, {'return_id': 'ret2'}],
        'last_evaluated_key': None
    }
    
    result = return_service.get_all_returns(user_id=TEST_USER_ID_SVC, status='REQUESTED', limit=5)
    
    mock_db_ops.list_return_requests.assert_called_once_with(
        user_id=TEST_USER_ID_SVC, status='REQUESTED', limit=5, last_evaluated_key=None # As per current service logic
    )
    assert len(result['items']) == 2
