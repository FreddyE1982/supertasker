from datetime import datetime, date, time as dtime, timedelta
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
    """Automatically schedule tasks into available calendar slots."""

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
        start = dt.replace(hour=9, minute=0, second=0, microsecond=0)
        end = dt.replace(hour=17, minute=0, second=0, microsecond=0)
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

    def _schedule_sessions(
        self, duration: int, due: date, events: list[tuple[datetime, datetime]]
    ) -> list[tuple[datetime, datetime]]:
        session_len = 25
        short_break = 5
        long_break = 15
        needed = (duration + session_len - 1) // session_len

        now = self._next_work_time(datetime.utcnow())
        sessions: list[tuple[datetime, datetime]] = []
        since_break = 0
        while len(sessions) < needed:
            start = now
            end = start + timedelta(minutes=session_len)
            if end.date() > due:
                raise HTTPException(status_code=400, detail="Cannot schedule before due date")
            if end.hour > 17 or (end.hour == 17 and end.minute > 0):
                now = self._next_work_time(start + timedelta(days=1))
                continue
            if self._conflicts(start, end, events):
                overlap_end = max(e for s, e in events if start < e and end > s)
                now = self._next_work_time(overlap_end)
                continue
            sessions.append((start, end))
            events.append((start, end))
            break_len = long_break if since_break == 3 else short_break
            break_end = end + timedelta(minutes=break_len)
            events.append((end, break_end))
            now = self._next_work_time(break_end)
            since_break = (since_break + 1) % 4
        return sessions

    def plan(self, data: schemas.PlanTaskCreate) -> models.Task:
        task = models.Task(
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            estimated_difficulty=data.estimated_difficulty,
            estimated_duration_minutes=data.estimated_duration_minutes,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        events = self._collect_events()
        sessions = self._schedule_sessions(data.estimated_duration_minutes, data.due_date, events)

        for s, e in sessions:
            fs = models.FocusSession(task_id=task.id, start_time=s, end_time=e, completed=False)
            self.db.add(fs)
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
