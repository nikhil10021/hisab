import importlib
import inspect
import pkgutil
import re
from collections.abc import Iterable
from typing import cast

from app.core.base import BaseCalculator, CalculatorInput

CalculatorClass = type[BaseCalculator[CalculatorInput]]
Calculator = BaseCalculator[CalculatorInput]
CALCULATOR_SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*-calculator")


def build_registry(
    calculator_types: Iterable[CalculatorClass],
) -> dict[str, Calculator]:
    registry: dict[str, Calculator] = {}
    seen_slugs: set[str] = set()

    for calculator_type in calculator_types:
        slug = calculator_type.slug
        if CALCULATOR_SLUG_PATTERN.fullmatch(slug) is None:
            raise ValueError(
                f"Calculator slug must be lowercase kebab-case and end "
                f"with '-calculator': {slug}"
            )
        if slug in seen_slugs:
            raise ValueError(f"Duplicate calculator slug: {slug}")
        seen_slugs.add(slug)

        if calculator_type.is_live:
            registry[slug] = calculator_type()

    return registry


def discover_calculators(
    package_name: str = "app.calculators",
) -> dict[str, Calculator]:
    package = importlib.import_module(package_name)
    package_path = getattr(package, "__path__", None)
    if package_path is None:
        raise ValueError(f"Calculator package has no module path: {package_name}")

    calculator_types: list[CalculatorClass] = []
    module_prefix = f"{package_name}."
    for module_info in pkgutil.walk_packages(
        package_path,
        prefix=module_prefix,
    ):
        module_name = module_info.name.rsplit(".", maxsplit=1)[-1]
        if module_name.startswith("_"):
            continue
        module = importlib.import_module(module_info.name)
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if (
                candidate is not BaseCalculator
                and candidate.__module__ == module.__name__
                and issubclass(candidate, BaseCalculator)
                and not inspect.isabstract(candidate)
            ):
                calculator_types.append(cast(CalculatorClass, candidate))

    calculators = build_registry(calculator_types)
    return calculators
