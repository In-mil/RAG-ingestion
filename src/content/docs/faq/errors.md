# Common Errors

## 401 Unauthorized

Your token is missing or expired. Re-authenticate via `/auth/login` and include the new token in your request headers.

## 413 Payload Too Large

The uploaded file exceeds the size limit. Reduce the file size or split it into smaller parts.

## 500 Internal Server Error

An unexpected error occurred on the server. Check the application logs for details and report the issue to the operations team.

## Connection Refused

The service is not running or the configured URL is incorrect. Verify the host and port in your environment variables.
