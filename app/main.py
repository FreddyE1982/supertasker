from datetime import datetime, date, time, timedelta
import os
import math
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class FocusSessionService:
    """Manage focus sessions for tasks."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, task_id: int, duration_minutes: int) -> models.FocusSession:
        task = self.db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        start = datetime.utcnow()
        end = start + timedelta(minutes=duration_minutes)
        session = models.FocusSession(
            task_id=task_id, start_time=start, end_time=end, completed=False
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def list(self, task_id: int) -> list[models.FocusSession]:
        return (
            self.db.query(models.FocusSession)
            .filter(models.FocusSession.task_id == task_id)
            .all()
        )

    def update(
        self, task_id: int, session_id: int, data: schemas.FocusSessionUpdate
    ) -> models.FocusSession:
        session = (
            self.db.query(models.FocusSession)
            .filter(
                models.FocusSession.id == session_id,
                models.FocusSession.task_id == task_id,
            )
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Focus session not found")
        for field, value in data.dict(exclude_unset=True).items():
            setattr(session, field, value)
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete(self, task_id: int, session_id: int) -> None:
        session = (
            self.db.query(models.FocusSession)
            .filter(
                models.FocusSession.id == session_id,
                models.FocusSession.task_id == task_id,
            )
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Focus session not found")
        self.db.delete(session)
        self.db.commit()


class TaskPlanner:
    """Automatically schedule tasks into available calendar slots.

    The planner respects configurable working hours via the ``WORK_START_HOUR``
    and ``WORK_END_HOUR`` environment variables. Sessions are scheduled earlier
    in the day for difficult tasks and later for easier ones to make planning
    more intelligent while still preventing overlaps with existing events.
    """

    def __init__(self, db: Session):
        self.db = db

    def _collect_events(self) -> list[tuple[datetime, datetime]]:
        events: list[tuple[datetime, datetime]] = []
        for appt in self.db.query(models.Appointment).all():
            events.append((appt.start_time, appt.end_time))
        for fs in self.db.query(models.FocusSession).all():
            events.append((fs.start_time, fs.end_time))
        for task in (
            self.db.query(models.Task)
            .filter(models.Task.start_date.isnot(None))
            .filter(models.Task.start_time.isnot(None))
            .filter(models.Task.end_date.isnot(None))
            .filter(models.Task.end_time.isnot(None))
            .all()
        ):
            sdt = datetime.combine(task.start_date, task.start_time)
            edt = datetime.combine(task.end_date, task.end_time)
            events.append((sdt, edt))
        events.sort(key=lambda e: e[0])
        return events

    def _next_work_time(self, dt: datetime) -> datetime:
        start_hour = int(os.getenv("WORK_START_HOUR", "9"))
        end_hour = int(os.getenv("WORK_END_HOUR", "17"))
        start = dt.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end = dt.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        if dt < start:
            return start
        if dt >= end:
            return start + timedelta(days=1)
        return dt

    def _conflicts(
        self, start: datetime, end: datetime, events: list[tuple[datetime, datetime]]
    ) -> bool:
        for s, e in events:
            if start < e and end > s:
                return True
        return False

    def _preferred_start_hour(self, difficulty: int, priority: int) -> int:
        start_hour = int(os.getenv("WORK_START_HOUR", "9"))
        end_hour = int(os.getenv("WORK_END_HOUR", "17"))
        offset = max(0, 5 - difficulty - (priority - 3))
        return min(end_hour - 1, start_hour + offset)

    def _schedule_sessions(
        self,
        duration: int,
        due: date,
        events: list[tuple[datetime, datetime]],
        difficulty: int,
        priority: int,
    ) -> list[tuple[datetime, datetime]]:
        session_len = 25
        short_break = 5
        long_break = 15
        max_per_day = int(os.getenv("MAX_SESSIONS_PER_DAY", "4"))
        needed = (duration + session_len - 1) // session_len

        now = self._next_work_time(datetime.utcnow())
        preferred = self._preferred_start_hour(difficulty, priority)
        days_needed = math.ceil(needed / max_per_day)
        start_day = max(now.date(), due - timedelta(days=days_needed - 1))
        now = self._next_work_time(datetime.combine(start_day, time(hour=preferred)))
        if now.hour < preferred:
            now = now.replace(hour=preferred, minute=0, second=0, microsecond=0)
        sessions: list[tuple[datetime, datetime]] = []
        since_break = 0
        per_day = 0
        while len(sessions) < needed:
            start = now
            end = start + timedelta(minutes=session_len)
            if end.date() > due:
                raise HTTPException(status_code=400, detail="Cannot schedule before due date")
            end_hour = int(os.getenv("WORK_END_HOUR", "17"))
            if end.hour > end_hour or (end.hour == end_hour and end.minute > 0):
                now = self._next_work_time(start + timedelta(days=1))
                if now.hour < preferred:
                    now = now.replace(hour=preferred, minute=0, second=0, microsecond=0)
                per_day = 0
                continue
            if self._conflicts(start, end, events):
                overlap_end = max(e for s, e in events if start < e and end > s)
                now = self._next_work_time(overlap_end)
                if now.hour < preferred:
                    now = now.replace(hour=preferred, minute=0, second=0, microsecond=0)
                if sessions and now.date() != sessions[-1][0].date():
                    per_day = 0
                continue
            if per_day >= max_per_day:
                start_hour = int(os.getenv("WORK_START_HOUR", "9"))
                now = self._next_work_time(
                    datetime.combine(start.date() + timedelta(days=1), time(hour=start_hour))
                )
                if now.hour < preferred:
                    now = now.replace(hour=preferred, minute=0, second=0, microsecond=0)
                per_day = 0
                continue
            sessions.append((start, end))
            events.append((start, end))
            break_len = long_break if since_break == 3 else short_break
            break_end = end + timedelta(minutes=break_len)
            events.append((end, break_end))
            now = self._next_work_time(break_end)
            if now.hour < preferred:
                now = now.replace(hour=preferred, minute=0, second=0, microsecond=0)
            since_break = (since_break + 1) % 4
            per_day += 1
        return sessions

    def plan(self, data: schemas.PlanTaskCreate) -> models.Task:
        task = models.Task(
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            estimated_difficulty=data.estimated_difficulty,
            estimated_duration_minutes=data.estimated_duration_minutes,
            priority=data.priority,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        events = self._collect_events()
        sessions = self._schedule_sessions(
            data.estimated_duration_minutes,
            data.due_date,
            events,
            data.estimated_difficulty,
            data.priority,
        )

        for idx, (s, e) in enumerate(sessions, start=1):
            fs = models.FocusSession(
                task_id=task.id,
                start_time=s,
                end_time=e,
                completed=False,
            )
            self.db.add(fs)
            sub = models.Subtask(
                task_id=task.id,
                title=f"Part {idx}",
                completed=False,
            )
            self.db.add(sub)
        if sessions:
            task.start_date = sessions[0][0].date()
            task.start_time = sessions[0][0].time()
            task.end_date = sessions[-1][1].date()
            task.end_time = sessions[-1][1].time()
        self.db.commit()
        self.db.refresh(task)
        return task
        

@app.post("/categories", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_cat = models.Category(**category.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


@app.get("/categories", response_model=list[schemas.Category])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@app.post('/appointments', response_model=schemas.Appointment)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    if appointment.category_id is not None:
        cat = db.query(models.Category).filter(models.Category.id == appointment.category_id).first()
        if cat is None:
            raise HTTPException(status_code=404, detail="Category not found")
    db_app = models.Appointment(**appointment.dict())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get('/appointments', response_model=list[schemas.Appointment])
def list_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointment).all()

@app.put('/appointments/{appointment_id}', response_model=schemas.Appointment)
def update_appointment(appointment_id: int, appointment: schemas.AppointmentUpdate, db: Session = Depends(get_db)):
    db_app = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail='Appointment not found')
    if appointment.category_id is not None:
        cat = db.query(models.Category).filter(models.Category.id == appointment.category_id).first()
        if cat is None:
            raise HTTPException(status_code=404, detail="Category not found")
    for field, value in appointment.dict().items():
        setattr(db_app, field, value)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.delete('/appointments/{appointment_id}')
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_app = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail='Appointment not found')
    db.delete(db_app)
    db.commit()
    return {'detail': 'Deleted'}


@app.post('/tasks', response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.post('/tasks/plan', response_model=schemas.Task)
def plan_task(data: schemas.PlanTaskCreate, db: Session = Depends(get_db)):
    planner = TaskPlanner(db)
    return planner.plan(data)


@app.get('/tasks', response_model=list[schemas.Task])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()


@app.put('/tasks/{task_id}', response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail='Task not found')
    for field, value in task.dict().items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete('/tasks/{task_id}')
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail='Task not found')
    db.delete(db_task)
    db.commit()
    return {'detail': 'Deleted'}


@app.post('/tasks/{task_id}/subtasks', response_model=schemas.Subtask)
def create_subtask(task_id: int, subtask: schemas.SubtaskCreate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')
    db_sub = models.Subtask(task_id=task_id, **subtask.dict())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub


@app.get('/tasks/{task_id}/subtasks', response_model=list[schemas.Subtask])
def list_subtasks(task_id: int, db: Session = Depends(get_db)):
    return db.query(models.Subtask).filter(models.Subtask.task_id == task_id).all()


@app.put('/tasks/{task_id}/subtasks/{subtask_id}', response_model=schemas.Subtask)
def update_subtask(task_id: int, subtask_id: int, subtask: schemas.SubtaskUpdate, db: Session = Depends(get_db)):
    db_sub = db.query(models.Subtask).filter(models.Subtask.id == subtask_id, models.Subtask.task_id == task_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail='Subtask not found')
    for field, value in subtask.dict().items():
        setattr(db_sub, field, value)
    db.commit()
    db.refresh(db_sub)
    return db_sub


@app.delete('/tasks/{task_id}/subtasks/{subtask_id}')
def delete_subtask(task_id: int, subtask_id: int, db: Session = Depends(get_db)):
    db_sub = db.query(models.Subtask).filter(models.Subtask.id == subtask_id, models.Subtask.task_id == task_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail='Subtask not found')
    db.delete(db_sub)
    db.commit()
    return {'detail': 'Deleted'}


@app.post('/tasks/{task_id}/focus_sessions', response_model=schemas.FocusSession)
def create_focus_session(task_id: int, fs: schemas.FocusSessionCreate, db: Session = Depends(get_db)):
    service = FocusSessionService(db)
    return service.create(task_id, fs.duration_minutes)


@app.get('/tasks/{task_id}/focus_sessions', response_model=list[schemas.FocusSession])
def list_focus_sessions(task_id: int, db: Session = Depends(get_db)):
    service = FocusSessionService(db)
    return service.list(task_id)


@app.put('/tasks/{task_id}/focus_sessions/{session_id}', response_model=schemas.FocusSession)
def update_focus_session(task_id: int, session_id: int, fs: schemas.FocusSessionUpdate, db: Session = Depends(get_db)):
    service = FocusSessionService(db)
    return service.update(task_id, session_id, fs)


@app.delete('/tasks/{task_id}/focus_sessions/{session_id}')
def delete_focus_session(task_id: int, session_id: int, db: Session = Depends(get_db)):
    service = FocusSessionService(db)
    service.delete(task_id, session_id)
    return {'detail': 'Deleted'}
