import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cli import TaskCLI

API_URL = "http://localhost:8000"
TODAY = date.today().isoformat()


def wait_for_api(url: str, timeout: float = 5.0):
    import time
    import requests

    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(url).status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False


@pytest.fixture
def server():
    if Path("appointments.db").exists():
        Path("appointments.db").unlink()
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app"])
    assert wait_for_api(f"{API_URL}/appointments")
    yield
    proc.terminate()
    proc.wait()
    if Path("appointments.db").exists():
        Path("appointments.db").unlink()


def test_cli_add_and_list(server, capsys):
    cli = TaskCLI()
    cli.run(["add", "Test", "--due-date", TODAY])
    captured = capsys.readouterr()
    assert "Created task" in captured.out

    cli.run(["list"])
    captured = capsys.readouterr()
    assert "Test" in captured.out
