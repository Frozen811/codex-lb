import pytest
from hypothesis import settings

from tests.property_settings import property_settings

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("profile", ["local", "ci", "thorough"])
@pytest.mark.parametrize("budget", [None, 8, 30, 100, 600])
def test_property_budgets_preserve_normal_limits_and_expand_thorough(profile: str, budget: int | None) -> None:
    previous = settings.get_current_profile_name()
    try:
        settings.load_profile(profile)

        @property_settings(max_examples=budget)
        def property_case() -> None:
            pass

        normal_budget = settings().max_examples if budget is None else budget
        expected = max(normal_budget, 500) if profile == "thorough" else normal_budget
        configured = getattr(property_case, "_hypothesis_internal_use_settings")
        assert isinstance(configured, settings)
        assert configured.max_examples == expected
        assert configured.deadline is None
        assert "extended_property" in {mark.name for mark in getattr(property_case, "pytestmark")}
    finally:
        settings.load_profile(previous)
