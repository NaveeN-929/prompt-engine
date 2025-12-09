# Multi-stage build for Validation LLM Service
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    build-essential \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime image
FROM python:3.11-slim as runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/opt/venv/bin:$PATH"

# Validation service specific environment variables
ENV VALIDATION_HOST=0.0.0.0
ENV VALIDATION_PORT=5002
ENV OLLAMA_HOST=http://ollama:11434
ENV QDRANT_HOST=qdrant
ENV QDRANT_PORT=6333

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY core/ ./core/
COPY config.py .
COPY simple_server.py .
COPY validation_server.py .
COPY setup_models.py .
COPY test-docker-env.py .
COPY docker-entrypoint.sh .
COPY requirements.txt .

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# Create directories for data persistence
RUN mkdir -p /app/logs /app/training_data/exports /app/training_data/exemplary \
    /app/training_data/high_quality /app/training_data/acceptable

# Create non-root user and set permissions
RUN useradd --create-home --shell /bin/bash --uid 1001 validator && \
    chown -R validator:validator /app

# Switch to non-root user
USER validator

# Expose port
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# Set entrypoint and command
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "simple_server.py"]
