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


def test_cli_export_import(tmp_path, capsys):
    export_path = tmp_path / "export.yaml"
    cli = TaskCLI()
    cli.run(["export-config", "--path", str(export_path)])
    captured = capsys.readouterr()
    assert export_path.exists()
    assert "Exported" in captured.out

    updated = {"api_url": "http://example.com", "log_level": "DEBUG"}
    update_file = tmp_path / "update.yaml"
    import yaml

    with update_file.open("w", encoding="utf-8") as f:
        yaml.safe_dump(updated, f)
    os.environ["CONFIG_FILE"] = str(tmp_path / "config.yaml")
    cli.run(["import-config", str(update_file)])
    captured = capsys.readouterr()
    assert "Imported" in captured.out
    with open(os.environ["CONFIG_FILE"], "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data == {k: str(v) for k, v in updated.items()}
