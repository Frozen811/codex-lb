"""Keep explicit PR budgets while expanding selected nightly properties."""

from collections.abc import Callable
from typing import Any, TypeVar

import pytest
from hypothesis import settings

F = TypeVar("F", bound=Callable[..., Any])


def property_settings(*, max_examples: int | None = None) -> Callable[[F], F]:
    defaults = settings()
    budget = defaults.max_examples if max_examples is None else max_examples
    if settings.get_current_profile_name() == "thorough":
        budget = max(budget, defaults.max_examples)

    def decorate(test: F) -> F:
        return pytest.mark.extended_property(settings(max_examples=budget, deadline=None)(test))

    return decorate
