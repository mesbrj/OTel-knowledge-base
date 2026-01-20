# OTel-knowledge-base

# Implementation Examples:

[Python FastAPI](python_fastapi/README.md) with [orjson](https://github.com/ijl/orjson), [httptools](https://github.com/MagicStack/httptools) and [uvloop](https://github.com/MagicStack/uvloop) (C and Rust based libraries).

# Observability Stack Setup

This setup includes:
- **FastAPI Application** - Python web service with OpenTelemetry instrumentation
- **Grafana Alloy** - OpenTelemetry collector (receives OTLP from FastAPI)
- **Apache SkyWalking** - APM platform (receives traces from Alloy)
- **Elasticsearch** - Storage backend for SkyWalking

## Architecture

```
FastAPI App (Port 8000)
    |
    | OTLP HTTP (Port 4318)
    ↓
Grafana Alloy
    |
    | OTLP (Port 11800)
    ↓
SkyWalking OAP (Port 12800)
    |
    | Storage
    ↓
Elasticsearch (Port 9200)
    ↑
    | Query
    |
SkyWalking UI (Port 8080)
```

## Quick Start

### 1. Start the Observability Stack

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Access the Services

- **FastAPI Application**: http://localhost:8000
- **FastAPI Docs**: http://localhost:8000/docs
- **SkyWalking UI**: http://localhost:8080
- **Alloy UI**: http://localhost:12345
- **Elasticsearch**: http://localhost:9200

### 3. Generate Some Traffic

```bash
# Health check
curl http://localhost:8000/health

# Create a team
curl -X POST http://localhost:8000/teams \
  -H "Content-Type: application/json" \
  -d '{"name": "engineering", "description": "Engineering team"}'

# List teams
curl http://localhost:8000/teams
```

### 4. View Traces in SkyWalking

1. Open http://localhost:8080
2. Navigate to "Topology" to see service dependencies
3. Go to "Trace" to view individual requests
4. Check "Service" dashboard for metrics

## Configuration

### Alloy Configuration

Located at `alloy/config.alloy`. Key settings:
- OTLP receivers on ports 4317 (gRPC) and 4318 (HTTP)
- Batch processing with 5s timeout
- Forwards to SkyWalking OAP on port 11800

### Environment Variables

FastAPI app (set in docker-compose.yml or .env):
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://alloy:4318
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
ENVIRONMENT=production
```

### SkyWalking Configuration

SkyWalking OAP is configured to:
- Accept OTLP data on port 11800
- Store data in Elasticsearch
- Expose UI on port 12800

## Development

### Running Locally (without Docker)

1. Start only the observability stack:
```bash
docker-compose up -d alloy skywalking-oap skywalking-ui elasticsearch
```

2. Run FastAPI locally:
```bash
cd python_fastapi
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
uvicorn src.adapter.rest.server:web_app --host 0.0.0.0 --port 8000 --reload
```

### Viewing Alloy Configuration

```bash
# Check Alloy UI
open http://localhost:12345

# View Alloy logs
docker-compose logs -f alloy
```

## Troubleshooting

### No traces appearing in SkyWalking

1. Check if Alloy is receiving traces:
```bash
docker-compose logs alloy | grep -i trace
```

2. Verify SkyWalking OAP health:
```bash
curl http://localhost:12800/health
```

3. Check Elasticsearch:
```bash
curl http://localhost:9200/_cluster/health
```

### Alloy not forwarding to SkyWalking

```bash
# Restart Alloy
docker-compose restart alloy

# Check network connectivity
docker-compose exec alloy ping skywalking-oap
```

### Elasticsearch errors

```bash
# Increase memory if needed
docker-compose down
docker volume rm otel-knowledge-base_es-data
docker-compose up -d
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Production Considerations

1. **Resource Limits**: Add resource limits in docker-compose.yml
2. **Persistence**: Configure volume mounts for data persistence
3. **Security**: 
   - Enable Elasticsearch security (xpack)
   - Add authentication for SkyWalking UI
   - Use TLS for OTLP communication
4. **Scaling**: 
   - Scale SkyWalking OAP horizontally
   - Use external Elasticsearch cluster
   - Deploy Alloy as a DaemonSet in Kubernetes
5. **Retention**: Configure data retention policies in SkyWalking

## Monitoring the Monitors

- **Alloy metrics**: http://localhost:12345/metrics
- **SkyWalking self-observability**: Enabled via SW_TELEMETRY=prometheus
- **Elasticsearch metrics**: http://localhost:9200/_stats

## Additional Resources

- [Grafana Alloy Documentation](https://grafana.com/docs/alloy/latest/)
- [Apache SkyWalking Documentation](https://skywalking.apache.org/docs/)
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
