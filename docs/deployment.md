---
title: Deployment Guide
---

# Deployment Guide

This guide covers deploying Accessible Math Reader in production environments.

## Quick Start (Docker)

The fastest way to deploy AMR:

```bash
# 1. Copy and configure environment
cp .env.example .env

# 2. Start the service
docker compose up -d

# 3. Verify
curl http://localhost:8000/health
```

## Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t amr .

# Run with defaults
docker run -p 8000:8000 amr

# Run with custom configuration
docker run -p 8000:8000 \
  -e AMR_LOG_FORMAT=json \
  -e AMR_METRICS=true \
  -e AMR_ENABLE_AUTH=true \
  -e AMR_API_KEYS=my-secret-key \
  amr
```

### Docker Compose

The included `docker-compose.yml` provides production defaults:

```yaml
services:
  amr:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
```

## Bare-Metal Deployment

### With Gunicorn (Linux/macOS)

```bash
pip install accessible-math-reader[api]
gunicorn "accessible_math_reader.server:create_app()" \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120
```

### With Waitress (Windows)

```bash
pip install accessible-math-reader[web] waitress
waitress-serve --port=8000 --call accessible_math_reader.server:create_app
```

### Development Mode

```bash
python -m accessible_math_reader.server
# or the original:
python app.py
```

## Kubernetes Deployment

AMR includes built-in support for Kubernetes probes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amr
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: amr
          image: amr:latest
          ports:
            - containerPort: 8000
          env:
            - name: AMR_LOG_FORMAT
              value: "json"
            - name: AMR_METRICS
              value: "true"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /readiness
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
```

### Prometheus Scraping

```yaml
apiVersion: v1
kind: Service
metadata:
  name: amr
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
    prometheus.io/path: "/metrics"
```

## REST API

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/speech` | Math → spoken English |
| `POST` | `/api/v1/braille` | Math → Braille notation |
| `POST` | `/api/v1/structure` | Math → semantic AST (JSON) |
| `POST` | `/api/v1/audio` | Math → MP3 audio file |
| `POST` | `/api/v1/validate` | WCAG accessibility check |
| `GET` | `/health` | Liveness probe |
| `GET` | `/readiness` | Readiness probe |
| `GET` | `/metrics` | Prometheus metrics |

### Request Format

```json
{
  "input": "x^2 + y^2 = z^2",
  "format": "auto",
  "notation": "nemeth",
  "verbosity": "verbose"
}
```

### Example

```bash
curl -X POST http://localhost:8000/api/v1/speech \
  -H 'Content-Type: application/json' \
  -d '{"input": "\\\\frac{a}{b}"}'
```

Response:
```json
{
  "speech": "start fraction a over b end fraction",
  "input": "\\frac{a}{b}"
}
```

## Configuration

All settings are via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `AMR_PORT` | `8000` | Server port |
| `AMR_LOG_FORMAT` | `text` | Logging format (`json`/`text`) |
| `AMR_LOG_LEVEL` | `INFO` | Log verbosity |
| `AMR_SPEECH_ENGINE` | `gtts` | TTS backend (`gtts`/`espeak`/`pyttsx3`/`coqui`) |
| `AMR_METRICS` | `false` | Enable Prometheus metrics |
| `AMR_TRACING` | `false` | Enable OpenTelemetry tracing |
| `AMR_ENABLE_AUTH` | `false` | Require API key authentication |
| `AMR_API_KEYS` | | Comma-separated valid API keys |
| `AMR_ENABLE_RATE_LIMIT` | `false` | Enable per-IP rate limiting |
| `AMR_RATE_LIMIT` | `100/minute` | Rate limit threshold |
| `AMR_MAX_REQUEST_SIZE` | `1048576` | Max request body (bytes) |

## Offline / Air-Gapped Deployment

For institutional environments without internet:

1. **Use offline TTS**: Set `AMR_SPEECH_ENGINE=espeak` or `pyttsx3`
2. **Pre-install dependencies**: `pip download accessible-math-reader[api] -d ./packages`
3. **No telemetry**: AMR has zero analytics or phone-home behavior
4. **Deterministic builds**: Pin versions with `pip freeze > requirements.lock`

## gRPC Service

For microservice architectures:

```bash
pip install accessible-math-reader[grpc]
python -m accessible_math_reader.grpc_service.server --port 50051
```

Protobuf schema: `accessible_math_reader/grpc_service/proto/math_service.proto`
