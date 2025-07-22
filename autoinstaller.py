class AutoInstaller:
    """Install missing dependencies found in Python files."""

    def __init__(self) -> None:
        from importlib.util import find_spec
        from pathlib import Path
        import os

        path_str = os.getenv("AUTOINSTALL_PATH", Path(__file__).resolve().parent)
        self.root = Path(path_str)
        self._find_spec = find_spec
        self._scan_and_install()

    def _collect_files(self) -> list["Path"]:
        from pathlib import Path

        return [p for p in self.root.rglob("*.py") if p.is_file()]

    def _parse_imports(self, file_path: "Path") -> set[str]:
        import ast

        modules: set[str] = set()
        with file_path.open("r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    modules.add(n.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and not node.level:
                    modules.add(node.module.split(".")[0])
        return modules

    def _is_installed(self, module: str) -> bool:
        return self._find_spec(module) is not None

    def _install(self, module: str) -> None:
        import subprocess
        import sys

        subprocess.run(
            [sys.executable, "-m", "pip", "install", module],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _scan_and_install(self) -> None:
        modules: set[str] = set()
        for path in self._collect_files():
            modules.update(self._parse_imports(path))
        for mod in modules:
            if not self._is_installed(mod):
                self._install(mod)


AutoInstaller()

