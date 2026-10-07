import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[2] / ".github/scripts/prepare_property_run.py"
pytestmark = pytest.mark.unit


@pytest.mark.parametrize("seed", ["", "0", "18446744073709551615"])
def test_property_seed_is_recorded_and_replayable(tmp_path: Path, seed: str, monkeypatch: pytest.MonkeyPatch) -> None:
    metadata = tmp_path / "nested/seed.json"
    outputs = tmp_path / "outputs"
    monkeypatch.setenv("GITHUB_OUTPUT", str(outputs))
    monkeypatch.setenv("GITHUB_SHA", "a" * 40)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--seed", seed, "--output", str(metadata)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    recorded = json.loads(metadata.read_text())
    assert 0 <= recorded["seed"] < 2**64
    if seed:
        assert recorded["seed"] == int(seed)
    assert recorded["commit"] == "a" * 40
    assert recorded["minimum_examples"] == 500
    assert outputs.read_text() == f"seed={recorded['seed']}\n"


@pytest.mark.parametrize("seed", ["-1", "18446744073709551616", "１２３", "1\nseed=2", "$(touch marker)"])
def test_invalid_property_seed_fails_before_recording(tmp_path: Path, seed: str) -> None:
    metadata = tmp_path / "seed.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), f"--seed={seed}", "--output", str(metadata)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert "unsigned decimal integer" in result.stderr
    assert not metadata.exists()
