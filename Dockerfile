# ==========================================
# Stage 1: Base Image
# ==========================================
# Official Playwright image with Chromium pre-installed
FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy

# ==========================================
# Environment Configuration
# ==========================================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# ==========================================
# System Dependencies
# ==========================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# Python Dependencies
# ==========================================
COPY requirements.txt .

RUN pip install --upgrade pip

# Install CPU version of torch first
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# Install Crawl4AI/Playwright Browsers (as root)
# ==========================================
# Since PLAYWRIGHT_BROWSERS_PATH is set to /ms-playwright,
# crawl4ai-setup will install Patchright's chromium-1223 here.
RUN crawl4ai-setup

# Ensure the non-root user 'pwuser' owns the browser directories
RUN chown -R pwuser:pwuser /ms-playwright

# ==========================================
# Copy Source Code
# ==========================================
COPY --chown=pwuser:pwuser . .

USER pwuser

# ==========================================
# Health Check
# ==========================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# ==========================================
# Railway Startup Command
# ==========================================
EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]