# Return Management Microservice

This project is an AWS Lambda-based microservice for managing e-marketplace order returns. It uses Python, API Gateway, and DynamoDB.

## Features

- Create new return requests.
- Retrieve details of a specific return request.
- Update the status and other information of a return request.
- List all return requests with optional filtering by user ID or status.

## Project Structure

```
return-management-service/
├── src/                    # Source code
│   ├── database.py         # DynamoDB interaction logic
│   ├── return_service.py   # Business logic layer
│   └── lambda_handler.py   # AWS Lambda handler and API routing
├── tests/                  # Unit tests
│   ├── conftest.py         # Pytest fixtures (e.g., mock DynamoDB setup)
│   ├── test_database.py    # Tests for database.py
│   └── test_return_service.py # Tests for return_service.py
├── .env-example            # Example environment variables
├── requirements.txt        # Python dependencies for application and testing
├── template.yaml           # AWS SAM template for deployment
└── README.md               # This file
```

## Prerequisites

- AWS Account
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate credentials and region.
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) for building and deploying the application.
- [Python](https://www.python.org/downloads/) (version 3.9, as specified in `template.yaml`).
- [Docker](https://www.docker.com/get-started) (for SAM local testing and building).
- (Optional) [DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html) for local development and testing.

## Setup and Local Development

1.  **Clone the repository (if applicable) or ensure you have the code.**

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate 
    # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Copy `.env-example` to a `.env` file and customize if needed. For AWS deployment, these will be set in the `template.yaml` or Lambda configuration.
    ```bash
    cp .env-example .env 
    # Edit .env if you need to change DYNAMODB_TABLE_NAME for local use, for example
    # export DYNAMODB_TABLE_NAME=my-local-returns-table 
    ```
    The `database.py` file is configured to connect to DynamoDB Local if `AWS_SAM_LOCAL=true` or `IS_OFFLINE=true` environment variables are set (common for SAM Local and Serverless Framework offline, respectively).
    The endpoint URL in `database.py` for local DynamoDB is `http://docker.for.mac.localhost:8000` or `http://localhost:8000`. Adjust if your DynamoDB Local runs elsewhere.

5.  **Running DynamoDB Local (Optional):**
    If you want to test against DynamoDB Local:
    ```bash
    # Using Docker (recommended)
    docker run -p 8000:8000 amazon/dynamodb-local -jar DynamoDBLocal.jar -sharedDb -dbPath ./data/
    
    # Or download and run the .jar file directly (see AWS documentation)
    ```
    You might need to create the table manually in DynamoDB Local using the AWS CLI, pointing to the local endpoint, or by running the `database.py` script's `__main__` block if adapted for this.
    Example AWS CLI command to create table locally (adjust attributes and GSIs as per `template.yaml` or `database.py`'s `create_dynamodb_table_schema`):
    ```bash
    aws dynamodb create-table         --table-name return-requests-table         --attribute-definitions AttributeName=return_id,AttributeType=S AttributeName=user_id,AttributeType=S AttributeName=status,AttributeType=S AttributeName=created_at,AttributeType=N         --key-schema AttributeName=return_id,KeyType=HASH         --global-secondary-indexes             "[
                {
                    "IndexName": "UserIndex",
                    "KeySchema": [{"AttributeName":"user_id","KeyType":"HASH"}],
                    "Projection": {"ProjectionType":"ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits":5,"WriteCapacityUnits":5}
                },
                {
                    "IndexName": "StatusIndex",
                    "KeySchema": [{"AttributeName":"status","KeyType":"HASH"}, {"AttributeName":"created_at","KeyType":"RANGE"}],
                    "Projection": {"ProjectionType":"ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits":5,"WriteCapacityUnits":5}
                }
            ]"         --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5         --endpoint-url http://localhost:8000
    ```

## Running Unit Tests

Ensure `pytest` is installed (it's in `requirements.txt`).
From the `return-management-service` root directory:
```bash
python -m pytest -v tests/
```
The tests use `moto` to mock DynamoDB, so they don't require a live DynamoDB instance or AWS credentials. The `DYNAMODB_TABLE_NAME` environment variable is set to `test-return-requests-table` during tests by `conftest.py`.

## AWS SAM Deployment

The `template.yaml` file describes the AWS resources needed for this microservice (Lambda function, API Gateway, DynamoDB table, IAM roles).

1.  **Build the SAM application:**
    This command compiles your application and prepares it for deployment.
    ```bash
    sam build --use-container # --use-container is recommended for consistency
    ```

2.  **Deploy the SAM application:**
    This command deploys your application to AWS. You'll be guided through some prompts.
    ```bash
    sam deploy --guided
    ```
    - **Stack Name:** A unique name for this CloudFormation stack (e.g., `return-management-prod`).
    - **AWS Region:** The AWS region to deploy to (e.g., `us-east-1`).
    - **Parameter DynamoDBTableName:** You can override the default table name (`return-requests-table`) here if needed.
    - **Confirm changes before deploy:** Review the changes SAM will make.
    - **Allow SAM CLI IAM role creation:** Yes.
    - **Save arguments to samconfig.toml:** Yes, this is useful for subsequent deployments (`sam deploy` without `--guided`).

    After deployment, SAM CLI will output the API Gateway endpoint URL.

## API Endpoints

The following API endpoints are defined (base URL will be provided by API Gateway after deployment):

-   **`POST /returns`**: Create a new return request.
    -   **Request Body (JSON):**
        ```json
        {
            "order_id": "string",
            "user_id": "string",
            "product_id": "string",
            "reason": "string"
        }
        ```
    -   **Response (201 - Created):**
        ```json
        {
            "return_id": "string (uuid)",
            "order_id": "string",
            "user_id": "string",
            "product_id": "string",
            "reason": "string",
            "status": "REQUESTED",
            "created_at": "timestamp (int)",
            "updated_at": "timestamp (int)"
        }
        ```

-   **`GET /returns/{return_id}`**: Get details of a specific return.
    -   **Path Parameter:** `return_id` (string, UUID)
    -   **Response (200 - OK):** The return request object (as above) or (404 - Not Found).

-   **`PUT /returns/{return_id}`**: Update a return request (e.g., status).
    -   **Path Parameter:** `return_id` (string, UUID)
    -   **Request Body (JSON):**
        ```json
        {
            "status": "string (e.g., APPROVED, REJECTED, SHIPPED)",
            "notes": "string (optional)" 
            // ... any other updatable attributes
        }
        ```
    -   **Response (200 - OK):** The updated return request object or (404 - Not Found).

-   **`GET /returns`**: List return requests.
    -   **Query Parameters (optional):**
        -   `user_id` (string): Filter by user ID.
        -   `status` (string): Filter by status.
        -   `limit` (int): Number of items to return (default: 10).
        -   `last_evaluated_key` (stringified JSON object): For pagination. The value should be the `last_evaluated_key` returned from a previous request.
    -   **Response (200 - OK):**
        ```json
        {
            "items": [ /* array of return request objects */ ],
            "last_evaluated_key": { /* object, or null if no more items */ }
        }
        ```

## DynamoDB Table

-   **Table Name:** Configured via `DYNAMODB_TABLE_NAME` environment variable (default: `return-requests-table`).
-   **Primary Key:** `return_id` (String)
-   **Global Secondary Indexes (GSIs):**
    -   `UserIndex`:
        -   Partition Key: `user_id` (String)
        -   Purpose: Efficiently query returns by user.
    -   `StatusIndex`:
        -   Partition Key: `status` (String)
        -   Sort Key: `created_at` (Number)
        -   Purpose: Efficiently query returns by status, optionally sorted by creation date.

## Further Considerations / TODO

-   More robust input validation (e.g., using Pydantic).
-   More sophisticated error handling and logging.
-   Implement authentication and authorization (e.g., using AWS Cognito with API Gateway).
-   Refine pagination for `GET /returns` to make `last_evaluated_key` handling more seamless.
-   Add more comprehensive unit and integration tests.
-   Implement CI/CD pipeline for automated testing and deployment.
-   Consider using a Python web framework like Chalice or FastAPI with an adapter (e.g., Mangum) if the API complexity grows.
```
