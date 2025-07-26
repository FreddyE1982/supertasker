from __future__ import annotations

import argparse
import os
import sys
from typing import Any

import requests

from app.config import ConfigLoader


class BaseCLI:
    """Base command line interface."""

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description="Task CLI")
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)
        self.configure()

    def configure(self) -> None:  # pragma: no cover - to be implemented in subclass
        pass

    def run(self, args: list[str] | None = None) -> None:
        parsed = self.parser.parse_args(args=args)
        handler = getattr(self, f"do_{parsed.command}")
        handler(parsed)


class TaskCLI(BaseCLI):
    """CLI for managing tasks via the REST API."""

    def __init__(self) -> None:
        self.config = ConfigLoader().load()
        super().__init__()

    def configure(self) -> None:
        add = self.subparsers.add_parser("add", help="Create a new task")
        add.add_argument("title")
        add.add_argument("--description", default="")
        add.add_argument("--due-date", required=True)
        add.add_argument("--priority", type=int, default=3)

        self.subparsers.add_parser("list", help="List tasks")

    def _api_url(self) -> str:
        return self.config.api_url

    def do_add(self, args: Any) -> None:
        data = {
            "title": args.title,
            "description": args.description,
            "due_date": args.due_date,
            "priority": args.priority,
        }
        resp = requests.post(f"{self._api_url()}/tasks", json=data, timeout=5)
        resp.raise_for_status()
        task = resp.json()
        print(f"Created task {task['id']}")

    def do_list(self, args: Any) -> None:
        resp = requests.get(f"{self._api_url()}/tasks", timeout=5)
        resp.raise_for_status()
        for task in resp.json():
            print(f"{task['id']} {task['title']} (due {task['due_date']})")


if __name__ == "__main__":  # pragma: no cover - manual execution
    TaskCLI().run()
