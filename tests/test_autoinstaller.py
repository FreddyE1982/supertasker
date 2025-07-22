import importlib
import os
import subprocess
import sys
from pathlib import Path


def test_autoinstaller_installs_packages(tmp_path, monkeypatch):
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "colorama"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    target = tmp_path / "proj"
    target.mkdir()
    (target / "sample.py").write_text("import colorama\n", encoding="utf-8")

    monkeypatch.setenv("AUTOINSTALL_PATH", str(target))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    if "autoinstaller" in sys.modules:
        importlib.reload(sys.modules["autoinstaller"])
    else:
        import autoinstaller  # noqa: F401

    assert importlib.util.find_spec("colorama") is not None

