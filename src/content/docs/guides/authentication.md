# Authentication

## Overview

The system uses token-based authentication. Each user receives an API key after registration.

## How It Works

1. Send a POST request to `/auth/login` with your credentials
2. The server returns a bearer token
3. Include the token in the `Authorization` header for all subsequent requests

## Token Expiry

Tokens expire after 24 hours. Use the `/auth/refresh` endpoint to obtain a new token without re-entering credentials.
