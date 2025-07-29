import logging
import os
import time

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./appointments.db")

connect_args = (
    {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class QueryProfiler:
    """Log SQL query execution times to a file when enabled."""

    def __init__(self, engine, path: str | None = None) -> None:
        self.engine = engine
        self.path = path or os.getenv("QUERY_LOG", "query.log")
        self.enabled = os.getenv("ENABLE_QUERY_PROFILING", "0") in {"1", "true", "True"}
        self.logger = logging.getLogger("sql.profiler")

    def install(self) -> None:
        if not self.enabled:
            return
        event.listen(self.engine, "before_cursor_execute", self._before)
        event.listen(self.engine, "after_cursor_execute", self._after)

    def _before(self, conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = time.perf_counter()

    def _after(self, conn, cursor, statement, parameters, context, executemany):
        duration = (time.perf_counter() - context._query_start_time) * 1000
        msg = f"{duration:.2f} ms: {statement}"
        self.logger.info(msg)
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except OSError:
            self.logger.warning("Failed to write query log")


QueryProfiler(engine).install()
