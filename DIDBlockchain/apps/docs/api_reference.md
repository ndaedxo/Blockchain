# API Reference for DIDBlockchain

## Base URL

http://127.0.0.1:8000/
## Endpoints

### 1. Create User

- **Endpoint**: `/users/`
- **Method**: `POST`
- **Description**: Create a new user.
- **Request Body**:
    ```json
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    ```
- **Response**:
    - **201 Created**: User created successfully.
    - **400 Bad Request**: Validation error.

### 2. Retrieve User

- **Endpoint**: `/users/{id}/`
- **Method**: `GET`
- **Description**: Retrieve user details by ID.
- **Response**:
    - **200 OK**: User details.
    - **404 Not Found**: User not found.

### 3. Create DID Document

- **Endpoint**: `api/did-documents/`
- **Method**: `POST`
- **Description**: Create a new DID document.
- **Request Body**:
    ```json
    {
        "did": "string",
        "public_key": "string",
        "service_endpoint": "string"
    }
    ```
- **Response**:
    - **201 Created**: DID document created successfully.
    - **400 Bad Request**: Validation error.

### 4. Retrieve DID Document

- **Endpoint**: `api/did-documents/{id}/`
- **Method**: `GET`
- **Description**: Retrieve DID document by ID.
- **Response**:
    - **200 OK**: DID document details.
    - **404 Not Found**: DID document not found.

## Authentication

Authentication for all endpoints can be done using JWT tokens. Include the token in the `Authorization` header:

