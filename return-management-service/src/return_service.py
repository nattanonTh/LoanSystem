import logging
from . import database # Assuming database.py is in the same directory

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def initiate_return_process(order_id: str, user_id: str, product_id: str, reason: str) -> dict:
    """
    Handles the business logic for initiating a new return request.
    - Validates input (basic validation for now).
    - Calls the database layer to create the return request.
    """
    if not all([order_id, user_id, product_id, reason]):
        logger.warning("Missing one or more required fields for initiating return.")
        # In a real app, you might raise a custom ValueError or return a specific error structure
        raise ValueError("Order ID, User ID, Product ID, and Reason are required.")

    # Potentially more complex validation or checks can go here, e.g.:
    # - Check if the order exists and is eligible for return
    # - Check if the user is authorized to return this product for this order
    # - Check if product is returnable, within return window etc.
    
    logger.info(f"Attempting to create return request for order_id: {order_id}, user_id: {user_id}")
    try:
        new_return_request = database.create_return_request(
            order_id=order_id,
            user_id=user_id,
            product_id=product_id,
            reason=reason
        )
        # Potentially trigger other processes here, like sending a notification
        logger.info(f"Successfully initiated return with ID: {new_return_request.get('return_id')}")
        return new_return_request
    except Exception as e:
        logger.error(f"Error in initiate_return_process for order_id {order_id}: {str(e)}")
        # Depending on API design, re-raise or return an error object
        raise 

def get_return_details(return_id: str) -> dict | None:
    """
    Retrieves details for a specific return request.
    """
    if not return_id:
        logger.warning("Return ID is required to fetch details.")
        raise ValueError("Return ID is required.")
        
    logger.info(f"Fetching details for return_id: {return_id}")
    try:
        return_request = database.get_return_request_by_id(return_id)
        if not return_request:
            logger.warning(f"No return request found for return_id: {return_id}")
            return None # Or raise a NotFoundError
        return return_request
    except Exception as e:
        logger.error(f"Error in get_return_details for return_id {return_id}: {str(e)}")
        raise

def update_return_info(return_id: str, status: str = None, **other_updates) -> dict | None:
    """
    Updates the information for a return request, primarily its status.
    'other_updates' can include notes, shipping info, etc.
    """
    if not return_id:
        logger.warning("Return ID is required to update details.")
        raise ValueError("Return ID is required.")

    if not status and not other_updates:
        logger.warning(f"No updates provided for return_id: {return_id}.")
        # Or return the existing item without changes
        return get_return_details(return_id)

    # Business logic for status transitions can be added here.
    # For example, ensure status transitions are valid (e.g., REQUESTED -> APPROVED, not REQUESTED -> REFUNDED directly)
    # current_return = database.get_return_request_by_id(return_id)
    # if not current_return:
    #     logger.warning(f"Return request {return_id} not found for update.")
    #     return None # Or raise NotFoundError
    #
    # valid_transitions = {
    #     "REQUESTED": ["APPROVED", "REJECTED"],
    #     "APPROVED": ["SHIPPED_BY_CUSTOMER", "CANCELLED"],
    #     "SHIPPED_BY_CUSTOMER": ["RECEIVED", "LOST_IN_TRANSIT"],
    #     "RECEIVED": ["INSPECTING", "REFUND_PROCESSING"],
    #     "REFUND_PROCESSING": ["REFUNDED", "REFUND_FAILED"],
    #     "REJECTED": [],
    #     "CANCELLED": []
    # }
    # if status and status not in valid_transitions.get(current_return.get('status'), []):
    #    logger.error(f"Invalid status transition from {current_return.get('status')} to {status} for {return_id}")
    #    raise ValueError(f"Invalid status transition from {current_return.get('status')} to {status}")

    logger.info(f"Attempting to update return_id: {return_id} with status: {status} and other data: {other_updates}")
    try:
        updated_return = database.update_return_request_status(return_id, status, **other_updates)
        if not updated_return:
             logger.warning(f"Failed to update or find return_id: {return_id}")
             return None # Or raise NotFoundError
        # Potentially trigger notifications or other workflows based on status change
        logger.info(f"Successfully updated return_id: {return_id}. New status: {updated_return.get('status')}")
        return updated_return
    except Exception as e:
        logger.error(f"Error in update_return_info for return_id {return_id}: {str(e)}")
        raise

