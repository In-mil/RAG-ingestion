# Configuration

## Environment Variables

| Variable       | Required | Description                    |
|----------------|----------|--------------------------------|
| DATABASE_URL   | Yes      | Connection string for the DB   |
| API_KEY        | Yes      | Secret key for authentication  |
| LOG_LEVEL      | No       | debug, info, warn, error       |
| PORT           | No       | Server port, defaults to 8080  |

## Config File

Alternatively, create a `config.yaml` in the project root:

```yaml
database:
  url: postgres://localhost:5432/mydb
server:
  port: 8080
  log_level: info
```

Environment variables take precedence over the config file.
