# Webhooks

## Configuration

Register a webhook URL under Settings > Integrations. The system sends a POST request to your URL whenever a relevant event occurs.

## Payload Format

```json
{
  "event": "file.created",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "id": "abc-123",
    "name": "report.md"
  }
}
```

## Retry Policy

Failed deliveries are retried up to 3 times with exponential backoff (1 min, 5 min, 15 min).
