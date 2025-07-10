# API Documentation: User Service

This document outlines the API for the User Service.

## Endpoints

### GET /users/{id}

Retrieves a user by their unique ID.

- **Parameters:**
  - `id` (string, required): The user's ID.
- **Returns:**
  - A user object.

### POST /users

Creates a new user.

- **Body:**
  - `email` (string, required): The user's email address.
  - `name` (string, required): The user's full name.
- **Returns:**
  - The newly created user object.
