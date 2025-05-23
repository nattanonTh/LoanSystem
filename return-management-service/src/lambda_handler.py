import json
import logging
import os
from . import return_service # Assuming return_service.py is in the same directory (src)
from . import database # To potentially initialize table name or other settings if needed directly

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Helper to format API Gateway responses
def _build_response(status_code, body, headers=None):
    if headers is None:
        headers = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"} # Add CORS headers
    
    # If body is not a string, serialize it to JSON
    if not isinstance(body, str):
        body = json.dumps(body)
        
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": body,
    }

def handler(event, context):
    """
    Main AWS Lambda handler function.
    Routes requests from API Gateway to the appropriate service functions.
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        http_method = event.get("httpMethod")
        path = event.get("path")
        
        # Ensure DYNAMODB_TABLE_NAME is available for the database layer
        # This could also be set globally when the Lambda instance initializes
        # but ensuring it here can be helpful for clarity or if it's dynamically configured.
        table_name = os.environ.get('DYNAMODB_TABLE_NAME')
        if not table_name:
            logger.error("DYNAMODB_TABLE_NAME environment variable not set.")
            return _build_response(500, {"error": "Server configuration error."})
        
        # Initialize database table (if database.py requires explicit table name setting beyond module load)
        # This depends on how database.py is structured. If it initializes 'table' on load using os.environ, this is fine.
        # If it had a function like database.set_table_name(table_name), you'd call it here.

        resource = path.split('/')[-1] # e.g., 'returns' or a specific return_id
        path_parameters = event.get("pathParameters")
        query_parameters = event.get("queryStringParameters") if event.get("queryStringParameters") else {}
        
        request_body = None
        if event.get("body"):
            try:
                request_body = json.loads(event["body"])
            except json.JSONDecodeError:
                logger.error("Invalid JSON in request body.")
                return _build_response(400, {"error": "Invalid JSON format in request body."})

        # Routing logic
        if path.startswith("/returns"):
            if http_method == "POST" and path == "/returns":
                # Create a new return request
                required_fields = ["order_id", "user_id", "product_id", "reason"]
                if not request_body or not all(field in request_body for field in required_fields):
                    return _build_response(400, {"error": "Missing required fields: order_id, user_id, product_id, reason."})
                
                new_return = return_service.initiate_return_process(
                    order_id=request_body["order_id"],
                    user_id=request_body["user_id"],
                    product_id=request_body["product_id"],
                    reason=request_body["reason"]
                )
                return _build_response(201, new_return)

            elif http_method == "GET":
                if path_parameters and "return_id" in path_parameters:
                    # Get a specific return by ID
                    return_id = path_parameters["return_id"]
                    return_details = return_service.get_return_details(return_id)
                    if return_details:
                        return _build_response(200, return_details)
                    else:
                        return _build_response(404, {"error": f"Return request with ID {return_id} not found."})
                elif path == "/returns":
                    # List all returns, possibly with filters
                    user_id = query_parameters.get("user_id")
                    status = query_parameters.get("status")
                    limit = int(query_parameters.get("limit", 10)) # Default limit to 10
                    # last_evaluated_key needs to be handled carefully (passed as string, parsed to dict)
                    # For simplicity, not fully implementing complex last_evaluated_key parsing from query string here.
                    # It should be passed from client as a JSON stringified dict if used.
                    last_key_str = query_parameters.get("last_evaluated_key")
                    last_evaluated_key = json.loads(last_key_str) if last_key_str else None

                    returns_page = return_service.get_all_returns(
                        user_id=user_id, 
                        status=status, 
                        limit=limit, 
                        # The service layer expects last_evaluated_key as dict, database layer takes it as dict.
                        # The current service layer get_all_returns passes None for last_evaluated_key.
                        # To enable pagination, this handler and the service layer need to correctly pass this.
                        # For now, we'll rely on the service layer's current simplified handling.
                        last_return_id=None # This was 'last_return_id' in service, let's match its expectation if it's simple.
                                            # Or, align service to take 'last_evaluated_key' (dict)
                    )
                    return _build_response(200, returns_page) # returns_page is {'items': [], 'last_evaluated_key': ...}

            elif http_method == "PUT" and path_parameters and "return_id" in path_parameters:
                # Update a return request
                return_id = path_parameters["return_id"]
                if not request_body:
                    return _build_response(400, {"error": "Request body is required for update."})

                status = request_body.get("status")
                # Allow other attributes to be updated too, passed as kwargs to the service
                other_updates = {k: v for k, v in request_body.items() if k != "status"}

                if not status and not other_updates:
                     return _build_response(400, {"error": "Status or other attributes to update are required."})

                updated_return = return_service.update_return_info(return_id, status=status, **other_updates)
                if updated_return:
                    return _build_response(200, updated_return)
                else:
                    # This could be 404 if not found, or based on specific error from service
                    return _build_response(404, {"error": f"Return request with ID {return_id} not found or update failed."})
            
            else:
                return _build_response(405, {"error": f"HTTP method {http_method} not allowed on {path}."})
        else:
            return _build_response(404, {"error": "Resource not found."})

    except ValueError as ve:
        logger.error(f"ValueError: {str(ve)}")
        return _build_response(400, {"error": str(ve)})
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        # Consider more specific error handling for different exception types from service/db layer
        return _build_response(500, {"error": "An internal server error occurred."})

# Example of how you might test this handler locally if you were using something like Flask/FastAPI locally
# For pure Lambda, you'd use 'sam local invoke' or similar tools.
if __name__ == '__main__':
    # This block is for conceptual local testing if you adapt it.
    # It won't run directly as a Lambda function without an event and context.
    
    # Mock event for local testing (e.g., creating a return)
    # Set environment variable for table name
    os.environ['DYNAMODB_TABLE_NAME'] = 'return-requests-table' # Or your test table name
    # Ensure DynamoDB Local is running if database.py points to it for local tests.

    # Example: Create Return
    # test_event_create = {
    #     "httpMethod": "POST",
    #     "path": "/returns",
    #     "body": json.dumps({
    #         "order_id": "order_local_test_123",
    #         "user_id": "user_local_test_456",
    #         "product_id": "product_local_test_789",
    #         "reason": "Local test reason - item damaged"
    #     })
    # }
    # print("Testing POST /returns:")
    # response = handler(test_event_create, None)
    # print(json.dumps(response, indent=2))
    # created_return_id = json.loads(response['body']).get('return_id') if response['statusCode'] == 201 else None

    # if created_return_id:
    #     # Example: Get Return by ID
    #     test_event_get = {
    #         "httpMethod": "GET",
    #         "path": f"/returns/{created_return_id}",
    #         "pathParameters": {"return_id": created_return_id}
    #     }
    #     print(f"\nTesting GET /returns/{created_return_id}:")
    #     response = handler(test_event_get, None)
    #     print(json.dumps(response, indent=2))

    #     # Example: Update Return
    #     test_event_update = {
    #         "httpMethod": "PUT",
    #         "path": f"/returns/{created_return_id}",
    #         "pathParameters": {"return_id": created_return_id},
    #         "body": json.dumps({
    #             "status": "APPROVED",
    #             "notes": "Return approved after local test."
    #         })
    #     }
    #     print(f"\nTesting PUT /returns/{created_return_id}:")
    #     response = handler(test_event_update, None)
    #     print(json.dumps(response, indent=2))

    # # Example: List Returns
    # test_event_list = {
    #     "httpMethod": "GET",
    #     "path": "/returns",
    #     "queryStringParameters": {"limit": "5"}
    # }
    # print("\nTesting GET /returns:")
    # response = handler(test_event_list, None)
    # print(json.dumps(response, indent=2))
    pass
