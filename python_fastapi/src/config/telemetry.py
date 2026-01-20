"""
OpenTelemetry configuration and setup.
Provides telemetry initialization and cleanup for the application.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from config.settings import settings

def setup_telemetry() -> None:
    """
    Initialize OpenTelemetry tracing with OTLP exporter.
    Exports traces to Alloy collector via OTLP HTTP.
    """
    resource = Resource.create({
        "service.name": "fastapi-service",
        "service.version": "1.0.0",
        "deployment.environment": settings.ENVIRONMENT,
    })
    tracer_provider = TracerProvider(resource=resource)

    otlp_endpoint = settings.OTEL_EXPORTER_OTLP_ENDPOINT
    span_processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces")
    )
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)

    instrument_sqlalchemy()


def instrument_sqlalchemy() -> None:
    """
    Instrument SQLAlchemy for automatic DB operation tracing.
    """
    SQLAlchemyInstrumentor().instrument(
        enable_commenter=True,
        commenter_options={"db_driver": True}
    )

def instrument_app(app) -> None:
    """
    Instrument FastAPI application for automatic HTTP request tracing.
    """
    FastAPIInstrumentor.instrument_app(app)


def shutdown_telemetry() -> None:
    """
    Cleanup OpenTelemetry resources.
    """
    SQLAlchemyInstrumentor().uninstrument()
    trace.get_tracer_provider().shutdown()
