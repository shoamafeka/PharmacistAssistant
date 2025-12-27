# Dockerfile for Pharmacist Assistant
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (curl for health check)
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Set PYTHONPATH so Python can find the app module
ENV PYTHONPATH=/app

# Expose Streamlit port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/_stcore/health || exit 1

# Run Streamlit app
CMD ["streamlit", "run", "app/main.py", "--server.port=3000", "--server.address=0.0.0.0"]

