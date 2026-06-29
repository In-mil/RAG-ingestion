# Deployment

## Production Checklist

- All environment variables set
- Database migrations applied
- Health check endpoint returning 200
- Monitoring and alerting configured

## Rollback

If a deployment fails, revert to the previous container image tag and re-run the pipeline.
