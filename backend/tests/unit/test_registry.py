from typing import ClassVar, cast

import pytest

from app.core.registry import (
    CalculatorClass,
    build_registry,
    discover_calculators,
)
from tests.unit.dummy_calculator import DummyCalculator


def test_registry_auto_discovers_only_live_test_calculators() -> None:
    registry = discover_calculators("tests.unit")

    assert set(registry) == {"dummy-calculator"}
    assert registry["dummy-calculator"].is_live is True
    assert registry["dummy-calculator"].name == "Dummy Calculator"


def test_default_registry_does_not_expose_legacy_non_live_calculators() -> None:
    registry = discover_calculators()

    assert registry == {}


def test_registry_rejects_slugs_without_calculator_suffix() -> None:
    class InvalidSlugCalculator(DummyCalculator):
        slug: ClassVar[str] = "dummy"

    with pytest.raises(ValueError, match="end with '-calculator'"):
        build_registry([cast(CalculatorClass, InvalidSlugCalculator)])
