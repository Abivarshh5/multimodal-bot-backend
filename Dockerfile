# ==========================================
# Stage 1: Base Image & Environment Setup
# ==========================================
# Use Python 3.11 slim image for a secure, lightweight runtime foundation
FROM python:3.11-slim

# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout/stderr (ensures instant log streaming in Railway)
ENV PYTHONUNBUFFERED=1

# Railway dynamically assigns a PORT environment variable. Defaulting to 8000 as fallback.
ENV PORT=8000
EXPOSE 8000

# Set the working directory
WORKDIR /app

# ==========================================
# Stage 2: System Dependencies
# ==========================================
# Install essential system build dependencies for torch, psycopg2, sentence-transformers, and health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# Stage 3: Python Dependencies & Layer Caching
# ==========================================
# Copy requirements.txt first to efficiently leverage Docker layer caching
COPY requirements.txt .

# Upgrade pip and install PyTorch CPU version first to prevent 2.5GB+ CUDA download causing Bus error / OOM
RUN --mount=type=cache,id=s/fc2149b5-f8bb-4d93-aa11-c18144e5c77f-/root/.cache/pip,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install -r requirements.txt

# Configure Playwright to install browser binaries in a custom system path accessible by non-root users
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN playwright install --with-deps chromium && \
    chmod -R 755 /ms-playwright

# ==========================================
# Stage 4: Source Code & Security
# ==========================================
# Create a non-root user (appuser) for production security best practices
RUN useradd -m -u 1000 appuser

# Copy project source code and assign ownership to the non-root user
COPY --chown=appuser:appuser . .

# Switch to non-root user execution
USER appuser

# ==========================================
# Stage 5: Health Check & Startup Command
# ==========================================
# Health check to ensure FastAPI is responsive before accepting traffic
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start FastAPI using uvicorn, binding to 0.0.0.0 and dynamically reading Railway's PORT variable
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
