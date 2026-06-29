# Dockerfile
# Packages sync.py into a minimal container image.
# The image is meant to run as a short-lived job in CI (GitHub Actions),
# not as a long-running service.

FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/sportidentgmbh/docs.git"
LABEL org.opencontainers.image.description="Syncs markdown docs into an Open WebUI Knowledge Base"

WORKDIR /app

# Install dependencies first (cached layer as long as requirements don't change).
COPY custom_requirements.txt .
RUN pip install --no-cache-dir -r custom_requirements.txt

# Copy the sync script.
COPY sync.py .

# The script reads all config from environment variables:
#   OPEN_WEBUI_API_URL  – base URL of the Open WebUI instance
#   OPEN_WEBUI_API_KEY  – API key for authentication
#   KNOWLEDGE_ID        – target Knowledge Base ID
#   DOCS_DIR            – path to the mounted docs folder (set at runtime)

ENTRYPOINT ["python", "sync.py"]
