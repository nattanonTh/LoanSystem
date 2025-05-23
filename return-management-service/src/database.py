import os
import boto3
from botocore.exceptions import ClientError
import logging
import time

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize DynamoDB resource
# It's good practice to get the table name from an environment variable
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'return-requests-table')
# Initialize a DynamoDB resource. If a specific region is not provided,
# it will use the default region configured in your AWS environment.
# For local development with DynamoDB Local, you might need to specify the endpoint_url.
if os.environ.get('AWS_SAM_LOCAL') or os.environ.get('IS_OFFLINE'): # IS_OFFLINE is often used by Serverless Framework
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://docker.for.mac.localhost:8000') # Or 'http://localhost:8000'
else:
    dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def create_return_request(order_id: str, user_id: str, product_id: str, reason: str) -> dict:
    """
    Creates a new return request item in DynamoDB.
    Assumes return_id will be generated or can be the order_id if unique for returns.
    For simplicity, using order_id as return_id if a return is one-to-one with an order.
    If multiple returns per order are possible, a unique return_id (e.g., UUID) is needed.
    Let's assume a unique return_id is required and generate it.
    """
    import uuid
    return_id = str(uuid.uuid4())
    timestamp = int(time.time())
    
    item = {
        'return_id': return_id, # Primary Key
        'order_id': order_id,
        'user_id': user_id,     # Could be a GSI for querying returns by user
        'product_id': product_id,
        'reason': reason,
        'status': 'REQUESTED',  # Initial status
        'created_at': timestamp,
        'updated_at': timestamp,
    }
    
    try:
        table.put_item(Item=item)
        logger.info(f"Created return request {return_id} for order {order_id}")
        return item
    except ClientError as e:
        logger.error(f"Error creating return request for order {order_id}: {e.response['Error']['Message']}")
        raise

def get_return_request_by_id(return_id: str) -> dict | None:
    """Retrieves a return request item by its ID from DynamoDB."""
    try:
        response = table.get_item(Key={'return_id': return_id})
        item = response.get('Item')
        if item:
            logger.info(f"Retrieved return request {return_id}")
        else:
            logger.info(f"Return request {return_id} not found")
        return item
    except ClientError as e:
        logger.error(f"Error retrieving return request {return_id}: {e.response['Error']['Message']}")
        raise

