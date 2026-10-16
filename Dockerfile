FROM python:3.13-slim AS backend-builder

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM node:24-slim AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY --from=backend-builder /app/backend .
COPY --from=backend-builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist ./static

# Create config directories
RUN mkdir -p /config/secrets && chmod 700 /config/secrets

# Create non-root user (PUID/PGID will be overridden at runtime if set)
RUN groupadd -g 1000 woosarr && useradd -u 1000 -g woosarr -m woosarr

# Set ownership
RUN chown -R woosarr:woosarr /app /config

# Set permissions
RUN chmod 600 /config/secrets/master.key 2>/dev/null || true

EXPOSE 2000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:2000/api/health || exit 1

# Use entrypoint script for PUID/PGID support
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "2000", "--workers", "1"]
