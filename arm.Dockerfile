# syntax=docker/dockerfile:1.7

# ── Build Stage ──────────────────────────────────────────
FROM --platform=$BUILDPLATFORM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Only install what is actually needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

COPY requirements.txt .

# Cache pip downloads between builds
RUN --mount=type=cache,target=/root/.cache/pip \
    /opt/venv/bin/pip install --upgrade pip wheel setuptools && \
    /opt/venv/bin/pip install --prefer-binary -r requirements.txt

# ── Runtime Stage ─────────────────────────────────────────
FROM --platform=$TARGETPLATFORM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

COPY --chown=appuser:appuser Backend/ Backend/
COPY --chown=appuser:appuser generated_pdfs/ generated_pdfs/

RUN mkdir -p /app/generated_pdfs /app/logs && \
    chown -R appuser:appuser /app

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "Backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]