# Una Health Backend Tech Challenge

## Overview

The main objective of this tech challenge is to build an API to store glucose levels. The blood glucose level is a key indicator for the human metabolism, so it's important for our users to be able to store and access this data.

This project implements a FastAPI application to manage and retrieve glucose levels for users. It includes endpoints to upload glucose data from CSV files, retrieve glucose levels, and export data.

## Requirements

- Python 3.8+
- Docker and Docker Compose

## Setup

### Using Docker Compose

1. **Clone the repository:**

   ```
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Run the application locally (without Docker Compose):**

   ```
   python -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Build and run the application locally (using Docker Compose):**

    ```
    docker-compose build
    docker-compose up
    ```

3. **Access the application:**

Open your browser and navigate to `http://127.0.0.1:8000/docs` to access interactive documentation of the endpoints using Swagger UI for testing.

## API Endpoints

### POST `/api/v1/load-data`

This endpoint uploads and processes a CSV file containing glucose data. Providing means to load data to the database.

- **Request**: `multipart/form-data` with a file field named `file`.
- **Response**: JSON with a message indicating the success or failure of the operation.

### GET `/api/v1/levels`

Retrieves a list of glucose levels for a given `user_id`, with optional filtering by `start` and `stop` timestamps. Supports pagination and sorting.

- **Query Parameters**: 
    - `user_id`: The user ID to filter glucose levels.
    - `start` (optional): Start timestamp for filtering.
    - `stop` (optional): Stop timestamp for filtering.
    - `page` (default=1): Page number for pagination.
    - `page_size` (default=10): Page size, number of items per page.
    - `sort` (default=timestamp.desc): Sort criteria, default is timestamp in descending order.
- **Response**: JSON list of glucose levels.

### GET `/api/v1/levels/{id}`
Retrieves a specific glucose level by ID.

- **Path Parameters**:
    - `id`: The ID of the glucose level to retrieve.
- **Response**: JSON object of the glucose level.

## Bonus Endpoints

### POST `/api/v1/levels`
This endpoint allows creating a new glucose level entry. It handles the creation process and includes error handling for database integrity errors and unexpected exceptions.

- **Query Parameters**:
    - `user_id`: The user ID to whom the glucose level belongs.
    - `timestamp`: The timestamp of the glucose level measurement.
    - `glucose_value`: The value of the glucose level.
- **Response**: The newly created glucose level entry.

### GET `/api/v1/export-data`
Exports glucose data for a given `user_id` to a CSV file.

- **Query Parameters**:
    - `user_id`: The user ID to filter glucose levels.
- **Response**: CSV file containing the glucose levels.

## Approach and Choice of Frameworks

### FastAPI
FastAPI is chosen for its performance and ease of use. It supports asynchronous request handling, which is beneficial for I/O-bound operations like file uploads and database interactions. There is also interactive documentation using Swagger UI which can be used to test the endpoints.

### SQLAlchemy
SQLAlchemy is used as the ORM to manage database interactions. It provides a robust and flexible way to define models and interact with the database.

### Docker and Docker Compose
Docker is used to containerize the application, ensuring consistency across different environments. Docker Compose simplifies the process of building and running the application locally.

## Project Structure
```
Project_Folder/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── main.py
├── models.py
├── schemas.py
└── (other files e.g test_main.py for testing)
```

## Running Tests
To run the unit tests navigate to project folder, and run `pytest`:
    ```
    pytest
    ```

## Conclusion
This project provides API endpoints for managing glucose data and options for local deployment using Docker Compose. The project is built with FastAPI and SQLAlchemy, providing a robust and scalable solution.

## Sources used for Help
Used google for searching for syntax, debugging. Took help from GPT to write the README, docstrings, and debugging.