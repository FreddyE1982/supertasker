import os
import subprocess
import sys
import time
from datetime import date, timedelta

import pytest
import requests

from pathlib import Path

API_URL = "http://localhost:8000"


def wait_for_api(url: str, timeout: float = 5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(url).status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False


@pytest.fixture(autouse=True)
def start_server(request):
    if os.path.exists("appointments.db"):
        os.remove("appointments.db")
    env = os.environ.copy()
    marker = request.node.get_closest_marker("env")
    if marker:
        env.update(marker.kwargs)
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app"], env=env)
    assert wait_for_api(f"{API_URL}/appointments")
    yield
    proc.terminate()
    proc.wait()
    if os.path.exists("appointments.db"):
        os.remove("appointments.db")


def wait_for_log(path: Path, timeout: float = 5.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if path.exists() and path.stat().st_size > 0:
            return True
        time.sleep(0.1)
    return False

TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)


@pytest.mark.env(ENABLE_QUERY_PROFILING="1", QUERY_LOG="test_query.log")
def test_query_log_created():
    log_path = Path("test_query.log")
    if log_path.exists():
        log_path.unlink()
    r = requests.get(f"{API_URL}/appointments")
    assert r.status_code == 200
    assert wait_for_api(f"{API_URL}/appointments")
    assert wait_for_log(log_path)
    with log_path.open("r", encoding="utf-8") as f:
        content = f.read()
    assert "SELECT" in content
