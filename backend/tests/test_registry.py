from collections.abc import Iterable
from typing import ClassVar

import pytest
from pydantic import BaseModel

from app.calculators.base import (
    BaseCalculator,
    CalculationResult,
    CalculatorInput,
    SummaryItem,
)
from app.registry.loader import build_registry, load_calculators


def test_registry_discovers_calculator_modules() -> None:
    registry = load_calculators()

    assert set(registry) == {"sip", "lumpsum"}
    assert registry["sip"].InputModel.__name__ == "SipInputs"


class FirstDuplicateCalculator(BaseCalculator[CalculatorInput]):
    slug: ClassVar[str] = "duplicate"
    name: ClassVar[str] = "First"
    category: ClassVar[str] = "Test"
    icon: ClassVar[str] = "test"
    description: ClassVar[str] = "First duplicate test calculator."
    InputModel: ClassVar[type[CalculatorInput]] = CalculatorInput

    @classmethod
    def calculate(cls, inputs: CalculatorInput) -> CalculationResult:
        return CalculationResult(
            summary=[
                SummaryItem(
                    key="input",
                    label="Input",
                    value=str(inputs.model_dump()),
                    format="text",
                )
            ],
            charts=[],
        )


class SecondDuplicateCalculator(FirstDuplicateCalculator):
    name: ClassVar[str] = "Second"


def test_registry_rejects_duplicate_slugs() -> None:
    calculator_types: Iterable[type[BaseCalculator[BaseModel]]] = [
        FirstDuplicateCalculator,
        SecondDuplicateCalculator,
    ]

    with pytest.raises(ValueError, match="Duplicate calculator slug: duplicate"):
        build_registry(calculator_types)
