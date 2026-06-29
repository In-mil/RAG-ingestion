# Reading Logs

## Log Location

Logs are written to stdout by default. In production, they are collected by the log aggregator.

## Log Levels

- `debug` — verbose output for development
- `info` — standard operational messages
- `warn` — non-critical issues that should be reviewed
- `error` — failures that need immediate attention

## Filtering

Use `LOG_LEVEL` to control which messages appear. Setting it to `warn` suppresses `debug` and `info` output.
