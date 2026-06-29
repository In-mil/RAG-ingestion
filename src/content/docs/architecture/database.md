# Database Schema

## Tables

### users

| Column     | Type      | Description           |
|------------|-----------|-----------------------|
| id         | UUID      | Primary key           |
| email      | VARCHAR   | Unique email address  |
| role       | VARCHAR   | admin, editor, viewer |
| created_at | TIMESTAMP | Account creation date |

### files

| Column     | Type      | Description           |
|------------|-----------|-----------------------|
| id         | UUID      | Primary key           |
| name       | VARCHAR   | Original filename     |
| size_bytes | INTEGER   | File size             |
| owner_id   | UUID      | Foreign key to users  |
| created_at | TIMESTAMP | Upload date           |

## Migrations

All schema changes are managed through numbered migration files in the `migrations/` directory. Run them in order with `python migrate.py`.
