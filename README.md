# Calendar App
[Deutschsprachige Anleitung](README_DE.md)


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
The API exposes an OpenAPI schema at `http://localhost:8000/openapi.json` and interactive docs at `http://localhost:8000/docs`.

### Authentication

Create an account via `POST /users`:

```bash
curl -X POST -H "Content-Type: application/json" \
    -d '{"username": "alice", "email": "alice@example.com", "password": "secret"}' \
    http://localhost:8000/users
```

Obtain a JWT token with `POST /token` using form data:

```bash
curl -X POST -d 'username=alice&password=secret' http://localhost:8000/token
```

Include the returned token in the `Authorization` header to access protected endpoints:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/appointments
```

### Logging

Set the log level with `LOG_LEVEL` in `config.yaml` or as an environment variable.

## Running the Streamlit GUI

```bash
streamlit run streamlit_app.py
```

### Dark Mode

The GUI supports an optional dark theme. Enable it via the **Dark Mode**
checkbox at the top of the application.

## Running Tests

To run all tests:

```bash
pytest
```

To run only the GUI tests:

```bash
pytest tests/test_gui.py
```
Run tests with coverage:
```bash
coverage run -m pytest
coverage html
```
Coverage reports appear in `htmlcov`.

This project uses pre-commit hooks for linting, formatting and type checking. Install them with:
```bash
pre-commit install
```
The hooks enforce Black formatting, isort import ordering, flake8 style checks and mypy type analysis.


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

## Categories

Appointments and tasks can optionally belong to categories. Create categories via
`POST /categories` and reference them using `category_id` when creating or
planning tasks or appointments. The planner groups tasks of the same category
close together when ``CATEGORY_CONTEXT_WINDOW`` provides enough room.
Categories may also define ``preferred_start_hour`` and ``preferred_end_hour``
so that tasks of that category are scheduled within a specific time window.
Additionally ``energy_curve`` may specify 24 comma separated numbers giving
relative energy levels for each hour. When set, the planner multiplies the
general energy curve with this category curve for smarter time selection.

## Focus Session API

Focus sessions help break work into manageable chunks. Endpoints:

- `POST /tasks/{task_id}/focus_sessions` – start a focus session
- `GET /tasks/{task_id}/focus_sessions` – list focus sessions for a task
- `PUT /tasks/{task_id}/focus_sessions/{session_id}` – update a focus session
- `DELETE /tasks/{task_id}/focus_sessions/{session_id}` – delete a focus session

## Automatic Task Planning

Create and schedule tasks in one step with `POST /tasks/plan`.
Send JSON with `title`, `description`, `estimated_difficulty`,
`estimated_duration_minutes`, `due_date` and optional `priority`,
`category_id` or `category_day_weight` to group related work and prefer days
that already contain tasks of the same category.
The service splits the work into 25-minute focus sessions with
Pomodoro-style breaks and ensures no overlap with existing calendar entries.
Sessions are interlaced with all current appointments and tasks so that work
fits naturally into the free slots of the day. Each focus session also creates
a corresponding subtask so large tasks are automatically broken into manageable
parts.
The planner honours the ``WORK_START_HOUR`` and ``WORK_END_HOUR`` environment
variables as well as ``MAX_SESSIONS_PER_DAY`` to adapt to custom working hours
and workload distribution. When ``INTELLIGENT_DAY_ORDER`` is enabled it
also weighs the available energy on each day using ``ENERGY_DAY_ORDER_WEIGHT``
so that sessions land on days with both enough time and high energy. Additional
settings allow advanced tuning:

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
- ``ENERGY_DAY_ORDER_WEIGHT`` – additional weight for days with higher available
  energy when intelligent day order is enabled (default 0)
- ``WEEKDAY_ENERGY`` – comma-separated list of seven numbers giving relative
  energy for each weekday starting Monday. Used with intelligent day order to
  prefer days that generally offer better focus (default all ``1``)
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
- ``FATIGUE_BREAK_FACTOR`` – multiply break length by ``1 + sessions_today * factor`` to model fatigue (default 0)
- ``ENERGY_CURVE`` – comma-separated 24 numbers representing energy levels per hour to pick better start times (optional)
- ``INTELLIGENT_SLOT_SELECTION`` – pick the best free time on a day based on the
  highest energy level (default disabled)
- ``SLOT_STEP_MINUTES`` – minutes between candidate start times when intelligent
  slot selection is enabled (default 15)
- ``DEEP_WORK_THRESHOLD`` – difficulty level from 1-5 that triggers scheduling
  all focus sessions for that task consecutively in the largest available block
  (default 0 disables deep work planning)
- ``DAILY_DIFFICULTY_LIMIT`` – maximum total difficulty scheduled per day across
  all tasks (default 0 disables difficulty balancing)
- ``DAILY_ENERGY_LIMIT`` – maximum sum of ``difficulty * session length``
  scheduled per day across all tasks (default 0 disables energy balancing)
- ``TRANSITION_BUFFER_MINUTES`` – minutes of preparation and wrap-up time before and after every focus session (default 0)
- ``INTELLIGENT_TRANSITION_BUFFER`` – scale buffer minutes with task difficulty when set to ``1`` or ``true`` (default disabled)
- ``CATEGORY_CONTEXT_WINDOW`` – minutes around existing same-category tasks to prefer when scheduling (default 60)
- ``CATEGORY_DAY_WEIGHT`` – additional weight favouring days that already contain events of the same category (default 0)
- ``PRODUCTIVITY_HISTORY_WEIGHT`` – weight of past session completion rates per hour when choosing slots (default 0)
- ``PRODUCTIVITY_HALF_LIFE_DAYS`` – days until historical weights halve when calculating productivity (default 30)
- ``CATEGORY_PRODUCTIVITY_WEIGHT`` – weight of category-specific completion rates when selecting slots (default 0)
- ``SPACED_REPETITION_FACTOR`` – multiply the gap between consecutive sessions by this factor for spaced repetition (default 1 disables spacing)
- ``SESSION_COUNT_WEIGHT`` – penalty per already scheduled session on a day when choosing planning days (default 0)
- ``DIFFICULTY_LOAD_WEIGHT`` – penalty based on total difficulty already scheduled on a day (default 0)
- ``ENERGY_LOAD_WEIGHT`` – penalty based on total energy load already scheduled on a day (default 0)
- ``preferred_start_hour`` and ``preferred_end_hour`` – optional fields on categories restricting scheduling to this window
- ``energy_curve`` – optional 24 comma values on categories weighting hours for
  category tasks

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
Providing an ``ENERGY_CURVE`` lets the planner map task importance to these energy levels so that highly important tasks start at times with higher energy values while less critical ones are placed into lower energy periods.
Enabling ``INTELLIGENT_SLOT_SELECTION`` further refines placement by scanning
all free slots on a day and picking the time with the highest energy value so
work always happens when focus is expected to be strongest.

## Command Line Interface
Use `python cli.py add` and `python cli.py list` to manage tasks from the terminal. Configure the API URL in `config.yaml` or via `API_URL` environment variable.

## Generated API Client

The `openapi_client` package is generated from the OpenAPI schema using `openapi-python-client`. Re-generate it with:

```bash
openapi-python-client generate --url http://localhost:8000/openapi.json --output-path openapi_client
```
## Metrics
A Prometheus metrics endpoint is available at `/admin/metrics`.
The Streamlit GUI includes an "Admin Dashboard" tab displaying task, appointment and category counts.



## Docker Compose
An example `docker-compose.yml` is provided to run the API in a container.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions on building the Docker image
and running the full stack with PostgreSQL.


See [USER_GUIDE.md](USER_GUIDE.md) for usage instructions and [FAQ.md](FAQ.md) for troubleshooting.

