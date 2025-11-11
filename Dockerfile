# Multi-stage build for DONUT Receipt Parser
# Optimized for production deployment

# ============================================================================
# Stage 1: Base image with dependencies
# ============================================================================
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Stage 2: Build stage with Python dependencies
# ============================================================================
FROM base as builder

WORKDIR /build

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 3: Production image
# ============================================================================
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    DONUT_DEVICE=cpu \
    GRADIO_SERVER_NAME=0.0.0.0

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application files
COPY config.py .
COPY donut_minimal.py .
COPY batch_processor.py .
COPY diagnose.py .
COPY README.md .

# Create required directories
RUN mkdir -p data/input data/output data/samples models logs

# Expose ports
EXPOSE 7860 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Default command (can be overridden)
CMD ["python", "donut_minimal.py"]

# ============================================================================
# Usage Examples:
# ============================================================================
# Build:
#   docker build -t donut-receipt-parser .
#
# Run Gradio UI:
#   docker run -p 7860:7860 donut-receipt-parser
#
# Run with GPU support:
#   docker run --gpus all -e DONUT_DEVICE=cuda -p 7860:7860 donut-receipt-parser
#
# Run with mounted volumes:
#   docker run -p 7860:7860 \
#     -v $(pwd)/data:/app/data \
#     -v $(pwd)/models:/app/models \
#     donut-receipt-parser
#
# Run batch processor:
#   docker run -v $(pwd)/data:/app/data \
#     donut-receipt-parser python batch_processor.py /app/data/input -o /app/data/output
# ============================================================================
