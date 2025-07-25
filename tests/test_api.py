import subprocess
import time
import requests
import os
import sys
import math
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


def test_planner_importance_affects_start_day(monkeypatch):
    future = TODAY + timedelta(days=5)
    high = {
        "title": "HighImp",
        "description": "",
        "estimated_difficulty": 5,
        "estimated_duration_minutes": 25,
        "due_date": future.isoformat(),
        "priority": 5,
    }
    low = {
        "title": "LowImp",
        "description": "",
        "estimated_difficulty": 1,
        "estimated_duration_minutes": 25,
        "due_date": future.isoformat(),
        "priority": 1,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=high)
    assert r.status_code == 200
    high_task = r.json()
    r = requests.post(f"{API_URL}/tasks/plan", json=low)
    assert r.status_code == 200
    low_task = r.json()
    high_day = datetime.fromisoformat(
        requests.get(f"{API_URL}/tasks/{high_task['id']}/focus_sessions").json()[0]["start_time"]
    ).date()
    low_day = datetime.fromisoformat(
        requests.get(f"{API_URL}/tasks/{low_task['id']}/focus_sessions").json()[0]["start_time"]
    ).date()
    assert high_day <= low_day


@pytest.mark.env(LOW_ENERGY_START_HOUR="14", LOW_ENERGY_END_HOUR="16")
def test_planner_avoids_low_energy(monkeypatch):
    data = {
        "title": "Slump",
        "description": "",
        "estimated_difficulty": 5,
        "estimated_duration_minutes": 50,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    sessions = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    for s in sessions:
        start = datetime.fromisoformat(s["start_time"])
        assert not (14 <= start.hour < 16)


@pytest.mark.env(HIGH_ENERGY_START_HOUR="8", HIGH_ENERGY_END_HOUR="11")
def test_planner_prefers_high_energy(monkeypatch):
    data = {
        "title": "Energy",
        "description": "",
        "estimated_difficulty": 5,
        "estimated_duration_minutes": 25,
        "due_date": TOMORROW.isoformat(),
        "priority": 4,
        "high_energy_start_hour": 8,
        "high_energy_end_hour": 11,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    sessions = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    for s in sessions:
        start = datetime.fromisoformat(s["start_time"])
        assert 8 <= start.hour < 11


@pytest.mark.env(DAILY_SESSION_LIMIT="1")
def test_planner_daily_session_limit(monkeypatch):
    due = TODAY + timedelta(days=2)
    data = {
        "title": "Limited",
        "description": "",
        "estimated_difficulty": 2,
        "estimated_duration_minutes": 50,
        "due_date": due.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    sessions = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(sessions) == 2
    days = [datetime.fromisoformat(s["start_time"]).date() for s in sessions]
    assert len(set(days)) == 2


@pytest.mark.env(
    INTELLIGENT_SESSION_LENGTH="1",
    MIN_SESSION_LENGTH_MINUTES="20",
    MAX_SESSION_LENGTH_MINUTES="60",
)
def test_dynamic_session_length(monkeypatch):
    data = {
        "title": "Scaled",
        "description": "",
        "estimated_difficulty": 5,
        "estimated_duration_minutes": 50,
        "due_date": TOMORROW.isoformat(),
        "priority": 5,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    sessions = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    urgency = 4
    weight = (5 + 5 + urgency) / 3
    expected_len = round(25 * (1 + (weight - 3) / 4))
    assert len(sessions) == math.ceil(50 / expected_len)
    for s in sessions:
        start = datetime.fromisoformat(s["start_time"])
        end = datetime.fromisoformat(s["end_time"])
        assert (end - start) == timedelta(minutes=expected_len)


@pytest.mark.env(
    INTELLIGENT_BREAKS="1",
    SHORT_BREAK_MINUTES="5",
    LONG_BREAK_MINUTES="15",
    MIN_SHORT_BREAK_MINUTES="5",
    MAX_SHORT_BREAK_MINUTES="10",
    MIN_LONG_BREAK_MINUTES="15",
    MAX_LONG_BREAK_MINUTES="20",
)
def test_dynamic_break_length(monkeypatch):
    data = {
        "title": "BreakTest",
        "description": "",
        "estimated_difficulty": 5,
        "estimated_duration_minutes": 60,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    sessions = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(sessions) == 3
    first_end = datetime.fromisoformat(sessions[0]["end_time"])
    second_start = datetime.fromisoformat(sessions[1]["start_time"])
    assert (second_start - first_end) == timedelta(minutes=8)


@pytest.mark.env(INTELLIGENT_DAY_ORDER="1")
def test_intelligent_day_order(monkeypatch):
    busy_start = datetime.combine(TOMORROW, dtime(9, 0))
    busy_end = datetime.combine(TOMORROW, dtime(16, 0))
    appt = {
        "title": "Busy Day",
        "description": "",
        "start_time": busy_start.isoformat(),
        "end_time": busy_end.isoformat(),
    }
    r = requests.post(f"{API_URL}/appointments", json=appt)
    assert r.status_code == 200

    plan = {
        "title": "Smart",
        "description": "",
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 25,
        "due_date": (TOMORROW + timedelta(days=1)).isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=plan)
    assert r.status_code == 200
    task = r.json()
    fs = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(fs) == 1
    start_day = datetime.fromisoformat(fs[0]["start_time"]).date()
    assert start_day == TOMORROW + timedelta(days=1)


@pytest.mark.env(INTELLIGENT_DAY_ORDER="1", ENERGY_DAY_ORDER_WEIGHT="2")
def test_energy_weighted_day_order(monkeypatch):
    curve = [1] * 24
    curve[9] = 10
    monkeypatch.setenv("ENERGY_CURVE", ",".join(str(x) for x in curve))
    busy_start = datetime.combine(TOMORROW, dtime(9, 0))
    busy_end = datetime.combine(TOMORROW, dtime(10, 0))
    appt = {
        "title": "Block",
        "description": "",
        "start_time": busy_start.isoformat(),
        "end_time": busy_end.isoformat(),
    }
    r = requests.post(f"{API_URL}/appointments", json=appt)
    assert r.status_code == 200

    plan = {
        "title": "EnergyPlan",
        "description": "",
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 25,
        "due_date": (TOMORROW + timedelta(days=1)).isoformat(),
        "priority": 3,
        "energy_curve": curve,
        "energy_day_order_weight": 2,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=plan)
    assert r.status_code == 200
    task = r.json()
    fs = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(fs) == 1
    start_day = datetime.fromisoformat(fs[0]["start_time"]).date()
    assert start_day == TOMORROW + timedelta(days=1)


@pytest.mark.env()
def test_energy_curve(monkeypatch):
    curve = ",".join("0" if i != 15 else "10" for i in range(24))
    monkeypatch.setenv("ENERGY_CURVE", curve)
    data = {
        "title": "Curve",
        "description": "",
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 25,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
        "energy_curve": [0 if i != 15 else 10 for i in range(24)],
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    fs = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(fs) == 1
    start = datetime.fromisoformat(fs[0]["start_time"])
    assert start.hour == 15


curve_imp = [1] * 24
curve_imp[9] = 10
curve_imp[17] = 2

@pytest.mark.env(
    WORK_START_HOUR="8",
    WORK_END_HOUR="18",
    ENERGY_CURVE=",".join(str(x) for x in curve_imp),
)
def test_energy_curve_importance():

    high = {
        "title": "HighImpCurve",
        "description": "",
        "estimated_difficulty": 5,
        "estimated_duration_minutes": 25,
        "due_date": TOMORROW.isoformat(),
        "priority": 5,
    }
    low = {
        "title": "LowImpCurve",
        "description": "",
        "estimated_difficulty": 1,
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

    high_hour = datetime.fromisoformat(
        requests.get(
            f"{API_URL}/tasks/{high_task['id']}/focus_sessions"
        ).json()[0]["start_time"]
    ).hour
    low_hour = datetime.fromisoformat(
        requests.get(
            f"{API_URL}/tasks/{low_task['id']}/focus_sessions"
        ).json()[0]["start_time"]
    ).hour

    assert high_hour == 9
    assert low_hour == 17
    assert high_hour < low_hour


@pytest.mark.env(
    FATIGUE_BREAK_FACTOR="1",
    SHORT_BREAK_MINUTES="5",
    LONG_BREAK_MINUTES="15",
    SESSIONS_BEFORE_LONG_BREAK="4",
    LUNCH_START_HOUR="0",
    LUNCH_DURATION_MINUTES="0",
)
def test_fatigue_break_factor(monkeypatch):
    data = {
        "title": "Fatigue",
        "description": "",
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 75,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
        "fatigue_break_factor": 1,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    fs = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(fs) == 3
    b1 = datetime.fromisoformat(fs[1]["start_time"]) - datetime.fromisoformat(fs[0]["end_time"])
    b2 = datetime.fromisoformat(fs[2]["start_time"]) - datetime.fromisoformat(fs[1]["end_time"])
    assert b1 == timedelta(minutes=5)
    assert b2 == timedelta(minutes=10)


@pytest.mark.env(
    WORK_START_HOUR="9",
    WORK_END_HOUR="19",
    INTELLIGENT_SLOT_SELECTION="1",
    ENERGY_CURVE=",".join(
        ["1"] * 15 + ["10", "2", "8"] + ["1"] * 6
    ),
)
def test_intelligent_slot_selection(monkeypatch):
    busy = {
        "title": "Busy",
        "description": "",
        "start_time": datetime.combine(TOMORROW, dtime(17, 0)).isoformat(),
        "end_time": datetime.combine(TOMORROW, dtime(18, 0)).isoformat(),
    }
    r = requests.post(f"{API_URL}/appointments", json=busy)
    assert r.status_code == 200

    data = {
        "title": "SmartSlot",
        "description": "",
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 25,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
        "energy_curve": [1] * 15 + [10, 2, 8] + [1] * 6,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    fs = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(fs) == 1
    start_hour = datetime.fromisoformat(fs[0]["start_time"]).hour
    assert start_hour == 15


@pytest.mark.env(DEEP_WORK_THRESHOLD="4", WORK_START_HOUR="9", WORK_END_HOUR="12")
def test_deep_work_mode(monkeypatch):
    data = {
        "title": "DeepWork",
        "description": "",
        "estimated_difficulty": 5,
        "estimated_duration_minutes": 75,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    sessions = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(sessions) == 3
    dates = {datetime.fromisoformat(s["start_time"]).date() for s in sessions}
    assert len(dates) == 1
    for i in range(1, len(sessions)):
        prev_end = datetime.fromisoformat(sessions[i - 1]["end_time"])
        start = datetime.fromisoformat(sessions[i]["start_time"])
        assert start - prev_end == timedelta(minutes=5)


@pytest.mark.env(DAILY_DIFFICULTY_LIMIT="5")
def test_daily_difficulty_limit(monkeypatch):
    due = TODAY + timedelta(days=1)
    first = {
        "title": "Hard1",
        "description": "",
        "estimated_difficulty": 5,
        "estimated_duration_minutes": 25,
        "due_date": due.isoformat(),
        "priority": 3,
    }
    second = {
        "title": "Hard2",
        "description": "",
        "estimated_difficulty": 5,
        "estimated_duration_minutes": 25,
        "due_date": (due + timedelta(days=1)).isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=first)
    assert r.status_code == 200
    t1 = r.json()
    day1 = datetime.fromisoformat(
        requests.get(f"{API_URL}/tasks/{t1['id']}/focus_sessions").json()[0]["start_time"]
    ).date()
    r = requests.post(f"{API_URL}/tasks/plan", json=second)
    assert r.status_code == 200
    t2 = r.json()
    day2 = datetime.fromisoformat(
        requests.get(f"{API_URL}/tasks/{t2['id']}/focus_sessions").json()[0]["start_time"]
    ).date()
    assert day1 != day2


@pytest.mark.env(TRANSITION_BUFFER_MINUTES="15")
def test_transition_buffer(monkeypatch):
    block = {
        "title": "Block",
        "description": "",
        "start_time": datetime.combine(TODAY, dtime(0, 0)).isoformat(),
        "end_time": datetime.combine(TODAY, dtime(23, 59)).isoformat(),
    }
    requests.post(f"{API_URL}/appointments", json=block)
    busy = {
        "title": "Busy",
        "description": "",
        "start_time": datetime.combine(TOMORROW, dtime(9, 0)).isoformat(),
        "end_time": datetime.combine(TOMORROW, dtime(10, 0)).isoformat(),
    }
    r = requests.post(f"{API_URL}/appointments", json=busy)
    assert r.status_code == 200

    data = {
        "title": "BufferTask",
        "description": "",
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 25,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    fs = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(fs) == 1
    start = datetime.fromisoformat(fs[0]["start_time"])
    assert start >= datetime.combine(TOMORROW, dtime(10, 0)) + timedelta(minutes=15)


@pytest.mark.env(TRANSITION_BUFFER_MINUTES="10", INTELLIGENT_TRANSITION_BUFFER="1")
def test_intelligent_buffer(monkeypatch):
    block = {
        "title": "BlockToday",
        "description": "",
        "start_time": datetime.combine(TODAY, dtime(0, 0)).isoformat(),
        "end_time": datetime.combine(TODAY, dtime(23, 59)).isoformat(),
    }
    requests.post(f"{API_URL}/appointments", json=block)
    busy = {
        "title": "Block",
        "description": "",
        "start_time": datetime.combine(TOMORROW, dtime(9, 0)).isoformat(),
        "end_time": datetime.combine(TOMORROW, dtime(10, 0)).isoformat(),
    }
    r = requests.post(f"{API_URL}/appointments", json=busy)
    assert r.status_code == 200

    data = {
        "title": "SmartBuffer",
        "description": "",
        "estimated_difficulty": 5,
        "estimated_duration_minutes": 25,
        "due_date": TOMORROW.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    fs = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(fs) == 1
    start = datetime.fromisoformat(fs[0]["start_time"])
    expected = datetime.combine(TOMORROW, dtime(10, 0)) + timedelta(minutes=20)
    assert start >= expected


@pytest.mark.env(
    INTELLIGENT_DAY_ORDER="1",
    ENERGY_DAY_ORDER_WEIGHT="2",
    WEEKDAY_ENERGY="1,1,1,1,1,10,1",
)
def test_weekday_energy_preference(monkeypatch):
    curve = ",".join("1" for _ in range(24))
    monkeypatch.setenv("ENERGY_CURVE", curve)
    saturday = TODAY + timedelta((5 - TODAY.weekday()) % 7)
    data = {
        "title": "WeekendEnergy",
        "description": "",
        "estimated_difficulty": 3,
        "estimated_duration_minutes": 25,
        "due_date": saturday.isoformat(),
        "priority": 3,
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=data)
    assert r.status_code == 200
    task = r.json()
    fs = requests.get(f"{API_URL}/tasks/{task['id']}/focus_sessions").json()
    assert len(fs) == 1
    start_day = datetime.fromisoformat(fs[0]["start_time"]).date()
    assert start_day == saturday


def test_category_context_grouping(monkeypatch):
    cat = {"name": "Code", "color": "#0000ff"}
    r = requests.post(f"{API_URL}/categories", json=cat)
    assert r.status_code == 200
    category = r.json()

    first = {
        "title": "First", 
        "description": "", 
        "estimated_difficulty": 3, 
        "estimated_duration_minutes": 25, 
        "due_date": TOMORROW.isoformat(), 
        "priority": 3, 
        "category_id": category["id"],
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=first)
    assert r.status_code == 200
    t1 = r.json()
    fs1 = requests.get(f"{API_URL}/tasks/{t1['id']}/focus_sessions").json()[0]
    end1 = datetime.fromisoformat(fs1["end_time"])

    second = {
        "title": "Second", 
        "description": "", 
        "estimated_difficulty": 2, 
        "estimated_duration_minutes": 25, 
        "due_date": TOMORROW.isoformat(), 
        "priority": 2, 
        "category_id": category["id"],
    }
    r = requests.post(f"{API_URL}/tasks/plan", json=second)
    assert r.status_code == 200
    t2 = r.json()
    fs2 = requests.get(f"{API_URL}/tasks/{t2['id']}/focus_sessions").json()[0]
    start2 = datetime.fromisoformat(fs2["start_time"])
    assert start2 >= end1
    assert start2 - end1 <= timedelta(minutes=60)

