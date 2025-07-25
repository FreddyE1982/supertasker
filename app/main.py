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

    def _session_counts(self) -> dict[date, int]:
        """Return the number of focus sessions already scheduled per day."""
        counts: dict[date, int] = {}
        for fs in self.db.query(models.FocusSession).all():
            d = fs.start_time.date()
            counts[d] = counts.get(d, 0) + 1
        return counts

    def _difficulty_loads(self) -> dict[date, int]:
        """Return the accumulated difficulty score scheduled per day."""
        loads: dict[date, int] = {}
        query = (
            self.db.query(models.FocusSession.start_time, models.Task.estimated_difficulty)
            .join(models.Task, models.Task.id == models.FocusSession.task_id)
            .all()
        )
        for start_time, diff in query:
            d = start_time.date()
            diff_val = diff if diff is not None else 0
            loads[d] = loads.get(d, 0) + diff_val
        return loads

    def _next_work_time(self, dt: datetime) -> datetime:
        start_hour = int(os.getenv("WORK_START_HOUR", "9"))
        end_hour = int(os.getenv("WORK_END_HOUR", "17"))
        work_days_env = os.getenv("WORK_DAYS")
        if work_days_env:
            work_days = {int(d) for d in work_days_env.split(",")}
        else:
            work_days = set(range(7))

        dt = dt.replace(second=0, microsecond=0)
        while dt.weekday() not in work_days:
            dt = dt.replace(hour=start_hour, minute=0) + timedelta(days=1)

        start = dt.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end = dt.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        lunch_start = int(os.getenv("LUNCH_START_HOUR", "12"))
        lunch_dur = int(os.getenv("LUNCH_DURATION_MINUTES", "60"))
        lunch_s = dt.replace(hour=lunch_start, minute=0, second=0, microsecond=0)
        lunch_e = lunch_s + timedelta(minutes=lunch_dur)
        if dt < start:
            dt = start
        elif dt >= end:
            dt = start + timedelta(days=1)
            while dt.weekday() not in work_days:
                dt = dt + timedelta(days=1)
                dt = dt.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        elif lunch_s <= dt < lunch_e:
            dt = lunch_e
            if dt >= end:
                dt = start + timedelta(days=1)
                while dt.weekday() not in work_days:
                    dt = dt + timedelta(days=1)
                    dt = dt.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        return dt

    def _conflicts(
        self, start: datetime, end: datetime, events: list[tuple[datetime, datetime]]
    ) -> bool:
        for s, e in events:
            if start < e and end > s:
                return True
        return False

    def _urgency(self, due: date) -> int:
        """Return an urgency score from 1-5 based on days left until ``due``."""
        days_left = (due - datetime.utcnow().date()).days
        if days_left <= 0:
            return 5
        return max(1, 5 - days_left)

    def _preferred_start_hour(
        self,
        difficulty: int,
        priority: int,
        urgency: int,
        energy_curve: list[int] | None = None,
    ) -> int:
        """Return the preferred start hour based on weighted importance and optional energy curve."""
        start_hour = int(os.getenv("WORK_START_HOUR", "9"))
        end_hour = int(os.getenv("WORK_END_HOUR", "17"))

        if energy_curve is None:
            curve_env = os.getenv("ENERGY_CURVE")
            if curve_env:
                try:
                    curve = [int(x) for x in curve_env.split(",")]
                    if len(curve) == 24:
                        energy_curve = curve
                except ValueError:
                    energy_curve = None

        diff_w = float(os.getenv("DIFFICULTY_WEIGHT", "1"))
        prio_w = float(os.getenv("PRIORITY_WEIGHT", "1"))
        urg_w = float(os.getenv("URGENCY_WEIGHT", "1"))
        total_w = diff_w + prio_w + urg_w

        weight = (
            difficulty * diff_w + priority * prio_w + urgency * urg_w
        ) / total_w

        if energy_curve and len(energy_curve) == 24:
            hours = range(start_hour, end_hour)
            importance = weight
            target = (importance / 5) * max(energy_curve[h] for h in hours)
            best = min(hours, key=lambda h: (energy_curve[h] - target) ** 2)
            return best

        offset = max(0, round(5 - weight))
        return min(end_hour - 1, start_hour + offset)
    def _avoid_low_energy(self, dt: datetime, difficulty: int) -> datetime:
        """Shift start time out of the low energy window for hard tasks."""
        if difficulty < 4:
            return dt
        le_start = int(os.getenv("LOW_ENERGY_START_HOUR", "14"))
        le_end = int(os.getenv("LOW_ENERGY_END_HOUR", "16"))
        if le_start <= dt.hour < le_end:
            return dt.replace(hour=le_end, minute=0, second=0, microsecond=0)
        return dt

    def _prefer_high_energy(
        self,
        dt: datetime,
        difficulty: int,
        priority: int,
        session_len: int,
        start_hour: int,
        end_hour: int,
    ) -> datetime:
        """Move session start into the high energy window for important tasks."""
        if difficulty < 4 and priority < 4:
            return dt
        if end_hour <= start_hour:
            return dt
        if dt.hour < start_hour:
            dt = dt.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        elif dt.hour + math.ceil(session_len / 60) > end_hour:
            dt = dt.replace(hour=start_hour, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return dt

    def _best_energy_slot(
        self,
        start: datetime,
        session_len: int,
        events: list[tuple[datetime, datetime]],
        energy_curve: list[int] | None = None,
    ) -> datetime:
        """Return the best available start time on ``start``'s day based on the
        highest energy level within working hours."""
        if os.getenv("INTELLIGENT_SLOT_SELECTION", "0") not in {"1", "true", "True"}:
            return start

        if energy_curve is None:
            curve_env = os.getenv("ENERGY_CURVE")
            if curve_env:
                try:
                    curve = [int(x) for x in curve_env.split(",")]
                    if len(curve) == 24:
                        energy_curve = curve
                except ValueError:
                    energy_curve = None

        step = int(os.getenv("SLOT_STEP_MINUTES", "15"))
        start_hour = int(os.getenv("WORK_START_HOUR", "9"))
        end_hour = int(os.getenv("WORK_END_HOUR", "17"))

        aligned = start.replace(second=0, microsecond=0)
        day_start = aligned.replace(hour=start_hour, minute=0)
        day_start = day_start - timedelta(minutes=day_start.minute % step)
        day_end = aligned.replace(hour=end_hour, minute=0)
        best = None
        best_energy = -1
        candidate = day_start
        duration = timedelta(minutes=session_len)
        while candidate + duration <= day_end:
            if not self._conflicts(candidate, candidate + duration, events):
                energy = (
                    energy_curve[candidate.hour]
                    if energy_curve and len(energy_curve) == 24
                    else 1
                )
                if energy > best_energy:
                    best_energy = energy
                    best = candidate
            candidate += timedelta(minutes=step)
        return best or start

    def _session_length(self, difficulty: int, priority: int, urgency: int) -> int:
        """Calculate the focus session length with optional intelligent scaling.

        The length now also considers task urgency for smarter scheduling.
        """
        base_len = int(os.getenv("SESSION_LENGTH_MINUTES", "25"))
        if os.getenv("INTELLIGENT_SESSION_LENGTH", "0") not in {"1", "true", "True"}:
            return base_len
        min_len = int(os.getenv("MIN_SESSION_LENGTH_MINUTES", str(base_len)))
        max_len = int(os.getenv("MAX_SESSION_LENGTH_MINUTES", str(base_len)))
        diff_w = float(os.getenv("DIFFICULTY_WEIGHT", "1"))
        prio_w = float(os.getenv("PRIORITY_WEIGHT", "1"))
        urg_w = float(os.getenv("URGENCY_WEIGHT", "1"))
        total_w = diff_w + prio_w + urg_w
        weight = (
            difficulty * diff_w + priority * prio_w + urgency * urg_w
        ) / total_w
        scale = 1 + (weight - 3) / 4
        length = round(base_len * scale)
        return max(min_len, min(max_len, length))

    def _break_lengths(self, session_len: int, difficulty: int) -> tuple[int, int]:
        """Return (short_break, long_break) with optional intelligent scaling."""
        short_base = int(os.getenv("SHORT_BREAK_MINUTES", "5"))
        long_base = int(os.getenv("LONG_BREAK_MINUTES", "15"))
        if os.getenv("INTELLIGENT_BREAKS", "0") not in {"1", "true", "True"}:
            return short_base, long_base

        min_short = int(os.getenv("MIN_SHORT_BREAK_MINUTES", str(short_base)))
        max_short = int(os.getenv("MAX_SHORT_BREAK_MINUTES", str(short_base)))
        min_long = int(os.getenv("MIN_LONG_BREAK_MINUTES", str(long_base)))
        max_long = int(os.getenv("MAX_LONG_BREAK_MINUTES", str(long_base)))

        weight = difficulty / 5
        short = round(short_base * (1 + weight / 2))
        long = round(long_base * (1 + weight / 2))
        short = max(min_short, min(max_short, short))
        long = max(min_long, min(max_long, long))
        return short, long

    def _free_minutes(
        self, day: date, events: list[tuple[datetime, datetime]]
    ) -> int:
        """Return available working minutes on ``day`` excluding existing events."""
        start_hour = int(os.getenv("WORK_START_HOUR", "9"))
        end_hour = int(os.getenv("WORK_END_HOUR", "17"))
        lunch_start = int(os.getenv("LUNCH_START_HOUR", "12"))
        lunch_dur = int(os.getenv("LUNCH_DURATION_MINUTES", "60"))
        work_start = datetime.combine(day, time(hour=start_hour))
        work_end = datetime.combine(day, time(hour=end_hour))
        lunch_s = datetime.combine(day, time(hour=lunch_start))
        lunch_e = lunch_s + timedelta(minutes=lunch_dur)

        intervals = [(work_start, lunch_s), (lunch_e, work_end)]
        total = sum(int((e - s).total_seconds() // 60) for s, e in intervals)
        busy = 0
        for s, e in events:
            for ws, we in intervals:
                overlap_start = max(s, ws)
                overlap_end = min(e, we)
                if overlap_start < overlap_end:
                    busy += int((overlap_end - overlap_start).total_seconds() // 60)
        return max(0, total - busy)

    def _available_energy(
        self,
        day: date,
        events: list[tuple[datetime, datetime]],
        energy_curve: list[int] | None = None,
    ) -> int:
        """Return a weighted energy score for all free minutes on ``day``."""
        if energy_curve is None:
            curve_env = os.getenv("ENERGY_CURVE")
            if curve_env:
                try:
                    curve = [int(x) for x in curve_env.split(",")]
                    if len(curve) == 24:
                        energy_curve = curve
                except ValueError:
                    energy_curve = None

        start_hour = int(os.getenv("WORK_START_HOUR", "9"))
        end_hour = int(os.getenv("WORK_END_HOUR", "17"))
        lunch_start = int(os.getenv("LUNCH_START_HOUR", "12"))
        lunch_dur = int(os.getenv("LUNCH_DURATION_MINUTES", "60"))

        intervals = [
            (
                datetime.combine(day, time(hour=start_hour)),
                datetime.combine(day, time(hour=lunch_start)),
            ),
            (
                datetime.combine(day, time(hour=lunch_start))
                + timedelta(minutes=lunch_dur),
                datetime.combine(day, time(hour=end_hour)),
            ),
        ]
        step = int(os.getenv("SLOT_STEP_MINUTES", "15"))
        score = 0
        for s, e in intervals:
            t = s
            while t < e:
                block_end = t + timedelta(minutes=step)
                if not self._conflicts(t, block_end, events):
                    level = (
                        energy_curve[t.hour]
                        if energy_curve and len(energy_curve) == 24
                        else 1
                    )
                    score += level
                t = block_end
        return score

    def _day_free_blocks(
        self, day: date, events: list[tuple[datetime, datetime]]
    ) -> list[tuple[datetime, datetime]]:
        """Return free intervals within the working hours of ``day``."""
        start_hour = int(os.getenv("WORK_START_HOUR", "9"))
        end_hour = int(os.getenv("WORK_END_HOUR", "17"))
        lunch_start = int(os.getenv("LUNCH_START_HOUR", "12"))
        lunch_dur = int(os.getenv("LUNCH_DURATION_MINUTES", "60"))

        blocks = [
            (
                datetime.combine(day, time(hour=start_hour)),
                datetime.combine(day, time(hour=lunch_start)),
            ),
            (
                datetime.combine(day, time(hour=lunch_start))
                + timedelta(minutes=lunch_dur),
                datetime.combine(day, time(hour=end_hour)),
            ),
        ]
        for s, e in sorted(events, key=lambda x: x[0]):
            if s.date() > day or e.date() < day:
                continue
            new_blocks: list[tuple[datetime, datetime]] = []
            for b_start, b_end in blocks:
                if e <= b_start or s >= b_end:
                    new_blocks.append((b_start, b_end))
                else:
                    if b_start < s:
                        new_blocks.append((b_start, s))
                    if e < b_end:
                        new_blocks.append((e, b_end))
            blocks = new_blocks
            if not blocks:
                break
        return blocks

    def _largest_free_block(
        self, day: date, events: list[tuple[datetime, datetime]]
    ) -> tuple[datetime, datetime] | None:
        """Return the largest free interval on ``day`` if available."""
        blocks = self._day_free_blocks(day, events)
        if not blocks:
            return None
        return max(blocks, key=lambda b: b[1] - b[0])

    def _next_day_by_free_time(
        self,
        start: date,
        last_day: date,
        events: list[tuple[datetime, datetime]],
        work_days: set[int],
        energy_curve: list[int] | None = None,
        energy_weight: float | None = None,
    ) -> date:
        """Return the next planning day using free time and optional energy weighting."""
        days: list[date] = []
        d = start
        while d <= last_day:
            if d.weekday() in work_days:
                days.append(d)
            d += timedelta(days=1)
        if not days:
            raise HTTPException(status_code=400, detail="Cannot schedule before due date")
        if os.getenv("INTELLIGENT_DAY_ORDER", "0") in {"1", "true", "True"}:
            if energy_weight is None:
                energy_weight = float(os.getenv("ENERGY_DAY_ORDER_WEIGHT", "0"))
            days.sort(
                key=lambda day: (
                    self._free_minutes(day, events)
                    + energy_weight * self._available_energy(day, events, energy_curve)
                ),
                reverse=True,
            )
        return days[0]


    def _schedule_sessions(
        self,
        duration: int,
        due: date,
        events: list[tuple[datetime, datetime]],
        difficulty: int,
        priority: int,
        high_energy_start: int | None = None,
        high_energy_end: int | None = None,
        fatigue_break_factor: float | None = None,
        energy_curve: list[int] | None = None,
        energy_day_order_weight: float | None = None,
    ) -> list[tuple[datetime, datetime]]:
        urgency = self._urgency(due)
        session_len = self._session_length(difficulty, priority, urgency)
        short_break, long_break = self._break_lengths(session_len, difficulty)
        long_interval = int(os.getenv("SESSIONS_BEFORE_LONG_BREAK", "4"))
        max_per_day = int(os.getenv("MAX_SESSIONS_PER_DAY", "4"))
        needed = (duration + session_len - 1) // session_len

        he_start = (
            high_energy_start
            if high_energy_start is not None
            else int(os.getenv("HIGH_ENERGY_START_HOUR", "9"))
        )
        he_end = (
            high_energy_end
            if high_energy_end is not None
            else int(os.getenv("HIGH_ENERGY_END_HOUR", "12"))
        )

        daily_limit = int(os.getenv("DAILY_SESSION_LIMIT", "0"))
        daily_counts = self._session_counts()
        difficulty_limit = int(os.getenv("DAILY_DIFFICULTY_LIMIT", "0"))
        difficulty_loads = self._difficulty_loads()

        now = self._next_work_time(datetime.utcnow())
        preferred = self._preferred_start_hour(
            difficulty, priority, urgency, energy_curve
        )
        days_left = max(1, (due - now.date()).days + 1)

        diff_w = float(os.getenv("DIFFICULTY_WEIGHT", "1"))
        prio_w = float(os.getenv("PRIORITY_WEIGHT", "1"))
        urg_w = float(os.getenv("URGENCY_WEIGHT", "1"))
        total_w = diff_w + prio_w + urg_w
        importance = (
            difficulty * diff_w + priority * prio_w + urgency * urg_w
        ) / total_w

        target_per_day = min(
            max_per_day,
            max(1, math.ceil((needed / days_left) * (1 + (importance - 3) / 2))),
        )
        work_days_env = os.getenv("WORK_DAYS")
        if work_days_env:
            work_days = {int(d) for d in work_days_env.split(",")}
        else:
            work_days = set(range(7))
        days_needed = math.ceil(needed / target_per_day)
        last_work_day = due
        while last_work_day.weekday() not in work_days:
            last_work_day -= timedelta(days=1)

        offset = round((importance - 1) / 4 * days_left * 0.5)
        start_candidate = last_work_day - timedelta(days=days_needed - 1 + offset)
        start_day = max(now.date(), start_candidate)
        start_day = self._next_day_by_free_time(
            start_day,
            last_work_day,
            events,
            work_days,
            energy_curve,
            energy_day_order_weight,
        )
        deep_threshold = int(os.getenv("DEEP_WORK_THRESHOLD", "0"))
        if deep_threshold and difficulty >= deep_threshold:
            total_needed = needed * session_len + short_break * (needed - 1)
            day = start_day
            while day <= last_work_day:
                if day.weekday() not in work_days:
                    day += timedelta(days=1)
                    continue
                block = self._largest_free_block(day, events)
                if block and (block[1] - block[0]).total_seconds() // 60 >= total_needed:
                    now = max(block[0], datetime.combine(day, time(hour=preferred)))
                    sessions: list[tuple[datetime, datetime]] = []
                    since_break = 0
                    for _ in range(needed):
                        start = now
                        end = start + timedelta(minutes=session_len)
                        sessions.append((start, end))
                        events.append((start, end))
                        now = end
                        if len(sessions) == needed:
                            break
                        break_len = long_break if since_break == long_interval - 1 else short_break
                        break_end = now + timedelta(minutes=break_len)
                        events.append((now, break_end))
                        now = break_end
                        since_break = (since_break + 1) % long_interval
                    return sessions
                day += timedelta(days=1)
        now = self._next_work_time(datetime.combine(start_day, time(hour=preferred)))
        if now.hour < preferred:
            now = now.replace(hour=preferred, minute=0, second=0, microsecond=0)
        free_today = self._free_minutes(now.date(), events)
        required_today = needed * session_len + short_break * (needed - 1)
        if required_today <= free_today and due <= now.date() + timedelta(days=1):
            target_per_day = max_per_day
        sessions: list[tuple[datetime, datetime]] = []
        since_break = 0
        per_day = 0
        while len(sessions) < needed:
            if daily_limit and daily_counts.get(now.date(), 0) >= daily_limit:
                start_hour = int(os.getenv("WORK_START_HOUR", "9"))
                next_day = self._next_day_by_free_time(
                    now.date() + timedelta(days=1),
                    last_work_day,
                    events,
                    work_days,
                    energy_curve,
                    energy_day_order_weight,
                )
                now = self._next_work_time(
                    datetime.combine(next_day, time(hour=start_hour))
                )
                if now.hour < preferred:
                    now = now.replace(hour=preferred, minute=0, second=0, microsecond=0)
                if sessions and now.date() != sessions[-1][0].date():
                    per_day = 0
                continue
            if difficulty_limit and difficulty_loads.get(now.date(), 0) + difficulty > difficulty_limit:
                start_hour = int(os.getenv("WORK_START_HOUR", "9"))
                next_day = self._next_day_by_free_time(
                    now.date() + timedelta(days=1),
                    last_work_day,
                    events,
                    work_days,
                    energy_curve,
                    energy_day_order_weight,
                )
                now = self._next_work_time(
                    datetime.combine(next_day, time(hour=start_hour))
                )
                if now.hour < preferred:
                    now = now.replace(hour=preferred, minute=0, second=0, microsecond=0)
                if sessions and now.date() != sessions[-1][0].date():
                    per_day = 0
                continue
            start = self._avoid_low_energy(now, difficulty)
            start = self._prefer_high_energy(
                start, difficulty, priority, session_len, he_start, he_end
            )
            start = self._best_energy_slot(start, session_len, events, energy_curve)
            if start != now:
                now = self._next_work_time(start)
                start = now
            end = start + timedelta(minutes=session_len)
            lunch_start = int(os.getenv("LUNCH_START_HOUR", "12"))
            lunch_dur = int(os.getenv("LUNCH_DURATION_MINUTES", "60"))
            lunch_s = start.replace(hour=lunch_start, minute=0, second=0, microsecond=0)
            lunch_e = lunch_s + timedelta(minutes=lunch_dur)
            if start < lunch_e and end > lunch_s:
                now = self._next_work_time(lunch_e)
                if now.hour < preferred:
                    now = now.replace(hour=preferred, minute=0, second=0, microsecond=0)
                if sessions and now.date() != sessions[-1][0].date():
                    per_day = 0
                continue
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
            if per_day >= target_per_day:
                remaining_days = max(1, (last_work_day - start.date()).days + 1)
                if remaining_days == 1:
                    target_per_day = max_per_day
                else:
                    start_hour = int(os.getenv("WORK_START_HOUR", "9"))
                    next_day = self._next_day_by_free_time(
                        start.date() + timedelta(days=1),
                        last_work_day,
                        events,
                        work_days,
                        energy_curve,
                        energy_day_order_weight,
                    )
                    now = self._next_work_time(
                        datetime.combine(next_day, time(hour=start_hour))
                    )
                    if now.hour < preferred:
                        now = now.replace(hour=preferred, minute=0, second=0, microsecond=0)
                    per_day = 0
                    remaining_days = max(1, (last_work_day - now.date()).days + 1)
                    target_per_day = min(
                        max_per_day,
                        max(1, math.ceil((needed - len(sessions)) / remaining_days)),
                    )
                    continue
            sessions.append((start, end))
            events.append((start, end))
            break_len = long_break if since_break == long_interval - 1 else short_break
            factor = fatigue_break_factor
            if factor is None:
                factor = float(os.getenv("FATIGUE_BREAK_FACTOR", "0"))
            break_len = round(break_len * (1 + per_day * factor))
            break_end = end + timedelta(minutes=break_len)
            events.append((end, break_end))
            now = self._next_work_time(break_end)
            if now.hour < preferred:
                now = now.replace(hour=preferred, minute=0, second=0, microsecond=0)
            since_break = (since_break + 1) % long_interval
            per_day += 1
            daily_counts[start.date()] = daily_counts.get(start.date(), 0) + 1
            difficulty_loads[start.date()] = difficulty_loads.get(start.date(), 0) + difficulty
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
            data.high_energy_start_hour,
            data.high_energy_end_hour,
            data.fatigue_break_factor,
            data.energy_curve,
            data.energy_day_order_weight,
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
