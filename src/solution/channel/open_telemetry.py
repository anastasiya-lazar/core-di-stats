from bst_core.shared.basic_logger import get_logger
from config import LOGGER_LEVEL, OTEL_COLLECTOR_URL
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)

logger = get_logger(__name__, LOGGER_LEVEL)


def config_open_telemetry():
    logger.info("Configure open telemetry")

    resource = Resource(attributes={
        "service.name": "core-di-stats-handler-gen1-srv"
    })

    provider = TracerProvider(resource=resource)
    if OTEL_COLLECTOR_URL:
        exporter = OTLPSpanExporter(endpoint=OTEL_COLLECTOR_URL, insecure=True)
    else:
        exporter = ConsoleSpanExporter()

    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    logger.info("Open telemetry configured")
