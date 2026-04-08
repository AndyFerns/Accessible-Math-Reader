# ============================================================================
# Accessible Math Reader — Dockerfile
# ============================================================================
# Multi-stage production build.
#
# Build:   docker build -t amr .
# Run:     docker run -p 8000:8000 amr
# Compose: docker compose up -d
# ============================================================================

# ── Stage 1: Builder ──────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
COPY pyproject.toml requirements.txt ./
COPY accessible_math_reader/ accessible_math_reader/
COPY templates/ templates/
COPY static/ static/
COPY app.py ./
COPY README.md LICENSE ./

# Install the package and its API extras
RUN pip install --no-cache-dir --prefix=/install \
    ".[api]" \
    gunicorn

# ── Stage 2: Runtime ─────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Security: run as non-root user
RUN groupadd -r amr && useradd -r -g amr amr

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local
COPY --from=builder /build /app

# Ensure audio directory exists
RUN mkdir -p /app/static/audio && chown -R amr:amr /app

USER amr

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Production WSGI server
CMD ["gunicorn", \
     "accessible_math_reader.server:create_app()", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
