# ── HydroAI Backend – Multi-stage Dockerfile ─────────────────────────────────
# Stage 1: dependency builder
FROM python:3.11-slim AS builder

WORKDIR /build

# System libs required by numpy / matplotlib / asyncpg / ANUGA
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libgdal-dev \
        libnetcdf-dev \
        libhdf5-dev \
        gfortran \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Only the runtime system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        libgdal32 \
        libnetcdf19 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Create directories that are written at runtime
RUN mkdir -p maps models

# Non-root user for security
RUN useradd -m hydroai && chown -R hydroai:hydroai /app
USER hydroai

EXPOSE 8000

# Uvicorn with multiple workers (adjust --workers for your CPU count)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "4", "--loop", "uvloop", "--http", "httptools"]
