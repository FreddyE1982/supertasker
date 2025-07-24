import subprocess
import time
import requests
import os
import sys

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

@pytest.fixture(autouse=True)
def start_server():
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

    data = {
        'title': 'Meeting',
        'description': 'Discuss project',
        'start_time': '2024-01-01T10:00:00',
        'end_time': '2024-01-01T11:00:00',
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
        "due_date": "2024-01-05",
        "start_date": "2024-01-04",
        "end_date": "2024-01-04",
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "perceived_difficulty": 2,
        "estimated_difficulty": 3,
        "worked_on": False,
        "paused": False,
    }
    r = requests.post(f"{API_URL}/tasks", json=data)
    assert r.status_code == 200
    task = r.json()
    assert task["title"] == data["title"]

    r = requests.get(f"{API_URL}/tasks")
    assert r.status_code == 200
    assert len(r.json()) == 1

    update = data.copy()
    update["title"] = "Updated Task"
    r = requests.put(f"{API_URL}/tasks/{task['id']}", json=update)
    assert r.status_code == 200
    assert r.json()["title"] == "Updated Task"

    r = requests.delete(f"{API_URL}/tasks/{task['id']}")
    assert r.status_code == 200
    r = requests.get(f"{API_URL}/tasks")
    assert r.status_code == 200
    assert r.json() == []


def test_subtask_crud():
    task_data = {
        "title": "Task",
        "description": "Do something",
        "due_date": "2024-01-05",
        "start_date": "2024-01-04",
        "end_date": "2024-01-04",
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "perceived_difficulty": 2,
        "estimated_difficulty": 3,
        "worked_on": False,
        "paused": False,
    }
    r = requests.post(f"{API_URL}/tasks", json=task_data)
    assert r.status_code == 200
    task = r.json()

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
