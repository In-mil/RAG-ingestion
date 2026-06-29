# General FAQ

## How do I reset my password?

Send a POST request to `/auth/reset-password` with your registered email address. You will receive a reset link.

## Can I use the API without a frontend?

Yes. The API is fully standalone. Use any HTTP client like `curl` or a REST client.

## What file formats are supported?

Currently only markdown (`.md`) files are supported for document ingestion.

## Is there a file size limit?

Individual files are limited to 10 MB. Contact the admin team if you need to upload larger files.
