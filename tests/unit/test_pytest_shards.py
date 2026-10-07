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


def write_mysql_manifest(root: Path, selectors: list[str]) -> None:
    manifest = root / ".github/pytest-mysql-targets.txt"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("\n".join(selectors) + "\n")


@pytest.fixture
def mysql_selection(tmp_path):
    files = [Path(f"tests/integration/test_{index}.py") for index in range(5)]
    files += [Path("tests/test_options.py"), Path("tests/unit/test_contract.py")]
    for path in files:
        source = tmp_path / path
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("def test_first(client): pass\ndef test_second(client): pass\n")
    selectors = [path.as_posix() for path in files]
    selectors[1:2] = [f"{files[1]}::test_first", f"{files[1]}::test_second"]
    write_mysql_manifest(tmp_path, selectors)
    return files, selectors


def test_mysql_shards_balance_history_and_preserve_exact_partial_selection(sharder, mysql_selection):
    files, selectors = mysql_selection
    groups = sharder.mysql_file_groups()
    durations = dict(zip((path.as_posix() for path in files), [40, 30, 20, 10, 5, 3, 2], strict=True))
    shards = [sharder.mysql_shard(groups, index, 3, durations) for index in range(1, 4)]
    assert sorted(node for shard in shards for node in shard) == sorted(selectors)
    assert all(shard for shard in shards)
    assert all(sum(any(node.split("::")[0] == str(path) for node in shard) for shard in shards) == 1 for path in files)
    assert str(files[1]) not in [node for shard in shards for node in shard]
    loads = [sum(durations[path] for path in {node.split("::")[0] for node in shard}) for shard in shards]
    assert max(loads) - min(loads) <= 5
    sharder.verify_mysql(groups, 3, durations)


def test_mysql_partial_estimates_exclude_unselected_migration_tests(sharder, tmp_path):
    path = Path("tests/integration/test_migration.py")
    (tmp_path / path).parent.mkdir(parents=True)
    (tmp_path / path).write_text(
        "def test_mysql(client): pass\n"
        "@pytest.mark.parametrize('case', [1, 2, 3])\n"
        "async def test_other_database(client, case):\n    await asyncio.sleep(50)\n"
    )
    selected = [f"{path}::test_mysql"]
    assert sharder.mysql_group_weight(path, selected) < sharder.mysql_group_weight(path, [str(path)]) / 10
    assert sharder.mysql_group_weight(path, selected, {str(path): 42}) == 42


@pytest.mark.parametrize(
    "selectors",
    [
        [],
        ["tests/test_a.py", "tests/test_a.py"],
        ["tests/test_a.py", "tests/test_a.py::test_first"],
        ["tests/test_a.py::test_first", "tests/test_a.py::test_first[one]"],
        ["tests/test_a.py::test_missing"],
        ["tests/test_missing.py"],
        ["../test_outside.py"],
        ["/tmp/test_outside.py"],
        ["--last-failed"],
    ],
)
def test_mysql_manifest_rejects_duplicates_overlaps_and_invalid_selectors(sharder, tmp_path, selectors):
    test = tmp_path / "tests/test_a.py"
    test.parent.mkdir(parents=True)
    test.write_text("def test_first(): pass\n")
    write_mysql_manifest(tmp_path, selectors)
    with pytest.raises(ValueError):
        sharder.mysql_file_groups()


def test_mysql_verify_rejects_empty_shards_and_missing_or_duplicate_nodes(sharder, mysql_selection, monkeypatch):
    files, selectors = mysql_selection
    groups = sharder.mysql_file_groups()
    with pytest.raises(SystemExit, match="empty"):
        sharder.verify_mysql({files[0]: groups[files[0]]}, 3)
    monkeypatch.setattr(sharder, "mysql_shard", lambda *args: [selectors[0]])
    with pytest.raises(SystemExit, match="assigned more than once"):
        sharder.verify_mysql(groups, 3)
    monkeypatch.setattr(sharder, "mysql_shard", lambda groups, shard, *args: [selectors[shard - 1]])
    with pytest.raises(SystemExit, match="file split across runners|missing"):
        sharder.verify_mysql(groups, 3)


@pytest.mark.parametrize("argument", ["--shard", "--shard-index"])
def test_mysql_cli_supports_both_index_spellings_and_three_shard_default(
    sharder, mysql_selection, monkeypatch, capsys, argument
):
    expected = sharder.mysql_shard(sharder.mysql_file_groups(), 1, 3)
    monkeypatch.setattr(sharder.sys, "argv", ["pytest_shards.py", "--suite", "mysql", argument, "1"])
    sharder.main()
    assert capsys.readouterr().out.splitlines() == expected


def test_mysql_junit_history_includes_selected_root_and_unit_files(sharder, mysql_selection, tmp_path):
    report = tmp_path / "mysql.xml"
    report.write_text(
        '<testsuite><testcase classname="tests.test_options" name="test_first" time="2"/>'
        '<testcase classname="tests.unit.test_contract" name="test_first" time="3"/>'
        '<testcase classname="tests.integration.test_0" name="test_first" time="4"/>'
        '<testcase classname="tests.test_options" name="test_second" time="50"><skipped/></testcase>'
        '<testcase classname="tests.integration.test_unselected" name="test_first" time="20"/></testsuite>'
    )
    history = tmp_path / "mysql-history.json"
    sharder.update_durations([report], history, suite="mysql")
    assert sharder.load_durations(history) == {
        "tests/test_options.py": 2,
        "tests/unit/test_contract.py": 3,
        "tests/integration/test_0.py": 4,
    }


def test_real_mysql_manifest_partitions_every_selector_and_file_once(sharder, monkeypatch):
    monkeypatch.setattr(sharder, "REPO_ROOT", Path(__file__).parents[2])
    groups = sharder.mysql_file_groups()
    sharder.verify_mysql(groups, 3)
    selected = [node for index in range(1, 4) for node in sharder.mysql_shard(groups, index, 3)]
    manifest = (sharder.REPO_ROOT / sharder.MYSQL_MANIFEST).read_text().split()
    assert sorted(selected) == sorted(manifest)
    assert len(selected) == len(set(selected))
    assert any(node.startswith("tests/unit/") for node in selected)
    assert any(node.startswith("tests/test_request_logs_options_api.py") for node in selected)
