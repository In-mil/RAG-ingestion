# API Overview

The REST API follows standard conventions. All endpoints return JSON and expect JSON request bodies where applicable.

## Base URL

The base URL depends on your deployment environment. Check your `.env` file for the configured value.

## Rate Limiting

All endpoints are rate-limited to 100 requests per minute per API key. Exceeding this limit returns a `429 Too Many Requests` response.
