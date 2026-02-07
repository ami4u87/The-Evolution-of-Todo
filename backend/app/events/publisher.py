"""Event publisher using Dapr pub/sub sidecar API.

When running outside Kubernetes (local dev), events are logged but not published.
When Dapr sidecar is available, events are published to Kafka via Dapr HTTP API.
"""

import logging
from typing import ClassVar

import httpx

from app.events.models import TaskEvent
from app.events.topics import Topics

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes task events via Dapr sidecar or logs them locally."""

    _instance: ClassVar["EventPublisher | None"] = None
    _dapr_url: str
    _enabled: bool

    def __init__(self, dapr_http_port: int = 3500, enabled: bool = True):
        self._dapr_url = f"http://localhost:{dapr_http_port}"
        self._enabled = enabled

    @classmethod
    def get_instance(cls) -> "EventPublisher":
        """Get or create singleton publisher instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def configure(cls, dapr_http_port: int = 3500, enabled: bool = True) -> None:
        """Configure the publisher (call during app startup)."""
        cls._instance = cls(dapr_http_port=dapr_http_port, enabled=enabled)

    async def publish(self, event: TaskEvent) -> bool:
        """Publish an event to Kafka via Dapr pub/sub.

        Returns True if published successfully, False otherwise.
        Always logs the event regardless of publish success.
        """
        event_dict = event.model_dump()

        logger.info(
            "Event: %s | task=%s user=%s",
            event.type.value,
            event.data.task_id,
            event.data.user_id,
        )

        if not self._enabled:
            logger.debug("Event publishing disabled, event logged only")
            return True

        try:
            url = (
                f"{self._dapr_url}/v1.0/publish/"
                f"{Topics.PUBSUB_NAME}/{Topics.TASK_EVENTS}"
            )
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.post(
                    url,
                    json=event_dict,
                    headers={"Content-Type": "application/cloudevents+json"},
                )
                if response.status_code in (200, 204):
                    logger.info("Event published: %s", event.id)
                    return True
                else:
                    logger.warning(
                        "Dapr publish returned %d: %s",
                        response.status_code,
                        response.text,
                    )
                    return False
        except httpx.ConnectError:
            logger.debug(
                "Dapr sidecar not available, event logged only (local dev mode)"
            )
            return True
        except Exception:
            logger.exception("Failed to publish event %s", event.id)
            return False

    def publish_sync(self, event: TaskEvent) -> bool:
        """Synchronous wrapper for publishing events.

        Used by the task service which operates synchronously.
        Events are best-effort: failure does not block the request.
        """
        event_dict = event.model_dump()

        logger.info(
            "Event: %s | task=%s user=%s",
            event.type.value,
            event.data.task_id,
            event.data.user_id,
        )

        if not self._enabled:
            logger.debug("Event publishing disabled, event logged only")
            return True

        try:
            url = (
                f"{self._dapr_url}/v1.0/publish/"
                f"{Topics.PUBSUB_NAME}/{Topics.TASK_EVENTS}"
            )
            with httpx.Client(timeout=2.0) as client:
                response = client.post(
                    url,
                    json=event_dict,
                    headers={"Content-Type": "application/cloudevents+json"},
                )
                if response.status_code in (200, 204):
                    logger.info("Event published: %s", event.id)
                    return True
                else:
                    logger.warning(
                        "Dapr publish returned %d: %s",
                        response.status_code,
                        response.text,
                    )
                    return False
        except httpx.ConnectError:
            logger.debug(
                "Dapr sidecar not available, event logged only (local dev mode)"
            )
            return True
        except Exception:
            logger.exception("Failed to publish event %s", event.id)
            return False
