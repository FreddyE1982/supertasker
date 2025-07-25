from datetime import datetime, date, time
from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    color: str
    preferred_start_hour: int | None = None
    preferred_end_hour: int | None = None
    energy_curve: list[int] | None = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    energy_curve: list[int] | None = None

    model_config = ConfigDict(from_attributes=True)


class AppointmentBase(BaseModel):
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    category_id: int | None = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(AppointmentBase):
    pass


class Appointment(AppointmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: date
    start_date: date | None = None
    end_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    category_id: int | None = None
    perceived_difficulty: int | None = None
    estimated_difficulty: int | None = None
    estimated_duration_minutes: int | None = None
    priority: int = 3
    worked_on: bool = False
    paused: bool = False


class TaskCreate(TaskBase):
    pass


class PlanTaskCreate(BaseModel):
    title: str
    description: str | None = None
    estimated_difficulty: int
    estimated_duration_minutes: int
    due_date: date
    priority: int = 3
    category_id: int | None = None
    high_energy_start_hour: int | None = None
    high_energy_end_hour: int | None = None
    fatigue_break_factor: float | None = None
    energy_curve: list[int] | None = None
    energy_day_order_weight: float | None = None
    category_day_weight: float | None = None
    transition_buffer_minutes: int | None = None
    intelligent_transition_buffer: bool | None = None
    productivity_history_weight: float | None = None
    productivity_half_life_days: int | None = None
    category_productivity_weight: float | None = None
    spaced_repetition_factor: float | None = None


class TaskUpdate(TaskBase):
    pass


class Task(TaskBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SubtaskBase(BaseModel):
    title: str
    completed: bool = False


class SubtaskCreate(SubtaskBase):
    pass


class SubtaskUpdate(SubtaskBase):
    pass


class Subtask(SubtaskBase):
    id: int
    task_id: int

    model_config = ConfigDict(from_attributes=True)


class FocusSessionBase(BaseModel):
    start_time: datetime
    end_time: datetime
    completed: bool = False


class FocusSessionCreate(BaseModel):
    duration_minutes: int
    start_time: datetime | None = None


class FocusSessionUpdate(BaseModel):
    end_time: datetime | None = None
    completed: bool | None = None


class FocusSession(FocusSessionBase):
    id: int
    task_id: int

    model_config = ConfigDict(from_attributes=True)
