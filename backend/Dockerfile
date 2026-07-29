# =============================================================================
# Stage 1: Build — install Python dependencies into an isolated venv
# =============================================================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build tools needed for psycopg binary wheel
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime — lean image, copy venv + source only
# =============================================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Runtime dependency for psycopg
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source (excludes venv, .env via .dockerignore)
COPY . .

EXPOSE 5000

# Run database migrations then start gunicorn
CMD ["sh", "-c", "flask --app run db upgrade && gunicorn run:app --bind 0.0.0.0:5000 --workers 4 --timeout 120"]
