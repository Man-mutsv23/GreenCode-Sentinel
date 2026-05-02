# GreenCode Sentinel - Dockerfile
# Multi-stage build for optimized image size

FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY ai_engine/ ./ai_engine/
COPY app/ ./app/
COPY data/ ./data/
COPY .env.template .env.template

# Create .env file if it doesn't exist (will be overridden by volume mount)
RUN if [ ! -f .env ]; then cp .env.template .env; fi

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080')" || exit 1

# Run the application
CMD ["python", "app/main.py"]

# Made with Bob
