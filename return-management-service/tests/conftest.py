import pytest
import os
import boto3
from moto import mock_dynamodb

@pytest.fixture(scope='function') # Use 'function' scope if table needs to be reset for each test
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1' # Default region for mock

@pytest.fixture(scope='function')
def dynamodb_table_mock(aws_credentials):
    """Creates a mock DynamoDB table for testing using Moto."""
    # Must import database module here, after moto's context is active
    # and environment variables are set.
    from src import database 
    
    # Set a test table name, can be different from production if needed
    # but using the one from database module ensures it matches what the code expects
    test_table_name = database.DYNAMODB_TABLE_NAME 
    # If database.py uses a dynamic endpoint_url for local testing,
    # ensure it's not set here, or moto might not intercept correctly.
    # For moto, we typically don't set endpoint_url, it mocks the default boto3 client.

    with mock_dynamodb():
        # If database.py has its own client/resource, ensure it's created within mock context
        # or re-initialize it here.
        # For simplicity, let's assume database.py initializes its boto3.resource('dynamodb')
        # and it will be mocked.
        
        # We need to ensure the database module's 'dynamodb' resource and 'table' object
        # are using the mocked environment. This might require reloading the module
        # or carefully structuring database.py to allow reinitialization.
        
        # A common pattern:
        # 1. database.py defines `get_dynamodb_resource` and `get_table` functions.
        # 2. Tests call these functions after mock_dynamodb is active.
        
        # For the current structure of database.py which initializes dynamodb and table at module level:
        # It might be tricky if it's already imported. We might need to reload it,
        # or modify database.py to have an init function for its dynamodb resource.
        
        # Let's assume database.create_dynamodb_table_schema can be used with a mock resource
        mock_db_resource = boto3.resource('dynamodb', region_name='us-east-1')
        try:
            # Use the schema creation function from database.py
            database.create_dynamodb_table_schema(mock_db_resource, test_table_name)
            # Ensure the 'table' object within the database module is now using this mocked table.
            # This is the tricky part with module-level initialization.
            # A robust way is to have database.py provide a function to set/get its table object.
            # E.g., database.init_table(table_name, resource_instance)
            # For now, we'll re-assign it if possible, or rely on it being re-evaluated.
            database.table = mock_db_resource.Table(test_table_name) 
        except Exception as e:
            print(f"Error creating mock table: {e}")
            # This might happen if create_dynamodb_table_schema tries to use the module-level 'dynamodb'
            # which might not be the same as 'mock_db_resource' if not handled carefully.
            # Fallback: create a simple table directly if schema function is problematic in mock
            mock_db_resource.create_table(
                TableName=test_table_name,
                KeySchema=[{'AttributeName': 'return_id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'return_id', 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
            database.table = mock_db_resource.Table(test_table_name)


        yield database.table # Provide the mocked table to tests
        # Teardown (if any) after yield, e.g., deleting table, happens when mock_dynamodb exits

# Fixture to ensure the DYNAMODB_TABLE_NAME env var is set for tests
@pytest.fixture(scope='session', autouse=True)
def set_env_vars():
    os.environ['DYNAMODB_TABLE_NAME'] = 'test-return-requests-table'
    # If other env vars are needed by the app during tests
    # os.environ['LOG_LEVEL'] = 'DEBUG'
