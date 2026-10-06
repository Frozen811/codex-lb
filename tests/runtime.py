"""Process-local test storage; never import the application before configuring it."""

from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

from sqlalchemy.engine import URL, make_url


def available_memory() -> int:
    if os.name == "nt":
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_uint32), ("load", ctypes.c_uint32)] + [
                (name, ctypes.c_uint64)
                for name in (
                    "total",
                    "available",
                    "pagefile",
                    "available_pagefile",
                    "virtual",
                    "available_virtual",
                    "extended",
                )
            ]

        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("Cannot read available memory for pytest workers")
        return status.available
    return os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")


def automatic_worker_count() -> int:
    """Respect affinity/cgroup CPU limits and reserve about 1 GiB per interpreter."""
    cpus = min(os.process_cpu_count() or 1, max(1, available_memory() // (1024**3)))
    quota = Path("/sys/fs/cgroup/cpu.max")
    if quota.is_file():
        limit, period = quota.read_text().split()
        if limit != "max":
            cpus = min(cpus, max(1, int(limit) // int(period)))
    memory_limit = Path("/sys/fs/cgroup/memory.max")
    if memory_limit.is_file():
        limit = memory_limit.read_text().strip()
        if limit != "max":
            cpus = min(cpus, max(1, int(limit) // (1024**3)))
    return max(1, cpus)


def worker_database_name(database: str, run_id: str, worker_id: str) -> str:
    """Keep names SQL-safe, below MySQL's 64-character limit, and run-specific."""
    base = re.sub(r"[^a-zA-Z0-9_]", "_", database)[:24]
    if not re.fullmatch(r"[a-f0-9]{12}", run_id) or not re.fullmatch(r"gw\d+", worker_id):
        raise ValueError("Invalid pytest run/worker identifier")
    return f"{base}_test_{run_id}_{worker_id}"


def _server_statement(admin_url: URL, statement: str) -> None:
    """Use a short-lived administrative connection, outside any async test loop."""
    if admin_url.get_backend_name() == "postgresql":
        import psycopg

        with psycopg.connect(
            admin_url.set(drivername="postgresql").render_as_string(hide_password=False), autocommit=True
        ) as connection:
            connection.execute(statement.encode("ascii"))
    else:
        import pymysql

        connection = pymysql.connect(**admin_url.translate_connect_args(username="user"), autocommit=True)
        try:
            with connection.cursor() as cursor:
                cursor.execute(statement)
        finally:
            connection.close()


@dataclass
class TestStorage:
    directory: tempfile.TemporaryDirectory[str]
    database_url: str
    owned_databases: list[tuple[URL, str]] = field(default_factory=list)

    @property
    def path(self) -> Path:
        return Path(self.directory.name)

    def close(self) -> None:
        try:
            for admin_url, name in self.owned_databases:
                if admin_url.get_backend_name() == "postgresql":
                    # FORCE also cleans up a database after a worker crashes.
                    statement = f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'
                else:
                    statement = f"DROP DATABASE IF EXISTS `{name}`"
                _server_statement(admin_url, statement)
            self.owned_databases.clear()
        finally:
            self.directory.cleanup()

    def prepare_worker(self, worker_id: str) -> None:
        """The controller owns provisioning/cleanup, including crashed workers."""
        url = make_url(self.database_url)
        if url.get_backend_name() == "sqlite":
            return
        name = worker_database_name(url.database or "codex_lb", os.environ["CODEX_LB_TEST_RUN_ID"], worker_id)
        quote = '"' if url.get_backend_name() == "postgresql" else "`"
        _server_statement(url, f"CREATE DATABASE {quote}{name}{quote}")
        self.owned_databases.append((url, name))


def create_test_storage() -> TestStorage:
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
    # The controller sets this before xdist launches fresh interpreters. Random
    # run IDs also isolate two pytest invocations on the same database server.
    run_id = os.environ.setdefault("CODEX_LB_TEST_RUN_ID", uuid4().hex[:12])
    ram_directory = Path("/dev/shm")
    parent = str(ram_directory) if ram_directory.is_dir() and os.access(ram_directory, os.W_OK) else None
    directory = tempfile.TemporaryDirectory(prefix=f"codex-lb-{worker_id}-", dir=parent)
    default_url = f"sqlite+aiosqlite:///{(Path(directory.name) / 'test.db').as_posix()}"
    configured = os.environ.get("CODEX_LB_TEST_DATABASE_URL")
    storage = TestStorage(directory, default_url)
    if configured:
        url = make_url(configured)
        backend = url.get_backend_name()
        if backend not in {"sqlite", "postgresql", "mysql"}:
            raise ValueError("Test database must use SQLite, PostgreSQL, or MySQL")
        if backend == "sqlite":
            # Even an explicitly configured file must not be shared by workers.
            storage.database_url = configured if worker_id == "master" else default_url
        elif worker_id == "master":
            storage.database_url = configured
        else:
            name = worker_database_name(url.database or "codex_lb", run_id, worker_id)
            # pytest_configure_node provisions this before starting the worker.
            # Only the controller drops databases, even when a worker crashes.
            storage.database_url = url.set(database=name).render_as_string(hide_password=False)
    os.environ["CODEX_LB_DATABASE_URL"] = storage.database_url
    # Spawned CLI subprocesses inherit the already resolved worker database.
    if configured:
        os.environ["CODEX_LB_TEST_DATABASE_URL"] = storage.database_url
    return storage
