from __future__ import annotations

from fastapi import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Gauge,
    generate_latest,
)
from sqlalchemy.orm import Session

from . import models
from .database import SessionLocal


class MetricsService:
    """Collect and expose application metrics."""

    _registry = CollectorRegistry()
    _task_gauge = Gauge(
        "tasks_total",
        "Total number of tasks",
        registry=_registry,
    )
    _appt_gauge = Gauge(
        "appointments_total",
        "Total number of appointments",
        registry=_registry,
    )
    _category_gauge = Gauge(
        "categories_total",
        "Total number of categories",
        registry=_registry,
    )

    def __init__(self, db: Session | None = None) -> None:
        self.db = db or SessionLocal()

    def _update_gauges(self) -> None:
        self._task_gauge.set(self.db.query(models.Task).count())
        self._appt_gauge.set(self.db.query(models.Appointment).count())
        self._category_gauge.set(self.db.query(models.Category).count())

    def stats(self) -> dict[str, int]:
        self._update_gauges()
        return {
            "tasks": int(self._task_gauge._value.get()),
            "appointments": int(self._appt_gauge._value.get()),
            "categories": int(self._category_gauge._value.get()),
        }

    def prometheus(self) -> Response:
        self._update_gauges()
        return Response(generate_latest(self._registry), media_type=CONTENT_TYPE_LATEST)
