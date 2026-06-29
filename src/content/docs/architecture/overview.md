# Architecture Overview

The system follows a layered architecture:

1. **API Layer** receives HTTP requests and validates input
2. **Service Layer** contains business logic and orchestrates operations
3. **Data Layer** manages database access and external integrations

## Communication

Services communicate synchronously via REST. For background tasks, a message queue processes jobs asynchronously.

## Storage

Files are stored in object storage. Metadata and user data live in a relational database.
