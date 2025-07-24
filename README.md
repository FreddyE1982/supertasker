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
`estimated_duration_minutes` and `due_date`.
The service splits the work into 25-minute focus sessions with
Pomodoro-style breaks and ensures no overlap with existing calendar entries.
Each focus session also creates a corresponding subtask so large tasks are
automatically broken into manageable parts.
