import importlib
import inspect
import pkgutil
from collections.abc import Iterable
from typing import TypeVar, cast

from pydantic import BaseModel

from app.calculators.base import BaseCalculator

CalculatorT = TypeVar("CalculatorT", bound=BaseCalculator[BaseModel])


def build_registry(
    calculator_types: Iterable[type[CalculatorT]],
) -> dict[str, CalculatorT]:
    registry: dict[str, CalculatorT] = {}

    for calculator_type in calculator_types:
        calculator = calculator_type()
        if calculator.slug in registry:
            raise ValueError(f"Duplicate calculator slug: {calculator.slug}")
        registry[calculator.slug] = calculator

    return registry


def load_calculators() -> dict[str, BaseCalculator[BaseModel]]:
    package = importlib.import_module("app.calculators")
    calculator_types: list[type[BaseCalculator[BaseModel]]] = []

    for module_info in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{module_info.name}")
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if (
                candidate is not BaseCalculator
                and candidate.__module__ == module.__name__
                and issubclass(candidate, BaseCalculator)
                and not inspect.isabstract(candidate)
            ):
                calculator_types.append(
                    cast(type[BaseCalculator[BaseModel]], candidate)
                )

    return build_registry(calculator_types)
