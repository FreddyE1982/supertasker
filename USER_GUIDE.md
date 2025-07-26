# User Guide

This guide explains how to operate the calendar and task planning application.

## Starting the API

Run `uvicorn app.main:app` to launch the REST API on `http://localhost:8000`.

## Streamlit Interface

Start the GUI with:

```bash
streamlit run streamlit_app.py
```

The application opens in your browser and allows creating appointments and tasks.

## Command Line Interface

The `cli.py` script provides a minimal CLI for managing tasks. Example:

```bash
python cli.py add "Buy milk" --due-date 2025-01-01
python cli.py list
```

The CLI reads `config.yaml` if present and honours the `API_URL` environment variable.
