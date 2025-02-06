# FastAPI Contacts API

## Overview
This is a FastAPI-based application that provides a RESTful API for managing contacts.

## Installation

### Prerequisites
- Ensure that **Docker** and **Docker Compose** are installed on your system.

### Setup using Docker Compose

1. Clone the repository:
   ```sh
   git clone https://github.com/Gloomcat/goit-pythonweb-hw-12.git
   cd <your-project-location>
   ```

2. Create a `.env` file in the project root with the following mandatory variables:

   ```env
   # Security settings
   JWT_SECRET=
   JWT_ALGORITHM=
   JWT_EXPIRATION_MINUTES=

   # Email verification settings (Required for email verification upon registration)
   MAIL_USERNAME=
   MAIL_PASSWORD=
   MAIL_FROM=
   MAIL_SERVER=

   # Upload settings (Cloudinary) (Required for users to update their avatar)
   CLD_NAME=
   CLD_API_KEY=
   CLD_API_SECRET=

   # Database settings
   DB_URL=
   POSTGRES_USER=
   POSTGRES_DB=
   POSTGRES_PASSWORD=
   ```

3. Start the application using Docker Compose:
   ```sh
   docker-compose up --build
   ```
   This will build and run the application, PostgreSQL, and any other necessary services.

## API Documentation
API documentation is available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Authentication API Endpoints

### Register a new user
- **Endpoint:** `POST /api/auth/register`
- **Request Body:**
  ```json
  {
    "username": "exampleuser",
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "username": "exampleuser",
    "email": "user@example.com",
    "avatar": null
  }
  ```

### Login user
- **Endpoint:** `POST /api/auth/login`
- **Request Body:**
  ```json
  {
    "username": "exampleuser",
    "password": "securepassword"
  }
  ```
- **Response:**
  ```json
  {
    "access_token": "jwt_token_here",
    "token_type": "bearer"
  }
  ```

### Confirm email
- **Endpoint:** `GET /api/auth/confirmed_email/{token}`
- **Description:** Confirms a user's email using a token.

### Request email verification
- **Endpoint:** `POST /api/auth/request_email`
- **Request Body:**
  ```json
  {
    "email": "user@example.com"
  }
  ```

## User API Endpoints (Requires Authentication)
- **All requests to the user API require a Bearer Token.**
- Add `Authorization: Bearer <access_token>` in the request headers.

### Get current user
- **Endpoint:** `GET /api/users/me`
- **Description:** Retrieves the authenticated user's details.

### Update user avatar
- **Endpoint:** `PATCH /api/users/avatar`
- **Description:** Allows a user to update their avatar.
- **Request Body:**
  ```json
  {
    "file": "<binary file data>"
  }
  ```

## Contacts API Endpoints (Requires Authentication)

### Get all contacts
- **Endpoint:** `GET /api/contacts/`
- **Headers:**
  ```sh
  Authorization: Bearer <access_token>
  ```
- **Response:**
  ```json
  [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "johndoe@example.com",
      "phone": "+123456789",
      "date_of_birth": "1990-01-01"
    }
  ]
  ```

### Get a single contact
- **Endpoint:** `GET /api/contacts/{contact_id}`

### Create a new contact
- **Endpoint:** `POST /api/contacts/`

### Update a contact
- **Endpoint:** `PUT /api/contacts/{contact_id}`

### Delete a contact
- **Endpoint:** `DELETE /api/contacts/{contact_id}`

### Additional Endpoints

#### Get upcoming birthdays
- **Endpoint:** `GET /api/contacts/birthdays`
- **Description:** Returns contacts with birthdays in the next 7 days.

#### Seed contacts data
- **Endpoint:** `POST /api/contacts/seed`
- **Query Parameter:**
  - `count` (integer, default=100) - Number of contacts to generate

#### Healthcheck
- **Endpoint:** `GET /api/healthchecker`
- **Description:** Check if the API is connected to the database.