def update_return_request_status(return_id: str, status: str, **other_attributes) -> dict | None:
    """
    Updates the status and other attributes of an existing return request item in DynamoDB.
    Uses UpdateExpression to modify only specified attributes.
    """
    timestamp = int(time.time())
    update_expression_parts = ["SET #status_attr = :status_val", "updated_at = :updated_at_val"]
    expression_attribute_values = {
        ':status_val': status,
        ':updated_at_val': timestamp,
    }
    expression_attribute_names = {
        "#status_attr": "status" # Using placeholder because status is a reserved keyword
    }

    for i, (key, value) in enumerate(other_attributes.items()):
        attr_placeholder = f":attr{i}"
        key_placeholder = f"#key{i}"
        update_expression_parts.append(f"{key_placeholder} = {attr_placeholder}")
        expression_attribute_values[attr_placeholder] = value
        expression_attribute_names[key_placeholder] = key
        
    update_expression = ", ".join(update_expression_parts)

    try:
        response = table.update_item(
            Key={'return_id': return_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues="ALL_NEW"  # Returns all attributes of the item as they appear after the update
        )
        logger.info(f"Updated return request {return_id} to status {status}")
        return response.get('Attributes')
    except ClientError as e:
        logger.error(f"Error updating return request {return_id}: {e.response['Error']['Message']}")
        # ConditionalCheckFailedException can occur if the item does not exist
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            logger.warning(f"Return request {return_id} not found for update.")
            return None
        raise

def list_return_requests(user_id: str = None, status: str = None, limit: int = 10, last_evaluated_key: dict = None) -> dict:
    """
    Lists return requests. Can filter by user_id (if a GSI is set up) or status.
    Implements basic pagination.
    
    Note: Filtering by non-key attributes (like 'status' directly in a scan) is inefficient.
    A GSI on 'status' (status-index) or 'user_id' and 'status' (user-status-index) would be better for production.
    For this example, we'll show a basic scan with optional filtering.
    If 'user_id' is provided, it assumes a GSI named 'UserIndex' with 'user_id' as its hash key.
    """
    scan_kwargs = {'Limit': limit}
    
    if last_evaluated_key:
        scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

    filter_expression_parts = []
    expression_attribute_values = {}
    expression_attribute_names = {} # For reserved keywords

    if status:
        filter_expression_parts.append("#status_attr = :status_val")
        expression_attribute_values[':status_val'] = status
        expression_attribute_names["#status_attr"] = "status"


    # If filtering by user_id, and a GSI 'UserIndex' exists on user_id
    if user_id:
        # If you have a GSI, you'd query it. Example:
        # scan_kwargs['IndexName'] = 'UserIndex' # Replace with your GSI name
        # scan_kwargs['KeyConditionExpression'] = Key('user_id').eq(user_id)
        # If also filtering by status on this GSI (if status is part of sort key or projected):
        #   filter_expression_parts.append("#status_attr = :status_val") (as above)
        # For now, if GSI on user_id is not explicitly defined for query,
        # we add it to the filter expression of a scan (less efficient).
        filter_expression_parts.append("user_id = :user_id_val")
        expression_attribute_values[':user_id_val'] = user_id


    if filter_expression_parts:
        scan_kwargs['FilterExpression'] = " AND ".join(filter_expression_parts)
    
    if expression_attribute_values:
         scan_kwargs['ExpressionAttributeValues'] = expression_attribute_values
    
    if expression_attribute_names:
        scan_kwargs['ExpressionAttributeNames'] = expression_attribute_names

    try:
        if user_id and 'IndexName' in scan_kwargs: # Placeholder for actual GSI query logic
            # response = table.query(**scan_kwargs) # Use query if IndexName and KeyConditionExpression are set
            pass # Replace with actual query
        
        # Fallback to scan if not querying a GSI or no specific index logic implemented yet
        response = table.scan(**scan_kwargs)
        
        items = response.get('Items', [])
        new_last_evaluated_key = response.get('LastEvaluatedKey')
        
        logger.info(f"Listed {len(items)} return requests. Filters: user_id={user_id}, status={status}")
        return {'items': items, 'last_evaluated_key': new_last_evaluated_key}
        
    except ClientError as e:
        logger.error(f"Error listing return requests: {e.response['Error']['Message']}")
        raise

# Example of how to create the table (for reference, not part of runtime code)
# This would typically be done via Infrastructure as Code (SAM, CloudFormation, Serverless Framework)
def create_dynamodb_table_schema(db_resource, table_name):
    """Defines and creates the DynamoDB table if it doesn't exist."""
    try:
        db_resource.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'return_id', 'KeyType': 'HASH'}  # Partition key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'return_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'status', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}, # Adjust as needed
            GlobalSecondaryIndexes=[ # Example GSI for querying by user_id
                {
                    'IndexName': 'UserIndex',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL' # Or 'KEYS_ONLY' or 'INCLUDE'
                    },
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                },
                {
                    'IndexName': 'StatusIndex',
                    'KeySchema': [
                        {'AttributeName': 'status', 'KeyType': 'HASH'}, # GSI on status
                        {'AttributeName': 'created_at', 'KeyType': 'RANGE'} # Optional: sort by creation time
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ]
        )
        logger.info(f"Table {table_name} creating...")
        # Wait until the table exists.
        db_resource.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        logger.info(f"Table {table_name} created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            logger.info(f"Table {table_name} already exists.")
        else:
            logger.error(f"Could not create table {table_name}: {e.response['Error']['Message']}")
            raise

if __name__ == '__main__':
    # This block is for local testing or one-off setup of the table.
    # In a Lambda environment, the table is expected to exist.
    # Ensure AWS credentials and region are configured in your environment.
    print(f"Attempting to ensure table '{DYNAMODB_TABLE_NAME}' exists for local testing...")
    
    # For local development against DynamoDB Local:
    local_dynamodb_client = boto3.resource('dynamodb', endpoint_url='http://localhost:8000') # or your DDB local endpoint
    
    # Check if table exists, otherwise create it
    try:
        local_dynamodb_client.meta.client.describe_table(TableName=DYNAMODB_TABLE_NAME)
        logger.info(f"Table '{DYNAMODB_TABLE_NAME}' already exists locally.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.info(f"Table '{DYNAMODB_TABLE_NAME}' not found locally, creating it...")
            create_dynamodb_table_schema(local_dynamodb_client, DYNAMODB_TABLE_NAME)
        else:
            logger.error(f"Error checking table: {e}")
            raise
    
    # Example usage (optional, for testing this script directly)
    # print("
--- Example Usage ---")
    # test_order_id = "order123"
    # test_user_id = "user456"
    # test_product_id = "product789"
    # test_reason = "Item defective"
    #
    # print(f"1. Creating return request for order {test_order_id}...")
    # new_return = create_return_request(test_order_id, test_user_id, test_product_id, test_reason)
    # if new_return:
    #     test_return_id = new_return['return_id']
    #     print(f"   Return request created with ID: {test_return_id}")
    #
    #     print(f"
2. Getting return request {test_return_id}...")
    #     ret_req = get_return_request_by_id(test_return_id)
    #     if ret_req:
    #         print(f"   Found: {ret_req}")
    #
    #     print(f"
3. Updating return request {test_return_id} status to 'APPROVED'...")
    #     updated_req = update_return_request_status(test_return_id, "APPROVED", notes="Customer contacted, return approved.")
    #     if updated_req:
    #         print(f"   Updated: {updated_req}")
    #
    #     print(f"
4. Listing return requests for user {test_user_id}...")
    #     user_returns = list_return_requests(user_id=test_user_id)
    #     print(f"   Found {len(user_returns['items'])} returns for user: {user_returns['items']}")
    #
    #     print(f"
5. Listing all return requests with status 'APPROVED'...")
    #     approved_returns = list_return_requests(status="APPROVED")
    #     print(f"   Found {len(approved_returns['items'])} approved returns: {approved_returns['items']}")
    # else:
    #     print("   Failed to create return request for example usage.")
    # print("--- End Example Usage ---")
