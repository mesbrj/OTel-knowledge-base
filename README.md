# OpenTelemetry Knowledge Base

# Implementation Examples:
[Python FastAPI](python_fastapi/README.md) with [orjson](https://github.com/ijl/orjson), [httptools](https://github.com/MagicStack/httptools) and [uvloop](https://github.com/MagicStack/uvloop) (C and Rust based libraries).

# Stack Components

| Component | Purpose | Ports |
|-----------|---------|-------|
| **FastAPI** | Instrumented Python web service (fastAPI and SQLAlchemy) | 8000 |
| **Grafana Alloy** | OTLP receiver with native OTLP exporter | 4317, 4318, 12345 |
| **Apache SkyWalking** | APM platform with OTLP integration | 8080, 9412, 11800, 12800, 1234 |
| **Elasticsearch** | Trace storage backend | 9200 |

## Architecture

```
FastAPI (OTLP) → Grafana Alloy (OTLP) → SkyWalking (OTLP receiver → Zipkin internal format) → Elasticsearch
```

SkyWalking 10.3.0+ [accepts native OTLP traces](https://skywalking.apache.org/docs/main/next/en/setup/backend/otlp-trace/) on port 11800 via `OpenTelemetryTraceHandler`, but internally converts them to Zipkin format for processing and storage. Traces are visible in the SkyWalking UI under: **Service Mesh → Services → Zipkin Trace**.

## Quick Start

```bash
# Start all services
podman-compose up -d

# If SkyWalking OAP exits, restart it: podman start skywalking-oap

# Generate test traffic
curl -X POST http://localhost:8000/teams \
  -H "Content-Type: application/json" \
  -d '{"name":"engineering"}'
```

## Access Points

- **FastAPI service API Documentation**: http://localhost:8000/docs
- **Grafana Alloy UI**: http://localhost:12345
- **Grafana Alloy Metrics**: http://localhost:12345/metrics (Prometheus)
- **SkyWalking UI**: http://localhost:8080
- **Zipkin Query API**: http://localhost:9412/zipkin/api/v2/services
- **SkyWalking Metrics**: http://localhost:1234/metrics (Prometheus self-observability)

## View Traces

**Via UI**: Navigate to http://localhost:8080 → Service Mesh → Services → Zipkin Trace

**Via API**:
```bash
# List services
curl http://localhost:9412/zipkin/api/v2/services

# Get traces
curl http://localhost:9412/zipkin/api/v2/traces?serviceName=fastapi-service&limit=10
```

## Configuration

### Key Files

- `alloy/config.alloy` - OTLP receivers, OTLP exporter to SkyWalking
- `skywalking/config/application.yml` - OTLP receiver configuration

### Environment Variables

```bash
# FastAPI
OTEL_EXPORTER_OTLP_ENDPOINT=http://grafana-alloy:4318
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf

# SkyWalking UI
SW_OAP_ADDRESS=http://skywalking-oap:12800
SW_ZIPKIN_ADDRESS=http://skywalking-oap:9412
```

## Local Development

```bash
# Start observability stack only
podman-compose up -d grafana-alloy skywalking-oap skywalking-ui elasticsearch

# Run FastAPI locally
cd python_fastapi
python src/main.py
```

## Trace Details

Captured spans include:
- HTTP server spans (method, route, status code)
- ASGI middleware spans (request/response lifecycle)
- Database operations (SQLite connections and queries)

## Resources

- [Grafana Alloy](https://grafana.com/docs/alloy/latest/)
- [Apache SkyWalking](https://skywalking.apache.org/docs/)
- [Zipkin API](https://zipkin.io/zipkin-api/)
- [OpenTelemetry](https://opentelemetry.io/docs/)
