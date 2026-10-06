from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture
def sharder(tmp_path, monkeypatch):
    path = Path(__file__).parents[2] / ".github/scripts/pytest_shards.py"
    spec = importlib.util.spec_from_file_location("pytest_shards", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    return module


def test_shards_balance_recorded_time_and_partition_every_file(sharder, tmp_path):
    files = [Path(f"test_{index}.py") for index in range(7)]
    durations = dict(zip((file.as_posix() for file in files), [40, 30, 20, 10, 5, 3, 2], strict=True))
    selections = [sharder.shard_files(files, shard, 3, durations) for shard in range(1, 4)]
    assert sorted(file for selected in selections for file in selected) == files
    loads = [sum(durations[file.as_posix()] for file in selected) for selected in selections]
    assert max(loads) - min(loads) <= 5
    assert selections == [sharder.shard_files(list(reversed(files)), shard, 3, durations) for shard in range(1, 4)]


def test_new_files_account_for_parametrization_database_setup_and_waits(sharder, tmp_path):
    fast = Path("fast.py")
    heavy = Path("heavy.py")
    (tmp_path / fast).write_text("def test_fast(): pass\n")
    (tmp_path / heavy).write_text(
        "@pytest.mark.parametrize('case', [1, 2, 3])\n"
        "async def test_heavy(case, async_client):\n    await asyncio.sleep(2)\n"
    )
    assert sharder.file_weight(heavy) > sharder.file_weight(fast) * 5


@pytest.mark.parametrize("value", [-1, 0, float("nan"), True, "slow"])
def test_invalid_duration_history_fails_instead_of_changing_assignment(sharder, tmp_path, value):
    history = tmp_path / "durations.json"
    history.write_text(json.dumps({"tests/integration/test_a.py": value}))
    with pytest.raises(ValueError):
        sharder.load_durations(history)


def test_history_import_includes_test_class_durations_and_preserves_other_files(sharder, tmp_path):
    test = tmp_path / "tests/integration/test_a.py"
    test.parent.mkdir(parents=True)
    test.write_text("")
    report = tmp_path / "report.xml"
    report.write_text(
        '<testsuite><testcase classname="tests.integration.test_a.TestCases" time="2"/>'
        '<testcase classname="tests.integration.test_a" time="3"/>'
        '<testcase classname="tests.integration.test_a" time="50"><skipped/></testcase></testsuite>'
    )
    history = tmp_path / "history.json"
    history.write_text('{"tests/integration/test_other.py": 8}')
    sharder.update_durations([report], history)
    assert sharder.load_durations(history) == {"tests/integration/test_a.py": 5, "tests/integration/test_other.py": 8}
