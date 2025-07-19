# Multi-stage Dockerfile for Crypto Trading AI Platform
FROM node:18-alpine AS frontend-builder

# Build React Frontend
WORKDIR /app/frontend
COPY package*.json ./
RUN npm ci --only=production
COPY src/ ./src/
COPY public/ ./public/
COPY tailwind.config.js postcss.config.js vite.config.js ./
RUN npm run build

# Python Backend
FROM python:3.11-slim AS backend

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY . .

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./static/react-build/

# Create necessary directories
RUN mkdir -p logs tmp

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:application"]