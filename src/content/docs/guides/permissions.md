# Permissions

## Roles

| Role    | Description                              |
|---------|------------------------------------------|
| admin   | Full access to all resources             |
| editor  | Can create and modify content            |
| viewer  | Read-only access                         |

## Assigning Roles

Roles are assigned per user by an admin via the `/users/:id/role` endpoint.

## Custom Permissions

For fine-grained control, attach permission objects to roles. Each permission specifies a resource and an action (read, write, delete).
