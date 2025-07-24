# Calendar App

This project provides a simple calendar application with a REST API and a Streamlit GUI. Users can create, update, delete, and list appointments.
It also supports managing tasks with optional subtasks. Subtasks are useful for breaking large tasks into smaller steps, which can be helpful for users with ADHD.

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
