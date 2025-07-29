from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.orm import relationship

from .database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    color = Column(String, nullable=False)
    preferred_start_hour = Column(Integer, nullable=True)
    preferred_end_hour = Column(Integer, nullable=True)
    energy_curve = Column(String, nullable=True)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category")
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    timezone = Column(String, nullable=True, default="UTC")
    tags = relationship("Tag", secondary="appointment_tags")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category")
    perceived_difficulty = Column(Integer, nullable=True)
    estimated_difficulty = Column(Integer, nullable=True)
    estimated_duration_minutes = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=False, default=3)
    worked_on = Column(Boolean, default=False)
    paused = Column(Boolean, default=False)
    completion_percentage = Column(Integer, nullable=False, default=0)
    tags = relationship("Tag", secondary="task_tags")

    subtasks = relationship(
        "Subtask", back_populates="task", cascade="all, delete-orphan"
    )
    focus_sessions = relationship(
        "FocusSession",
        back_populates="task",
        cascade="all, delete-orphan",
    )


class Subtask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    task = relationship("Task", back_populates="subtasks")


class FocusSession(Base):
    __tablename__ = "focus_sessions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=False)

    task = relationship("Task", back_populates="focus_sessions")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)


class TaskTag(Base):
    __tablename__ = "task_tags"

    task_id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


class AppointmentTag(Base):
    __tablename__ = "appointment_tags"

    appointment_id = Column(Integer, ForeignKey("appointments.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


class RateLimit(Base):
    __tablename__ = "rate_limits"

    ip = Column(String, primary_key=True)
    window_start = Column(DateTime, nullable=False)
    count = Column(Integer, nullable=False, default=0)
