# Calendar App

This project provides a simple calendar application with a REST API and a Streamlit GUI. Users can create, update, delete, and list appointments.
It also supports managing tasks with optional subtasks. Subtasks are useful for breaking large tasks into smaller steps, which can be helpful for users with ADHD.
Additionally, tasks now support **focus sessions** to encourage short, timed work intervals. This feature is designed with ADHD users in mind to aid concentration.
Tasks also have a **priority** level from 1-5 to help ADHD users identify what to focus on first.

## Requirements

- Python 3.10+
- pip

Install dependencies:

```bash
pip install fastapi uvicorn sqlalchemy pydantic requests streamlit pytest
```

## Running the API

```bash
uvicorn app.main:app
```

The API will be available at `http://localhost:8000`.

## Running the Streamlit GUI

```bash
streamlit run streamlit_app.py
```

## Running Tests

To run all tests:

```bash
pytest
```

To run only the GUI tests:

```bash
pytest tests/test_gui.py
```

## Automatic Dependency Installation

Importing the `autoinstaller` module installs any missing Python packages
discovered in the project. Set `AUTOINSTALL_PATH` to scan a different directory
before importing the module.

## Subtask API

Subtasks are managed via the following endpoints:

- `POST /tasks/{task_id}/subtasks` – create a new subtask for a task
- `GET /tasks/{task_id}/subtasks` – list subtasks of a task
- `PUT /tasks/{task_id}/subtasks/{subtask_id}` – update a subtask
- `DELETE /tasks/{task_id}/subtasks/{subtask_id}` – delete a subtask

## Task Priority

Each task has a `priority` from 1 (lowest) to 5 (highest). Use this field when
creating or updating tasks to highlight important items.

## Focus Session API

Focus sessions help break work into manageable chunks. Endpoints:

- `POST /tasks/{task_id}/focus_sessions` – start a focus session
- `GET /tasks/{task_id}/focus_sessions` – list focus sessions for a task
- `PUT /tasks/{task_id}/focus_sessions/{session_id}` – update a focus session
- `DELETE /tasks/{task_id}/focus_sessions/{session_id}` – delete a focus session

## Automatic Task Planning

Create and schedule tasks in one step with `POST /tasks/plan`.
Send JSON with `title`, `description`, `estimated_difficulty`,
`estimated_duration_minutes`, `due_date` and optional `priority`.
The service splits the work into 25-minute focus sessions with
Pomodoro-style breaks and ensures no overlap with existing calendar entries.
Sessions are interlaced with all current appointments and tasks so that work
fits naturally into the free slots of the day. Each focus session also creates
a corresponding subtask so large tasks are automatically broken into manageable
parts.
The planner honours the ``WORK_START_HOUR`` and ``WORK_END_HOUR`` environment
variables as well as ``MAX_SESSIONS_PER_DAY`` to adapt to custom working hours
and workload distribution. Additional settings allow advanced tuning:

- ``SESSION_LENGTH_MINUTES`` – duration of each focus session (default 25)
- ``INTELLIGENT_SESSION_LENGTH`` – scale session length based on difficulty and priority when set to ``1`` or ``true`` (default disabled)
- ``MIN_SESSION_LENGTH_MINUTES`` – minimum allowed session length when intelligent scaling is enabled (default ``SESSION_LENGTH_MINUTES``)
- ``MAX_SESSION_LENGTH_MINUTES`` – maximum allowed session length when intelligent scaling is enabled (default ``SESSION_LENGTH_MINUTES``)
- ``SHORT_BREAK_MINUTES`` – short break length (default 5)
- ``LONG_BREAK_MINUTES`` – long break length (default 15)
- ``INTELLIGENT_BREAKS`` – scale break lengths based on task difficulty when set to ``1`` or ``true`` (default disabled)
- ``MIN_SHORT_BREAK_MINUTES`` – minimum short break when intelligent breaks are enabled (default ``SHORT_BREAK_MINUTES``)
- ``MAX_SHORT_BREAK_MINUTES`` – maximum short break when intelligent breaks are enabled (default ``SHORT_BREAK_MINUTES``)
- ``MIN_LONG_BREAK_MINUTES`` – minimum long break when intelligent breaks are enabled (default ``LONG_BREAK_MINUTES``)
- ``MAX_LONG_BREAK_MINUTES`` – maximum long break when intelligent breaks are enabled (default ``LONG_BREAK_MINUTES``)
- ``SESSIONS_BEFORE_LONG_BREAK`` – number of sessions before a long break
  is inserted (default 4)
- ``MAX_SESSIONS_PER_DAY`` – maximum sessions per task each day (default 4)
- ``DAILY_SESSION_LIMIT`` – maximum sessions from all tasks on a single day
  (default unlimited)
- ``INTELLIGENT_DAY_ORDER`` – prefer days with more free time when scheduling
  focus sessions (default disabled)
- ``WORK_DAYS`` – comma-separated list of weekday numbers (0=Monday) that are
  considered working days. By default all days are allowed.
- ``LUNCH_START_HOUR`` – hour when a daily lunch break begins (default 12)
- ``LUNCH_DURATION_MINUTES`` – length of the lunch break (default 60)
- ``DIFFICULTY_WEIGHT`` – weight of difficulty when calculating importance (default 1)
- ``PRIORITY_WEIGHT`` – weight of priority when calculating importance (default 1)
- ``URGENCY_WEIGHT`` – weight of due date urgency when calculating importance (default 1)

- ``LOW_ENERGY_START_HOUR`` – start of the low energy period to avoid for difficult tasks (default 14)
- ``LOW_ENERGY_END_HOUR`` – end hour of the low energy period (default 16)
- ``HIGH_ENERGY_START_HOUR`` – preferred start hour for important tasks (default 9)
- ``HIGH_ENERGY_END_HOUR`` – end of the preferred high energy window (default 12)

More difficult or high priority tasks are placed earlier in the day while
easier ones are scheduled later, spreading sessions across days when needed for
smarter and more personalised planning. Important tasks start earlier in the
schedule by weighting difficulty, priority and urgency using the weight
variables above. Session times also consider urgency based on how soon a task is
due and the planner balances the number of focus sessions per day so that work
is spread evenly until the deadline.
The lunch break settings ensure planning pauses between ``LUNCH_START_HOUR``
and ``LUNCH_START_HOUR`` plus ``LUNCH_DURATION_MINUTES`` so focus sessions never
overlap with this daily break.
Hard tasks are also moved out of the ``LOW_ENERGY_START_HOUR`` to ``LOW_ENERGY_END_HOUR`` window to keep sessions productive.
Important tasks are additionally pulled into the ``HIGH_ENERGY_START_HOUR`` to ``HIGH_ENERGY_END_HOUR`` window whenever possible so the most challenging work occurs during peak focus times.