def get_all_returns(user_id: str = None, status: str = None, limit: int = 10, last_return_id: str = None) -> dict:
    """
    Retrieves a list of returns, optionally filtered by user_id or status.
    Handles pagination via last_return_id (which would map to ExclusiveStartKey for DynamoDB).
    """
    # In a real scenario, last_return_id might be a more complex structure (the whole LastEvaluatedKey)
    # For simplicity here, if it's just the ID, the database layer needs to know how to use it.
    # The database.list_return_requests function expects `last_evaluated_key` as a dict.
    # This service layer function might need to translate `last_return_id` if it's just the ID.
    # For now, we assume database.list_return_requests can handle a simple ID or is adapted.
    # Or, the API layer passes the full `last_evaluated_key` stringified, and this layer parses it.

    # Let's assume `last_evaluated_key` is passed as a dictionary string from the API, or None
    # For now, we'll pass `last_return_id` as is and assume `database.py` handles it or it's None.
    # This part needs careful design for robust pagination.
    # The `list_return_requests` in `database.py` expects `last_evaluated_key` (dict)
    # We will pass `None` for now for `last_evaluated_key` to simplify, actual pagination key needs to be handled.
    
    logger.info(f"Fetching all returns with filters - user_id: {user_id}, status: {status}, limit: {limit}")
    try:
        # For robust pagination, the `last_evaluated_key` (not just an ID) should be passed opaque from client to here to DB layer
        # The current `database.list_return_requests` takes `last_evaluated_key` as a dict.
        # If `last_return_id` is just the ID, it's not directly usable as `ExclusiveStartKey` unless it's the only key.
        # We will call it with `None` for `last_evaluated_key` for now.
        # Proper pagination would require passing the `last_evaluated_key` from the previous response.
        results = database.list_return_requests(user_id=user_id, status=status, limit=limit, last_evaluated_key=None)
        logger.info(f"Found {len(results.get('items',[]))} returns matching criteria.")
        return results
    except Exception as e:
        logger.error(f"Error in get_all_returns: {str(e)}")
        raise

# Example (can be removed or kept for direct service testing if desired)
if __name__ == '__main__':
    print("Testing return_service.py (requires DynamoDB Local or configured AWS environment)")
    # Configure DYNAMODB_TABLE_NAME if not set, or ensure database.py handles it
    # os.environ['DYNAMODB_TABLE_NAME'] = 'return-requests-table' # Set if not already
    
    # Note: To run this directly, you might need to adjust PYTHONPATH or run as a module
    # And ensure DynamoDB table exists (e.g., by running database.py's __main__ first)

    # Test initiate_return_process
    # try:
    #     print("
Testing initiate_return_process...")
    #     new_return = initiate_return_process("order789", "user101", "productABC", "Faulty product")
    #     print(f"Initiated return: {new_return}")
    #     return_id_for_test = new_return['return_id']

    #     # Test get_return_details
    #     print(f"
Testing get_return_details for {return_id_for_test}...")
    #     details = get_return_details(return_id_for_test)
    #     print(f"Details: {details}")

    #     # Test update_return_info
    #     print(f"
Testing update_return_info for {return_id_for_test} to APPROVED...")
    #     updated = update_return_info(return_id_for_test, status="APPROVED", notes="Return approved by support.")
    #     print(f"Updated: {updated}")

    #     # Test get_all_returns
    #     print("
Testing get_all_returns...")
    #     all_returns = get_all_returns(limit=5)
    #     print(f"All returns (limit 5): {all_returns['items']}")
        
    #     print(f"
Testing get_all_returns for user101...")
    #     user_returns = get_all_returns(user_id="user101", limit=5)
    #     print(f"User101 returns: {user_returns['items']}")

    # except ValueError as ve:
    #     print(f"ValueError: {ve}")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")
    pass # Keep __main__ empty or with commented out examples
