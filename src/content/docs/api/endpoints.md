# Endpoints

## Users

| Method | Path           | Description          |
|--------|----------------|----------------------|
| GET    | /users         | List all users       |
| POST   | /users         | Create a new user    |
| GET    | /users/:id     | Get user by ID       |
| DELETE | /users/:id     | Delete a user        |

## Files

| Method | Path           | Description          |
|--------|----------------|----------------------|
| GET    | /files         | List uploaded files  |
| POST   | /files         | Upload a file        |
| DELETE | /files/:id     | Remove a file        |

## Error Codes

- `400` Invalid request body
- `401` Missing or invalid token
- `404` Resource not found
- `500` Internal server error
