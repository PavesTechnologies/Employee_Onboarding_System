# ── Build Stage ──────────────────────────────────────────
FROM python:3.12-slim-bookworm AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libmariadb-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create venv
RUN python -m venv /opt/venv

# ── CACHE BREAKER ──
# This forces Docker to re-run everything below this line
RUN date > /build_time.txt

COPY requirements.txt .
RUN /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ── Runtime Stage ─────────────────────────────────────────
FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 \
    libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libglib2.0-0 shared-mime-info \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && useradd -m appuser

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser Backend/ Backend/

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"

USER appuser
EXPOSE 8000

# Using the full path to the venv python to be absolutely safe
# Change the CMD to this:
CMD ["uvicorn", "Backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]