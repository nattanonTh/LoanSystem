import pytest
from src import database # The module we're testing
from botocore.exceptions import ClientError
import time

# Test data
TEST_ORDER_ID = "order_db_123"
TEST_USER_ID = "user_db_456"
TEST_PRODUCT_ID = "product_db_789"
TEST_REASON = "Test reason - database"

def test_create_return_request(dynamodb_table_mock):
    """Test creating a new return request."""
    # dynamodb_table_mock fixture ensures table is created in mock DDB
    # and that database.table is pointing to this mock table.
    
    created_item = database.create_return_request(
        order_id=TEST_ORDER_ID,
        user_id=TEST_USER_ID,
        product_id=TEST_PRODUCT_ID,
        reason=TEST_REASON
    )
    assert created_item is not None
    assert created_item['order_id'] == TEST_ORDER_ID
    assert created_item['user_id'] == TEST_USER_ID
    assert created_item['status'] == 'REQUESTED'
    assert 'return_id' in created_item
    assert 'created_at' in created_item
    assert 'updated_at' in created_item

    # Verify it's in the (mocked) table
    retrieved = dynamodb_table_mock.get_item(Key={'return_id': created_item['return_id']})
    assert 'Item' in retrieved
    assert retrieved['Item']['order_id'] == TEST_ORDER_ID

def test_get_return_request_by_id(dynamodb_table_mock):
    """Test retrieving a return request by its ID."""
    # First, create an item to retrieve
    item_to_create = {
        'return_id': 'test_get_id_001',
        'order_id': TEST_ORDER_ID,
        'user_id': TEST_USER_ID,
        'product_id': TEST_PRODUCT_ID,
        'reason': 'For get_by_id test',
        'status': 'REQUESTED',
        'created_at': int(time.time()),
        'updated_at': int(time.time())
    }
    dynamodb_table_mock.put_item(Item=item_to_create)

    retrieved_item = database.get_return_request_by_id('test_get_id_001')
    assert retrieved_item is not None
    assert retrieved_item['return_id'] == 'test_get_id_001'
    assert retrieved_item['order_id'] == TEST_ORDER_ID

def test_get_return_request_by_id_not_found(dynamodb_table_mock):
    """Test retrieving a non-existent return request."""
    retrieved_item = database.get_return_request_by_id('non_existent_id_123')
    assert retrieved_item is None

def test_update_return_request_status(dynamodb_table_mock):
    """Test updating the status of a return request."""
    return_id = 'test_update_id_002'
    initial_item = {
        'return_id': return_id,
        'order_id': TEST_ORDER_ID,
        'user_id': TEST_USER_ID,
        'product_id': TEST_PRODUCT_ID,
        'reason': 'For update_status test',
        'status': 'REQUESTED',
        'created_at': int(time.time()),
        'updated_at': int(time.time())
    }
    dynamodb_table_mock.put_item(Item=initial_item)

    updated_item = database.update_return_request_status(return_id, 'APPROVED', notes='Approved for test')
    assert updated_item is not None
    assert updated_item['return_id'] == return_id
    assert updated_item['status'] == 'APPROVED'
    assert updated_item['notes'] == 'Approved for test' # Assuming 'notes' is an 'other_attribute'
    assert updated_item['updated_at'] > initial_item['updated_at']

    # Verify in table
    retrieved = dynamodb_table_mock.get_item(Key={'return_id': return_id})
    assert retrieved['Item']['status'] == 'APPROVED'
    assert retrieved['Item']['notes'] == 'Approved for test'


def test_update_return_request_status_not_found(dynamodb_table_mock):
    """Test updating a non-existent return request."""
    updated_item = database.update_return_request_status('non_existent_for_update', 'APPROVED')
    assert updated_item is None # Or handle ClientError if it raises instead of returning None

def test_list_return_requests_basic(dynamodb_table_mock):
    """Test listing return requests with no filters (basic scan)."""
    # Add some items
    items_to_add = [
        {'return_id': f'list_item_{i}', 'order_id': f'order_{i}', 'user_id': 'user_list_test', 
         'product_id': 'prod_list', 'reason': 'list test', 'status': 'REQUESTED', 
         'created_at': int(time.time()), 'updated_at': int(time.time())}
        for i in range(3)
    ]
    for item in items_to_add:
        dynamodb_table_mock.put_item(Item=item)

    result = database.list_return_requests(limit=5)
    assert len(result['items']) >= 3 # Could be more if other tests added items and table is not reset
    assert 'last_evaluated_key' in result # Will be None if less than limit and no more items

def test_list_return_requests_with_status_filter(dynamodb_table_mock):
    """Test listing with status filter."""
    # Clear table or use unique statuses for this test if table is not reset per test
    # For simplicity, assuming other tests don't interfere with 'APPROVED_LIST_TEST' status
    ts = int(time.time())
    items_data = [
        {'return_id': 'status_filter_1', 'status': 'APPROVED_LIST_TEST', 'user_id': 'u1', 'order_id': 'o1', 'product_id': 'p1', 'reason': 'r1', 'created_at': ts, 'updated_at': ts},
        {'return_id': 'status_filter_2', 'status': 'REQUESTED_LIST_TEST', 'user_id': 'u2', 'order_id': 'o2', 'product_id': 'p2', 'reason': 'r2', 'created_at': ts, 'updated_at': ts},
        {'return_id': 'status_filter_3', 'status': 'APPROVED_LIST_TEST', 'user_id': 'u3', 'order_id': 'o3', 'product_id': 'p3', 'reason': 'r3', 'created_at': ts, 'updated_at': ts},
    ]
    for item in items_data:
        dynamodb_table_mock.put_item(Item=item)
    
    result = database.list_return_requests(status='APPROVED_LIST_TEST', limit=5)
    assert len(result['items']) == 2
    for item in result['items']:
        assert item['status'] == 'APPROVED_LIST_TEST'

# Note: Testing list_return_requests with user_id filter would require GSI setup in mock.
# The current create_dynamodb_table_schema in database.py includes GSIs.
# The conftest.py's dynamodb_table_mock fixture uses this schema function.
def test_list_return_requests_with_user_id_filter(dynamodb_table_mock):
    """Test listing with user_id filter (assumes GSI 'UserIndex' is mocked)."""
    ts = int(time.time())
    target_user_id = "user_gsi_test_123"
    other_user_id = "user_gsi_test_other"
    items_data = [
        {'return_id': 'user_filter_1', 'status': 'S1', 'user_id': target_user_id,    'order_id': 'o1', 'product_id': 'p1', 'reason': 'r1', 'created_at': ts, 'updated_at': ts},
        {'return_id': 'user_filter_2', 'status': 'S2', 'user_id': other_user_id,     'order_id': 'o2', 'product_id': 'p2', 'reason': 'r2', 'created_at': ts, 'updated_at': ts},
        {'return_id': 'user_filter_3', 'status': 'S3', 'user_id': target_user_id,    'order_id': 'o3', 'product_id': 'p3', 'reason': 'r3', 'created_at': ts, 'updated_at': ts},
    ]
    for item in items_data:
        dynamodb_table_mock.put_item(Item=item)

    # The database.list_return_requests uses a Scan with FilterExpression if IndexName is not specified.
    # To test GSI query, database.py would need to be modified to use table.query with IndexName.
    # For now, this tests the filter expression part of the scan for user_id.
    result = database.list_return_requests(user_id=target_user_id, limit=5)
    assert len(result['items']) == 2
    for item in result['items']:
        assert item['user_id'] == target_user_id
