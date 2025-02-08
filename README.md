# FastAPI Contacts API

## Overview
This is a FastAPI-based application that provides a RESTful API for managing contacts and user authentication.

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

   # Email verification settings (Required for email verification and password reset)
   MAIL_USERNAME=
   MAIL_PASSWORD=
   MAIL_FROM=
   MAIL_SERVER=

   # Upload settings (Cloudinary) (Required for users to update their avatar)
   CLD_NAME=
   CLD_API_KEY=
   CLD_API_SECRET=

   # Database settings (Postgres)
   DB_URL=
   POSTGRES_USER=
   POSTGRES_DB=
   POSTGRES_PASSWORD=

   # Database settings (Redis)
   REDIS_HOST=
   REDIS_PORT=
   ```

3. Start the application using Docker Compose:
   ```sh
   docker-compose up --build
   ```
   This will build and run the application, including PostgreSQL, Redis, and the FastAPI app.

## API Documentation
API documentation is available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Authentication API Endpoints

### Register a new user
- **Endpoint:** `POST /api/auth/register`
- **Description:** Registers a new user and sends a confirmation email.
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
- **Description:** Authenticates a user and returns an access token.
- **Request Body (form-data):**
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

### Forgot Password
- **Endpoint:** `POST /api/auth/forgot_password`
- **Description:** Sends a password reset email to the provided email address.
- **Request Body:**
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Password reset requested."
  }
  ```

### Reset Password
#### Serve Reset Password Form
- **Endpoint:** `GET /api/auth/reset_password/{token}`
- **Description:** Serves the password reset form for the given token.

#### Reset Password
- **Endpoint:** `POST /api/auth/reset_password/{token}`
- **Description:** Resets the user's password using the provided token and new password.
- **Request Body (form-data):**
  ```json
  {
    "password": "newsecurepassword"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Password reset successfully."
  }
  ```

---

## User API Endpoints (Requires Authentication)
- **All requests to the user API require a Bearer Token.**
- Add `Authorization: Bearer <access_token>` in the request headers.

### Get current user
- **Endpoint:** `GET /api/users/me`
- **Description:** Retrieves the authenticated user's details.

### Update user avatar
- **Endpoint:** `PATCH /api/users/avatar`
- **Description:** Updates the user's avatar by uploading a new image.
- **Request Body (form-data):**
  ```json
  {
    "file": "<binary file data>"
  }
  ```

---

## Contacts API Endpoints (Requires Authentication)

### Get all contacts
- **Endpoint:** `GET /api/contacts/`
- **Query Parameters:**
  - `skip`: Number of contacts to skip (default: 0)
  - `limit`: Maximum number of contacts to return (default: 10, max: 100)
  - `first_name`: Filter by first name
  - `last_name`: Filter by last name
  - `email`: Filter by email

### Get a single contact
- **Endpoint:** `GET /api/contacts/{contact_id}`
- **Description:** Retrieves a contact by its ID.

### Create a new contact
- **Endpoint:** `POST /api/contacts/`
- **Request Body:**
  ```json
  {
    "first_name": "John",
    "last_name": "Doe",
    "email": "johndoe@example.com",
    "phone": "+123456789",
    "date_of_birth": "1990-01-01"
  }
  ```

### Update a contact
- **Endpoint:** `PUT /api/contacts/{contact_id}`
- **Description:** Updates an existing contact.

### Delete a contact
- **Endpoint:** `DELETE /api/contacts/{contact_id}`
- **Description:** Deletes a contact by its ID.

---

## Additional Endpoints

### Get upcoming birthdays (Requires Authentication)
- **Endpoint:** `GET /api/contacts/birthdays`
- **Description:** Returns contacts with birthdays in the next 7 days.

### Seed contacts data (Requires Authentication)
- **Endpoint:** `POST /api/contacts/seed`
- **Query Parameter:**
  - `count` (integer, default=100) - Number of contacts to generate

### Healthcheck
- **Endpoint:** `GET /api/healthchecker`
- **Description:** Checks the health of the database connection.
```
