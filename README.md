# OpenTelemetry Knowledge Base

# Implementation Examples:
[Python FastAPI](python_fastapi/README.md) with [orjson](https://github.com/ijl/orjson), [httptools](https://github.com/MagicStack/httptools) and [uvloop](https://github.com/MagicStack/uvloop) (C and Rust based libraries).

# Stack Components

| Component | Purpose | Ports |
|-----------|---------|-------|
| **FastAPI** | Instrumented Python web service | 8000 |
| **OpenTelemetry Collector** | OTLP receiver with Zipkin exporter | 4317, 4318 |
| **Apache SkyWalking** | APM platform with Zipkin integration | 8080, 9412, 12800, 1234 |
| **Elasticsearch** | Trace storage backend | 9200 |

## Architecture

```
FastAPI (OTLP) → OTel Collector (Protocol Conversion) → SkyWalking (Zipkin) → Elasticsearch
```

Using Zipkin protocol. SkyWalking's OTLP (traces) receiver doesn't worked as [expected](https://skywalking.apache.org/docs/main/next/en/setup/backend/otlp-trace/).
More info about this issue can be found [here](https://github.com/apache/skywalking/discussions/11873).

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

- **FastAPI Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
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

- `otel-collector/config.yaml` - OTLP receivers, Zipkin exporter
- `skywalking/config/application.yml` - Zipkin receiver/query modules
- `docker-compose.yml` - Service orchestration

### Environment Variables

```bash
# FastAPI
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf

# SkyWalking UI
SW_OAP_ADDRESS=http://skywalking-oap:12800
SW_ZIPKIN_ADDRESS=http://skywalking-oap:9412
```

## Local Development

```bash
# Start observability stack only
podman-compose up -d otel-collector skywalking-oap skywalking-ui elasticsearch

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

- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)
- [Apache SkyWalking](https://skywalking.apache.org/docs/)
- [Zipkin API](https://zipkin.io/zipkin-api/)
