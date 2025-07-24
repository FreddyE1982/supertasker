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
def start_server(monkeypatch, request):
    if os.path.exists("appointments.db"):
        os.remove("appointments.db")
    env = os.environ.copy()
    marker = request.node.get_closest_marker("env")
    if marker:
        env.update(marker.kwargs)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app"], env=env
    )
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
        "priority": 3,
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


def test_plan_task_interlaced():
    # block current day to force scheduling tomorrow
    start_block = datetime.combine(TODAY, dtime(0, 0))
    end_block = datetime.combine(TODAY, dtime(23, 59))
    block = {
        "title": "Block",
        "description": "all day",
        "start_time": start_block.isoformat(),
        "end_time": end_block.isoformat(),
    }
    r = requests.post(f"{API_URL}/appointments", json=block)
    assert r.status_code == 200

    # create events and task on the target day
    appt1 = {
        "title": "Morning",
        "description": "",
        "start_time": datetime.combine(TOMORROW, dtime(9, 0)).isoformat(),
        "end_time": datetime.combine(TOMORROW, dtime(9, 30)).isoformat(),
    }
    appt2 = {
        "title": "Standup",
        "description": "",
        "start_time": datetime.combine(TOMORROW, dtime(10, 0)).isoformat(),
        "end_time": datetime.combine(TOMORROW, dtime(11, 0)).isoformat(),
    }
    r = requests.post(f"{API_URL}/appointments", json=appt1)
    assert r.status_code == 200
    r = requests.post(f"{API_URL}/appointments", json=appt2)
    assert r.status_code == 200

    task_data = {
        "title": "Existing",
        "description": "",
        "due_date": TOMORROW.isoformat(),
        "start_date": TOMORROW.isoformat(),
        "end_date": TOMORROW.isoformat(),
        "start_time": "11:30:00",
        "end_time": "12:30:00",
        "perceived_difficulty": 1,
        "estimated_difficulty": 1,
        "priority": 3,
        "worked_on": False,
        "paused": False,
    }
    r = requests.post(f"{API_URL}/tasks", json=task_data)
    assert r.status_code == 200

    plan = {
        "title": "New Big Task",
        "description": "Work",
        "estimated_difficulty": 2,
        "estimated_duration_minutes": 100,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=plan)
    assert r.status_code == 200
    task = r.json()
    fs = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(fs) == 4
    sessions = [(datetime.fromisoformat(s["start_time"]), datetime.fromisoformat(s["end_time"])) for s in fs]
    appointments = [
        (
            datetime.combine(TOMORROW, dtime(9, 0)),
            datetime.combine(TOMORROW, dtime(9, 30)),
        ),
        (
            datetime.combine(TOMORROW, dtime(10, 0)),
            datetime.combine(TOMORROW, dtime(11, 0)),
        ),
        (
            datetime.combine(TOMORROW, dtime(11, 30)),
            datetime.combine(TOMORROW, dtime(12, 30)),
        ),
    ]
    for s_start, s_end in sessions:
        assert s_end - s_start == timedelta(minutes=25)
        for a_start, a_end in appointments:
            assert not (s_start < a_end and s_end > a_start)
    for i in range(1, len(sessions)):
        assert sessions[i][0] - sessions[i - 1][1] >= timedelta(minutes=5)
    assert sessions[-1][1].date() <= TOMORROW


