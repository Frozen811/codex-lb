from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
_ROOT = Path(__file__).resolve().parents[2]


def test_client_guide_toml_blocks_parse_and_have_no_conflict_markers():
    guide = (_ROOT / "docs/client-setup.md").read_text(encoding="utf-8")
    assert not re.search(r"^(?:<{7}|={7}|>{7})(?:\s|$)", guide, re.MULTILINE)
    examples = re.findall(r"```toml\n(.*?)\n```", guide, re.DOTALL)
    assert examples
    for example in examples:
        tomllib.loads(example)


def test_shipped_codex_example_usage_and_catalog_urls_match_generation_base():
    source = (_ROOT / "docs/examples/codex/config.toml").read_text(encoding="utf-8")
    config = tomllib.loads(source)
    provider = config["model_providers"][config["model_provider"]]
    assert provider["base_url"].endswith("/backend-api/codex")
    assert provider["model_catalog_url"] == provider["base_url"] + "/models"
    usage_example = re.search(r'^# chatgpt_base_url = "([^"]+)"$', source, re.MULTILINE)
    assert usage_example is not None
    assert usage_example.group(1) == provider["base_url"].removesuffix("/codex")
