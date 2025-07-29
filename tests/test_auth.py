import os
import subprocess
import sys
import time

import pytest
import requests

API_URL = "http://localhost:8000"


def wait_for_api(url: str, timeout: float = 5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(url).status_code < 500:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False


@pytest.fixture
def server():
    if os.path.exists("appointments.db"):
        os.remove("appointments.db")
    env = os.environ.copy()
    env["DISABLE_AUTH"] = "0"
    env["RATE_LIMIT"] = "1000"
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app"], env=env)
    assert wait_for_api(f"{API_URL}/openapi.json")
    yield
    proc.terminate()
    proc.wait()
    if os.path.exists("appointments.db"):
        os.remove("appointments.db")


def test_register_login(server):
    data = {"username": "alice", "email": "a@example.com", "password": "secret"}
    r = requests.post(f"{API_URL}/users", json=data)
    assert r.status_code == 200

    r = requests.post(
        f"{API_URL}/token", data={"username": "alice", "password": "secret"}
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_URL}/appointments", headers=headers)
    assert r.status_code == 200
    assert r.json() == []
