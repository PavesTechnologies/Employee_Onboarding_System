# ── Build Stage ──────────────────────────────────────────
FROM python:3.11-slim-bookworm AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

# Cache breaker
RUN date > /build_time.txt

COPY requirements.txt .
RUN /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install -v --no-cache-dir -r requirements.txt


# ── Runtime Stage ─────────────────────────────────────────
FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 \
    libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libglib2.0-0 shared-mime-info \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m appuser

WORKDIR /app

# Copy venv + code
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser Backend/ Backend/
COPY --chown=appuser:appuser generated_pdfs/ generated_pdfs/

# ✅ Create required directories with correct permissions
RUN mkdir -p /app/generated_pdfs /app/logs && \
    chown -R appuser:appuser /app

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"

USER appuser

EXPOSE 8000

CMD ["uvicorn", "Backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]