def test_planner_respects_work_hours(monkeypatch):
    monkeypatch.setenv("WORK_START_HOUR", "8")
    monkeypatch.setenv("WORK_END_HOUR", "16")

    data = {
        "title": "Early Task",
        "description": "",
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 50,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    fs = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert all(
        8 <= datetime.fromisoformat(s["start_time"]).hour < 16 for s in fs
    )
    assert all(
        8 < datetime.fromisoformat(s["end_time"]).hour <= 16
        or (
            datetime.fromisoformat(s["end_time"]).hour == 16
            and datetime.fromisoformat(s["end_time"]).minute == 0
        )
        for s in fs
    )


def test_planner_considers_difficulty(monkeypatch):
    monkeypatch.setenv("WORK_START_HOUR", "9")
    monkeypatch.setenv("WORK_END_HOUR", "17")

    hard = {
        "title": "Hard",
        "description": "",
        "estimated_difficulty": 5,
        "estimated_duration_minutes": 25,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
    }
    easy = {
        "title": "Easy",
        "description": "",
        "estimated_difficulty": 1,
        "estimated_duration_minutes": 25,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=hard)
    assert r.status_code == 200
    hard_task = r.json()
    r = requests.post(f"{API_URL}/tasks/plan", json=easy)
    assert r.status_code == 200
    easy_task = r.json()
    hard_start = datetime.fromisoformat(
        requests.get(
            f"{API_URL}/tasks/{hard_task['id']}/focus_sessions"
        ).json()[0]["start_time"]
    ).hour
    easy_start = datetime.fromisoformat(
        requests.get(
            f"{API_URL}/tasks/{easy_task['id']}/focus_sessions"
        ).json()[0]["start_time"]
    ).hour
    assert hard_start <= easy_start


def test_planner_considers_priority(monkeypatch):
    monkeypatch.setenv("WORK_START_HOUR", "9")
    monkeypatch.setenv("WORK_END_HOUR", "17")

    high = {
        "title": "High",
        "description": "",
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 25,
        "due_date": TOMORROW.isoformat(),
        "priority": 5,
    }
    low = {
        "title": "Low",
        "description": "",
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 25,
        "due_date": TOMORROW.isoformat(),
        "priority": 1,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=high)
    assert r.status_code == 200
    high_task = r.json()
    r = requests.post(f"{API_URL}/tasks/plan", json=low)
    assert r.status_code == 200
    low_task = r.json()
    high_start = datetime.fromisoformat(
        requests.get(
            f"{API_URL}/tasks/{high_task['id']}/focus_sessions"
        ).json()[0]["start_time"]
    ).hour
    low_start = datetime.fromisoformat(
        requests.get(
            f"{API_URL}/tasks/{low_task['id']}/focus_sessions"
        ).json()[0]["start_time"]
    ).hour
    assert high_start <= low_start


def test_planner_spreads_sessions(monkeypatch):
    due = TODAY + timedelta(days=3)
    plan = {
        "title": "Spread",
        "description": "",
        "estimated_difficulty": 2,
        "estimated_duration_minutes": 100,
        "due_date": due.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=plan)
    assert r.status_code == 200
    task = r.json()
    sessions = requests.get(
        f"{API_URL}/tasks/{task['id']}/focus_sessions"
    ).json()
    days = {datetime.fromisoformat(s["start_time"]).date() for s in sessions}
    assert len(days) >= 2
    assert max(days) <= due


@pytest.mark.env(SESSION_LENGTH_MINUTES="50")
def test_custom_session_length(monkeypatch):

    data = {
        "title": "Long",
        "description": "",
        "estimated_difficulty": 2,
        "estimated_duration_minutes": 50,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    sessions = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(sessions) == 1
    delta = datetime.fromisoformat(sessions[0]["end_time"]) - datetime.fromisoformat(sessions[0]["start_time"])
    assert delta == timedelta(minutes=50)


@pytest.mark.env(WORK_DAYS="0,1,2,3,4")
def test_planner_respects_work_days(monkeypatch):
    weekend = TODAY + timedelta((5 - TODAY.weekday()) % 7)

    data = {
        "title": "Weekend",
        "description": "",
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 25,
        "due_date": weekend.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    sessions = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert all(datetime.fromisoformat(s["start_time"]).weekday() < 5 for s in sessions)
    assert datetime.fromisoformat(sessions[-1]["end_time"]).date() <= weekend


@pytest.mark.env(LUNCH_START_HOUR="12", LUNCH_DURATION_MINUTES="60")
def test_planner_avoids_lunch_break(monkeypatch):
    data = {
        "title": "LunchTest",
        "description": "",
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 200,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    sessions = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    lunch_start = datetime.combine(TODAY, dtime(12, 0))
    lunch_end = lunch_start + timedelta(minutes=60)
    for s in sessions:
        s_start = datetime.fromisoformat(s["start_time"])
        s_end = datetime.fromisoformat(s["end_time"])
        assert not (s_start < lunch_end and s_end > lunch_start)

