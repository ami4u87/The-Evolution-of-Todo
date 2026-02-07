"""Kafka topic constants for event-driven architecture."""


class Topics:
    """Kafka topic names for task events."""

    TASK_EVENTS = "task-events"

    # Dapr pub/sub component name (must match Dapr component metadata)
    PUBSUB_NAME = "kafka-pubsub"
