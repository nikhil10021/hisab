from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, JsonValue, ValidationError
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.calculators.base import (
    BaseCalculator,
    CalculationResult,
)

router = APIRouter(prefix="/api")
limiter = Limiter(key_func=get_remote_address)

InputKind = Literal[
    "number",
    "currency",
    "percent",
    "years",
    "select",
    "date",
    "boolean",
]


class CalculatorSummary(BaseModel):
    slug: str
    name: str
    category: str
    icon: str
    description: str


class CalculatorInputDefinition(BaseModel):
    key: str
    label: str
    type: InputKind
    default: JsonValue | None
    min: Decimal | int | float | None
    max: Decimal | int | float | None
    step: Decimal | int | float | None
    unit: str | None
    help: str | None
    options: list[dict[str, JsonValue]]


class CalculatorDetail(CalculatorSummary):
    inputs: list[CalculatorInputDefinition]
    last_updated: str | None


def calculator_summary(
    calculator: BaseCalculator[BaseModel],
) -> CalculatorSummary:
    return CalculatorSummary(
        slug=calculator.slug,
        name=calculator.name,
        category=calculator.category,
        icon=calculator.icon,
        description=calculator.description,
    )


def schema_constraint(schema: dict[str, object], constraint: str) -> object:
    value = schema.get(constraint)
    if value is not None:
        return value

    branches = schema.get("anyOf")
    if isinstance(branches, list):
        for branch in branches:
            if isinstance(branch, dict) and constraint in branch:
                return branch[constraint]

    return None


def calculator_detail(
    calculator: BaseCalculator[BaseModel],
) -> CalculatorDetail:
    input_model = calculator.InputModel
    schema = input_model.model_json_schema(mode="validation")
    properties = schema.get("properties", {})
    inputs: list[CalculatorInputDefinition] = []

    for key, field_info in input_model.model_fields.items():
        field_schema = properties.get(key, {})
        metadata = field_info.json_schema_extra or {}
        inputs.append(
            CalculatorInputDefinition(
                key=key,
                label=str(metadata.get("label", field_info.title or key)),
                type=metadata.get("type", "number"),
                default=field_schema.get("default"),
                min=schema_constraint(field_schema, "minimum"),
                max=schema_constraint(field_schema, "maximum"),
                step=metadata.get("step"),
                unit=metadata.get("unit"),
                help=metadata.get("help", field_info.description),
                options=metadata.get("options", []),
            )
        )

    return CalculatorDetail(
        **calculator_summary(calculator).model_dump(),
        inputs=inputs,
        last_updated=None,
    )


def get_calculator(
    request: Request,
    slug: str,
) -> BaseCalculator[BaseModel]:
    calculators: dict[str, BaseCalculator[BaseModel]] = (
        request.app.state.calculators
    )
    calculator = calculators.get(slug)
    if calculator is None:
        raise HTTPException(status_code=404, detail="Calculator not found.")
    return calculator


@router.get("/health")
@limiter.limit("60/minute")
def health(request: Request) -> dict[str, str]:
    rates_loaded = hasattr(request.app.state, "rates")
    return {"status": "ok" if rates_loaded else "starting"}


@router.get("/calculators", response_model=list[CalculatorSummary])
@limiter.limit("60/minute")
def list_calculators(request: Request) -> list[CalculatorSummary]:
    calculators: dict[str, BaseCalculator[BaseModel]] = (
        request.app.state.calculators
    )
    return [
        calculator_summary(calculators[slug])
        for slug in sorted(calculators)
    ]


@router.get(
    "/calculators/{slug}",
    response_model=CalculatorDetail,
)
@limiter.limit("60/minute")
def read_calculator(request: Request, slug: str) -> CalculatorDetail:
    return calculator_detail(get_calculator(request, slug))


@router.post(
    "/calculators/{slug}",
    response_model=CalculationResult,
)
@limiter.limit("60/minute")
def calculate(
    request: Request,
    slug: str,
    payload: dict[str, JsonValue],
) -> CalculationResult:
    calculator = get_calculator(request, slug)

    try:
        inputs = calculator.InputModel.model_validate(payload)
    except ValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "key": str(item["loc"][0]) if item["loc"] else "input",
                    "message": item["msg"],
                }
                for item in error.errors()
            ],
        ) from error

    return calculator.calculate(inputs)
