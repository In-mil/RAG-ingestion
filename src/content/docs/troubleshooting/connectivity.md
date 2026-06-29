# Connectivity Issues

## Symptoms

- API requests time out
- Health check returns no response
- Frontend shows "Service unavailable"

## Checklist

1. Verify the service is running (`ps aux | grep main.py`)
2. Check if the configured port is open (`curl http://localhost:8080/health`)
3. Inspect firewall rules for blocked ports
4. Review DNS resolution if using a hostname instead of an IP
5. Check the database connection string for typos
