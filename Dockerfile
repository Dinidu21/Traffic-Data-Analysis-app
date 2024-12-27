# Stage 1: Build Stage
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /opt

# Copy application code
COPY app.py .

# Install Python dependencies
RUN pip install --no-cache-dir flask

# Stage 2: Runtime Stage
FROM python:3.12-slim

# Set the working directory
WORKDIR /opt

# Install the necessary dependencies in the runtime stage
RUN pip install --no-cache-dir flask

# Copy only the necessary files from the build stage
COPY --from=builder /opt /opt

# Expose Flask's default port
EXPOSE 5000

# Run the Flask application
ENTRYPOINT ["python3", "app.py"]

