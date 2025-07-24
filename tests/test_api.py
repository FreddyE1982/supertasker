import subprocess
import time
import requests
import os
import sys
from datetime import date, timedelta, datetime, time as dtime

import pytest


def wait_for_api(url: str, timeout: float = 5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(url).status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False

API_URL = 'http://localhost:8000'
TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)

@pytest.fixture(autouse=True)
def start_server():
    if os.path.exists("appointments.db"):
        os.remove("appointments.db")
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app"])
    assert wait_for_api(f"{API_URL}/appointments")
    yield
    proc.terminate()
    proc.wait()
    if os.path.exists("appointments.db"):
        os.remove("appointments.db")


def test_create_list_update_delete():
    cat = {'name': 'Work', 'color': '#ff0000'}
    r = requests.post(f'{API_URL}/categories', json=cat)
    assert r.status_code == 200
    category = r.json()

    start = datetime.combine(TOMORROW, dtime(10, 0))
    end = datetime.combine(TOMORROW, dtime(11, 0))
    data = {
        'title': 'Meeting',
        'description': 'Discuss project',
        'start_time': start.isoformat(),
        'end_time': end.isoformat(),
        'category_id': category['id']
    }
    r = requests.post(f'{API_URL}/appointments', json=data)
    assert r.status_code == 200
    appt = r.json()
    assert appt['title'] == data['title']
    assert appt['category_id'] == category['id']

    r = requests.get(f'{API_URL}/appointments')
    assert r.status_code == 200
    assert len(r.json()) == 1

    update = data.copy()
    update['title'] = 'Updated Meeting'
    update['category_id'] = category['id']
    r = requests.put(f'{API_URL}/appointments/{appt["id"]}', json=update)
    assert r.status_code == 200
    assert r.json()['title'] == 'Updated Meeting'
    assert r.json()['category_id'] == category['id']

    r = requests.delete(f'{API_URL}/appointments/{appt["id"]}')
    assert r.status_code == 200
    r = requests.get(f'{API_URL}/appointments')
    assert r.status_code == 200
    assert r.json() == []


def test_task_crud():
    data = {
        "title": "Task",
        "description": "Do something",
        "due_date": TOMORROW.isoformat(),
        "start_date": TODAY.isoformat(),
        "end_date": TODAY.isoformat(),
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "perceived_difficulty": 2,
        "estimated_difficulty": 3,
        "priority": 3,
        "worked_on": False,
        "paused": False,
    }
    r = requests.post(f"{API_URL}/tasks", json=data)
    assert r.status_code == 200
    task = r.json()
    assert task["title"] == data["title"]
    assert task["priority"] == data["priority"]

    r = requests.get(f"{API_URL}/tasks")
    assert r.status_code == 200
    assert len(r.json()) == 1

    update = data.copy()
    update["title"] = "Updated Task"
    update["priority"] = 4
    r = requests.put(f"{API_URL}/tasks/{task['id']}", json=update)
    assert r.status_code == 200
    assert r.json()["title"] == "Updated Task"
    assert r.json()["priority"] == 4

    r = requests.delete(f"{API_URL}/tasks/{task['id']}")
    assert r.status_code == 200
    r = requests.get(f"{API_URL}/tasks")
    assert r.status_code == 200
    assert r.json() == []


def test_subtask_crud():
    task_data = {
        "title": "Task",
        "description": "Do something",
        "due_date": TOMORROW.isoformat(),
        "start_date": TODAY.isoformat(),
        "end_date": TODAY.isoformat(),
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "perceived_difficulty": 2,
        "estimated_difficulty": 3,
        "priority": 3,
        "worked_on": False,
        "paused": False,
    }
    r = requests.post(f"{API_URL}/tasks", json=task_data)
    assert r.status_code == 200
    task = r.json()
    assert task["priority"] == 3

    sub_data = {"title": "Subtask 1", "completed": False}
    r = requests.post(f"{API_URL}/tasks/{task['id']}/subtasks", json=sub_data)
    assert r.status_code == 200
    sub = r.json()
    assert sub["title"] == "Subtask 1"

    r = requests.get(f"{API_URL}/tasks/{task['id']}/subtasks")
    assert r.status_code == 200
    assert len(r.json()) == 1

    update = {"title": "Updated Subtask", "completed": True}
    r = requests.put(
        f"{API_URL}/tasks/{task['id']}/subtasks/{sub['id']}", json=update
    )
    assert r.status_code == 200
    assert r.json()["completed"] is True

    r = requests.delete(f"{API_URL}/tasks/{task['id']}/subtasks/{sub['id']}")
    assert r.status_code == 200
    r = requests.get(f"{API_URL}/tasks/{task['id']}/subtasks")
    assert r.status_code == 200
    assert r.json() == []


def test_focus_session_crud():
    task_data = {
        "title": "Task",
        "description": "Do something",
        "due_date": TOMORROW.isoformat(),
        "start_date": TODAY.isoformat(),
        "end_date": TODAY.isoformat(),
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "perceived_difficulty": 2,
        "estimated_difficulty": 3,
        "priority": 3,
        "worked_on": False,
        "paused": False,
    }
    r = requests.post(f"{API_URL}/tasks", json=task_data)
    assert r.status_code == 200
    task = r.json()

    fs_data = {"duration_minutes": 25}
    r = requests.post(f"{API_URL}/tasks/{task['id']}/focus_sessions", json=fs_data)
    assert r.status_code == 200
    session = r.json()
    assert session["task_id"] == task["id"]

    r = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions")
    assert r.status_code == 200
    assert len(r.json()) == 1

    update = {"completed": True}
    r = requests.put(
        f"{API_URL}/tasks/{task['id']}/focus_sessions/{session['id']}",
        json=update,
    )
    assert r.status_code == 200
    assert r.json()["completed"] is True

    r = requests.delete(
        f"{API_URL}/tasks/{task['id']}/focus_sessions/{session['id']}"
    )
    assert r.status_code == 200
    r = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions")
    assert r.status_code == 200
    assert r.json() == []


def test_plan_task():
    start = datetime.combine(TOMORROW, dtime(9, 0))
    end = datetime.combine(TOMORROW, dtime(10, 0))
    appt = {
        "title": "Busy",
        "description": "",
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
    }
    r = requests.post(f"{API_URL}/appointments", json=appt)
    assert r.status_code == 200

    data = {
        "title": "Big Task",
        "description": "Work", 
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 50,
        "due_date": TOMORROW.isoformat(),
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    fs = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(fs) == 2
    subs = requests.get(f"{API_URL}/tasks/{task['id']}/subtasks").json()
    assert len(subs) == len(fs)
    for s in fs:
        s_start = datetime.fromisoformat(s["start_time"])
        s_end = datetime.fromisoformat(s["end_time"])
        assert not (s_start < end and s_end > start)
        assert s_end.date() <= TOMORROW
